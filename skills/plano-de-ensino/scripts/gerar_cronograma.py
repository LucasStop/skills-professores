#!/usr/bin/env python3
"""Calcula o cronograma de um plano de ensino: distribui os encontros de aula
entre os RAs conforme o peso de cada um, busca feriados nacionais na BrasilAPI
e reserva a carga horária de TDE dentro do RA correspondente.

Só biblioteca padrão do Python — sem pip install, sem chamada de rede além da
BrasilAPI (com fallback se não houver internet).

Uso:
    python3 gerar_cronograma.py dados.json > cronograma.json

Cada linha de saída traz: indice (nº sequencial da sessão, None pra TDE sem
data fixa — mesmo padrão de linha administrativa sem número dos planos
reais), data (DD/MM ou DD/MM/AAAA conforme "formato_data"), data_iso (uso
interno), ra, descricao, carga_horaria (número, uso interno) e
carga_horaria_fmt ("HH:MM", formato dos planos reais). O documento final usa
indice/data/ra/descricao/carga_horaria_fmt — "#" é a primeira coluna da
tabela de cronograma no template oficial.

Formato de dados.json:
{
  "data_inicio": "2026-08-05",
  "data_fim": "2026-12-05",
  "dias_semana": {"terca": 4},                # ou {"terca": 2, "quinta": 2}
  "recessos_manuais": ["2026-11-02"],          # pontos facultativos institucionais
  "formato_data": "dd_mm",                     # ou "dd_mm_aaaa" — opcional, default "dd_mm"
  "feriados_como_linha": false,                 # opcional — true: feriado nacional ("Feriado") e
                                                 # recesso manual ("Recesso Acadêmico") viram linha
                                                 # visível no cronograma (RA "-", carga horária do
                                                 # dia, não consome a meta de nenhum RA)
  "ras": [
    {"nome": "RA1", "percentual": 30, "temas": ["Tema A", "Tema B"],
     "tde": [{"horas": 4, "quantidade": 1}]},
    {"nome": "RA2", "percentual": 70, "temas": ["Tema C"], "tde": []}
  ]
}
"""
import json
import sys
import unicodedata
import urllib.error
import urllib.request
from datetime import date, timedelta

DIAS_SEMANA_PT = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]


def formata_carga_horaria(horas):
    """4 -> '04:00' — formato usado nos planos de ensino reais (HH:MM)."""
    h = int(horas)
    m = round((horas - h) * 60)
    return f"{h:02d}:{m:02d}"


def normaliza_dia(nome):
    """'Terça', 'terça-feira', 'TERCA' -> 'terca'."""
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", nome) if not unicodedata.combining(c)
    )
    sem_acento = sem_acento.lower().strip()
    for dia in DIAS_SEMANA_PT:
        if sem_acento.startswith(dia):
            return dia
    raise ValueError(f"dia da semana não reconhecido: {nome!r}")


def parse_data(s):
    return date.fromisoformat(s)


def busca_feriados_nacionais(anos):
    """GET BrasilAPI (stdlib urllib, sem chave). Retorna set de 'YYYY-MM-DD' ou
    None se não conseguir buscar (sem internet, API fora do ar, etc) — quem
    chama decide o fallback (pedir a lista manual ao professor)."""
    feriados = set()
    for ano in sorted(anos):
        url = f"https://brasilapi.com.br/api/feriados/v1/{ano}"
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                dados = json.loads(resp.read().decode("utf-8"))
            feriados.update(item["date"] for item in dados)
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError, OSError):
            return None
    return feriados


def gera_encontros(data_inicio, data_fim, dias_semana, feriados_nacionais, recessos_manuais, feriados_como_linha=False):
    """dias_semana: dict {dia_normalizado: horas}. feriados_nacionais/recessos_manuais:
    sets de 'YYYY-MM-DD'. Com feriados_como_linha=True, datas de feriado/recesso que
    caem em dia de aula continuam no resultado, marcadas com "feriado"/"recesso": True
    — quem chama decide como renderizar (linha visível "Feriado"/"Recesso Acadêmico",
    sem consumir meta de RA)."""
    encontros = []
    d = data_inicio
    while d <= data_fim:
        dia_idx = d.weekday()  # segunda=0 ... domingo=6
        dia_nome = DIAS_SEMANA_PT[dia_idx]
        if dia_nome in dias_semana:
            iso = d.isoformat()
            if iso not in feriados_nacionais and iso not in recessos_manuais:
                encontros.append({"data": d, "horas": dias_semana[dia_nome]})
            elif feriados_como_linha:
                tag = "feriado" if iso in feriados_nacionais else "recesso"
                encontros.append({"data": d, "horas": dias_semana[dia_nome], tag: True})
        d += timedelta(days=1)
    return encontros


def gera_cronograma(data_inicio, data_fim, dias_semana, feriados_nacionais, recessos_manuais, ras,
                     formato_data="dd_mm", feriados_como_linha=False):
    """Retorna (linhas, avisos). linhas = [{data, ra, descricao, carga_horaria}]."""
    avisos = []
    fmt_strftime = "%d/%m/%Y" if formato_data == "dd_mm_aaaa" else "%d/%m"
    feriados_nacionais = set(feriados_nacionais)
    recessos_manuais = set(recessos_manuais)
    encontros = gera_encontros(data_inicio, data_fim, dias_semana, feriados_nacionais, recessos_manuais, feriados_como_linha)
    if not encontros:
        raise ValueError("nenhum encontro gerado — confira o range de datas e os dias da semana")

    carga_total = sum(e["horas"] for e in encontros if not e.get("feriado") and not e.get("recesso"))
    soma_pct = sum(ra["percentual"] for ra in ras)
    if abs(soma_pct - 100) > 0.01:
        avisos.append(f"percentuais dos RAs somam {soma_pct}%, não 100%")

    for ra in ras:
        ra["_meta_total"] = carga_total * ra["percentual"] / 100
        ra["_tde_horas"] = sum(t["horas"] * t["quantidade"] for t in ra.get("tde", []))
        ra["_meta_aula"] = max(0.0, ra["_meta_total"] - ra["_tde_horas"])
        if ra["_tde_horas"] > ra["_meta_total"]:
            avisos.append(f"{ra['nome']}: carga de TDE ({ra['_tde_horas']}h) excede a carga total do RA ({ra['_meta_total']}h)")
        ra["_temas_restantes"] = list(ra.get("temas", []))
        ra["_horas_aula_acumuladas"] = 0.0

    linhas = []
    indice = 1
    ra_idx = 0
    for encontro in encontros:
        if encontro.get("feriado") or encontro.get("recesso"):
            linhas.append({
                "indice": indice,
                "data": encontro["data"].strftime(fmt_strftime),
                "data_iso": encontro["data"].isoformat(),
                "ra": "-",
                "descricao": "Feriado" if encontro.get("feriado") else "Recesso Acadêmico",
                "carga_horaria": encontro["horas"],
                "carga_horaria_fmt": formata_carga_horaria(encontro["horas"]),
            })
            indice += 1
            continue
        while (
            ra_idx < len(ras) - 1
            and ras[ra_idx]["_horas_aula_acumuladas"] >= ras[ra_idx]["_meta_aula"]
        ):
            ra_idx += 1
        ra = ras[ra_idx]
        if ra["_temas_restantes"]:
            descricao = ra["_temas_restantes"].pop(0)
        else:
            descricao = "[definir conteúdo]"
            avisos.append(f"{ra['nome']}: acabaram os temas antes das aulas (encontro de {encontro['data'].isoformat()} sem tema)")
        linhas.append({
            "indice": indice,  # numeração sequencial da linha, como nos planos reais (coluna "#")
            "data": encontro["data"].strftime(fmt_strftime),  # DD/MM (padrão) ou DD/MM/AAAA
            "data_iso": encontro["data"].isoformat(),
            "ra": ra["nome"],
            "descricao": descricao,
            "carga_horaria": encontro["horas"],
            "carga_horaria_fmt": formata_carga_horaria(encontro["horas"]),
        })
        indice += 1
        ra["_horas_aula_acumuladas"] += encontro["horas"]

        # RA trocou de bloco (ou é o último encontro do RA atual) -> insere TDEs pendentes
        proximo_ra_vai_comecar = ra_idx < len(ras) - 1 and ra["_horas_aula_acumuladas"] >= ra["_meta_aula"]
        ultimo_encontro_geral = encontro is encontros[-1]
        if (proximo_ra_vai_comecar or ultimo_encontro_geral) and not ra.get("_tde_inserido"):
            for tde in ra.get("tde", []):
                for _ in range(tde["quantidade"]):
                    linhas.append({
                        "indice": None,  # sem data fixa -> sem número de sessão, como as linhas administrativas dos planos reais
                        "data": "[professor define a data]",
                        "data_iso": None,
                        "ra": ra["nome"],
                        "descricao": "TDE",
                        "carga_horaria": tde["horas"],
                        "carga_horaria_fmt": formata_carga_horaria(tde["horas"]),
                    })
            ra["_tde_inserido"] = True

    return linhas, avisos


def carrega_dados(caminho):
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    dados["data_inicio"] = parse_data(dados["data_inicio"])
    dados["data_fim"] = parse_data(dados["data_fim"])
    dados["dias_semana"] = {normaliza_dia(k): v for k, v in dados["dias_semana"].items()}
    dados.setdefault("recessos_manuais", [])
    dados.setdefault("formato_data", "dd_mm")
    dados.setdefault("feriados_como_linha", False)
    for ra in dados["ras"]:
        ra.setdefault("tde", [])
        ra.setdefault("temas", [])
    return dados


def main():
    if len(sys.argv) != 2:
        print("uso: python3 gerar_cronograma.py dados.json", file=sys.stderr)
        sys.exit(1)

    dados = carrega_dados(sys.argv[1])
    anos = {dados["data_inicio"].year, dados["data_fim"].year}
    feriados = busca_feriados_nacionais(anos)
    aviso_feriados = None
    if feriados is None:
        aviso_feriados = "não consegui buscar feriados nacionais na BrasilAPI (sem internet ou API fora do ar) — confirme com o professor se há feriados no período e passe em recessos_manuais"
        feriados = set()

    linhas, avisos = gera_cronograma(
        dados["data_inicio"], dados["data_fim"], dados["dias_semana"],
        feriados, dados["recessos_manuais"], dados["ras"],
        formato_data=dados["formato_data"], feriados_como_linha=dados["feriados_como_linha"],
    )
    if aviso_feriados:
        avisos.insert(0, aviso_feriados)

    print(json.dumps({"cronograma": linhas, "avisos": avisos}, ensure_ascii=False, indent=2))


def demo():
    """Auto-checagem: roda um caso conhecido e valida as invariantes do
    algoritmo. python3 gerar_cronograma.py --demo"""
    ras = [
        {"nome": "RA1", "percentual": 40, "temas": ["Introdução", "Fundamentos", "Prática 1"], "tde": [{"horas": 4, "quantidade": 1}]},
        {"nome": "RA2", "percentual": 60, "temas": ["Avançado 1", "Avançado 2", "Projeto", "Revisão"], "tde": []},
    ]
    linhas, avisos = gera_cronograma(
        data_inicio=date(2026, 8, 4),
        data_fim=date(2026, 10, 27),
        dias_semana={"terca": 4},
        feriados_nacionais=set(),
        recessos_manuais=["2026-09-08"],
        ras=ras,
    )

    datas_iso = [l["data_iso"] for l in linhas if l["data_iso"] is not None]
    datas_br = [l["data"] for l in linhas if l["data_iso"] is not None]
    assert datas_iso == sorted(datas_iso), "datas fora de ordem"
    assert "2026-09-08" not in datas_iso, "recesso manual não foi excluído"
    for d in datas_iso:
        assert date.fromisoformat(d).weekday() == 1, f"encontro fora do dia da semana pedido: {d}"
        assert date(2026, 8, 4) <= date.fromisoformat(d) <= date(2026, 10, 27), f"data fora do range: {d}"
    for d_iso, d_br in zip(datas_iso, datas_br):
        assert d_br == date.fromisoformat(d_iso).strftime("%d/%m"), f"data BR não bate com data_iso: {d_br} vs {d_iso}"
        assert "/" in d_br and len(d_br) == 5, f"data não está no formato DD/MM: {d_br!r}"

    for ra_nome, ra_pct in [("RA1", 40), ("RA2", 60)]:
        horas_ra = sum(l["carga_horaria"] for l in linhas if l["ra"] == ra_nome)
        carga_total = sum(4 for _ in datas_iso)  # 4h por encontro nesse cenário fixo
        meta = carga_total * ra_pct / 100
        assert abs(horas_ra - meta) <= 4, f"{ra_nome}: horas geradas ({horas_ra}) longe da meta ({meta})"

    tde_linhas = [l for l in linhas if l["descricao"] == "TDE"]
    assert len(tde_linhas) == 1 and tde_linhas[0]["ra"] == "RA1" and tde_linhas[0]["data"] == "[professor define a data]"
    assert tde_linhas[0]["indice"] is None, "TDE sem data fixa deveria ficar sem número de sessão"
    assert tde_linhas[0]["carga_horaria_fmt"] == "04:00", f"formato HH:MM incorreto: {tde_linhas[0]['carga_horaria_fmt']!r}"

    indices = [l["indice"] for l in linhas if l["indice"] is not None]
    assert indices == list(range(1, len(indices) + 1)), f"índices não são sequenciais 1..N: {indices}"

    # feriados_como_linha=True: feriado nacional numa terça vira linha "Feriado"
    # visível, sem tirar horas da meta de nenhum RA.
    linhas_fer, avisos_fer = gera_cronograma(
        data_inicio=date(2026, 8, 4),
        data_fim=date(2026, 8, 18),
        dias_semana={"terca": 4},
        feriados_nacionais={"2026-08-11"},
        recessos_manuais=[],
        ras=[{"nome": "RA1", "percentual": 100, "temas": ["A", "B"], "tde": []}],
        feriados_como_linha=True,
        formato_data="dd_mm_aaaa",
    )
    feriado_linhas = [l for l in linhas_fer if l["descricao"] == "Feriado"]
    assert len(feriado_linhas) == 1, f"esperava 1 linha de feriado, veio {len(feriado_linhas)}"
    assert feriado_linhas[0]["ra"] == "-" and feriado_linhas[0]["indice"] is not None
    assert feriado_linhas[0]["data"] == "11/08/2026", f"formato_data com ano não aplicado: {feriado_linhas[0]['data']!r}"
    horas_ra1_fer = sum(l["carga_horaria"] for l in linhas_fer if l["ra"] == "RA1")
    assert horas_ra1_fer == 8, f"feriado não deveria contar na meta do RA: {horas_ra1_fer}h"
    datas_normais = [l for l in linhas_fer if l["ra"] == "RA1"]
    assert all("/" in l["data"] and len(l["data"]) == 10 for l in datas_normais), "formato_data dd_mm_aaaa não aplicado às linhas normais"

    print(f"demo ok — {len(linhas)} linhas geradas, {len(avisos)} avisos: {avisos} | feriado-linha: {len(linhas_fer)} linhas, {len(avisos_fer)} avisos")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--demo":
        demo()
    else:
        main()

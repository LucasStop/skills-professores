#!/usr/bin/env python3
"""Preenche um .docx-template (institucional, com identidade visual da
PUCPR) a partir de placeholders — só biblioteca padrão (zipfile + re).
Alternativa a gerar_docx.py quando existe um .docx oficial editável em vez
de gerar o documento do zero.

Faz a troca por manipulação de string no XML bruto, NUNCA reserializando a
árvore inteira via xml.etree — um .docx real do Word declara ~15 namespaces
extras (mc, w14, wp14, ...) e o atributo `mc:Ignorable="w14 w15 ..."`
referencia esses prefixos pelo NOME. ElementTree.tostring() renomeia
prefixos não-registrados pra ns0/ns1/... e não atualiza essa lista —
Word acusa "conteúdo ilegível" ao abrir. Trocar só as strings que
interessam, preservando o resto do arquivo byte a byte, evita o problema.

Contrato do template:
- Placeholders escalares: `{{TOKEN}}` — precisa estar inteiro num único
  <w:t> (um template limpo por `limpar_template.py`, ou gerado por
  gerar_docx.py, já garante isso).
- Linha de tabela repetível (ex: cronograma): UMA linha <w:tr> no template
  contendo os placeholders da linha, marcada por um placeholder-âncora
  único (ex: {{CRONO_INDICE}}) que não aparece em nenhuma outra tabela.
  Clonada uma vez por item de `linhas_repetir[ancora]`.
- Seção opcional (ex: Regras da Disciplina): par de parágrafos adjacentes
  `{{SECAO_OPCIONAL_N_TITULO}}` (clona o estilo real de heading do
  documento — mesmo pStyle, ver `limpar_template_oficial.py`) e
  `{{SECAO_OPCIONAL_N_CORPO}}`, N = 1, 2, 3... Se `secoes_opcionais[N-1]`
  existir em dados.json, preenche os dois; se não (lista mais curta que o
  número de slots no template), remove o par de parágrafos inteiro — não
  deixa placeholder nem heading vazio no documento final.
  O corpo aceita duas formas: `"corpo"` (string) preenche o parágrafo
  único como está no template; `"topicos"` (lista de string) clona esse
  MESMO parágrafo uma vez por item — mesmo mecanismo de linha repetível
  de tabela, só que aplicado a `<w:p>` em vez de `<w:tr>` — pra render
  cada tópico (Diagnóstica/Formativa/Somativa/...) na própria linha, em
  vez de tudo corrido num parágrafo só.
- Mapa Mental: se `valores["MAPA_MENTAL"]` vier vazio/ausente, o heading
  "Mapa Mental (opcional...)" some junto (o próprio template pede pra
  remover o item inteiro quando não usado).
- Tabela condicional (seção 3, Certificadora x Internalizadora/Mobilizadora
  — mutuamente exclusivas): se a disciplina não é Certificadora, **não**
  inclua `CERT_RA`/`CERT_TEMAS` em `valores` (nem uma entrada em
  `linhas_repetir`) — a tabela inteira (heading + linha-molde) some sozinha.
  Mesma lógica inversa pra `IM_RA`/`linhas_repetir["IM_RA"]` se a disciplina
  for só Certificadora. Disciplina mista usa as duas normalmente.

Uso:
    python3 preencher_template.py template.docx dados.json saida.docx

dados.json:
{
  "valores": {"DISCIPLINA": "Testes de Software", "PROFESSOR": "Marina de Lara"},
  "linhas_repetir": {
    "CRONO_INDICE": [
      {"CRONO_INDICE": "1", "CRONO_DATA": "04/08/2026", "CRONO_RA": "RA1", "CRONO_DESC": "Introdução", "CRONO_CH": "04:00"}
    ]
  },
  "secoes_opcionais": [
    {"titulo": "REGRAS DA DISCIPLINA", "topicos": ["Diagnóstica: ...", "Formativa: ..."]},
    {"titulo": "OUTRA SEÇÃO", "corpo": "Texto corrido único."}
  ]
}
"""
import json
import re
import sys
import zipfile

TR_RE = re.compile(r"<w:tr(?:\s[^>]*)?>.*?</w:tr>", re.DOTALL)
P_RE = re.compile(r"<w:p(?:\s[^>]*)?>.*?</w:p>", re.DOTALL)
TBL_RE = re.compile(r"<w:tbl(?:\s[^>]*)?>.*?</w:tbl>", re.DOTALL)
T_RE = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.DOTALL)


def _escapa(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _texto_p(bloco):
    return "".join(T_RE.findall(bloco))


def _acha_bloco_tr(xml, ancora_token):
    marcador = "{{" + ancora_token + "}}"
    for m in TR_RE.finditer(xml):
        if marcador in m.group(0):
            return m.start(), m.end(), m.group(0)
    return None


def _acha_bloco_p(xml, ancora_token):
    marcador = "{{" + ancora_token + "}}"
    for m in P_RE.finditer(xml):
        if marcador in m.group(0):
            return m.start(), m.end(), m.group(0)
    return None


def _remove_secoes_opcionais_nao_usadas(xml):
    """Depois do preenchimento normal, qualquer par de placeholders
    {{SECAO_OPCIONAL_N_TITULO}}/{{SECAO_OPCIONAL_N_CORPO}} que sobrou (o
    professor não pediu essa seção) tem os 2 parágrafos removidos por
    inteiro — sem isso sobraria um heading vazio no documento."""
    indices = set(re.findall(r"\{\{SECAO_OPCIONAL_(\d+)_TITULO\}\}", xml))
    for indice in indices:
        titulo_tok = "{{SECAO_OPCIONAL_" + indice + "_TITULO}}"
        corpo_tok = "{{SECAO_OPCIONAL_" + indice + "_CORPO}}"
        heading_m = corpo_m = None
        for p in P_RE.finditer(xml):
            if titulo_tok in p.group(0):
                heading_m = p
            elif heading_m is not None and corpo_tok in p.group(0):
                corpo_m = p
                break
        if heading_m and corpo_m:
            xml = xml[: heading_m.start()] + xml[corpo_m.end() :]
    return xml


def _remove_mapa_mental_se_vazio(xml, valores):
    """O heading 'Mapa Mental (opcional...)' é texto fixo do template, não
    um placeholder — só some se `valores["MAPA_MENTAL"]` vier vazio/ausente
    (chama ANTES da substituição normal, senão {{MAPA_MENTAL}} já virou
    string vazia e não dá pra achar o parágrafo pelo token)."""
    if valores.get("MAPA_MENTAL"):
        return xml
    heading_texto = "Mapa Mental (opcional - se não utilizar, retirar este item)"
    heading_m = corpo_m = None
    for p in P_RE.finditer(xml):
        if heading_m is None:
            if _texto_p(p.group(0)).strip() == heading_texto:
                heading_m = p
        elif "{{MAPA_MENTAL}}" in p.group(0):
            corpo_m = p
            break
    if heading_m and corpo_m:
        xml = xml[: heading_m.start()] + xml[corpo_m.end() :]
    return xml


def _remove_tabela_condicional(xml, ancora_token, heading_texto):
    """Seção 3 tem 2 tabelas mutuamente exclusivas (Certificadora /
    Internalizadora-Mobilizadora). Se o professor não deu dado pra uma delas
    (o placeholder-âncora sobrevive ao preenchimento normal — não apareceu
    em `valores` nem `linhas_repetir`), remove o heading dela + a tabela
    inteira."""
    marcador = "{{" + ancora_token + "}}"
    if marcador not in xml:
        return xml
    tbl_m = next((m for m in TBL_RE.finditer(xml) if marcador in m.group(0)), None)
    if tbl_m is None:
        return xml
    heading_m = None
    for p in P_RE.finditer(xml[: tbl_m.start()]):
        if _texto_p(p.group(0)).strip() == heading_texto:
            heading_m = p
    inicio = heading_m.start() if heading_m else tbl_m.start()
    return xml[:inicio] + xml[tbl_m.end() :]


def preenche(template_path, dados, saida_path):
    valores = dict(dados.get("valores", {}))
    linhas_repetir = dict(dados.get("linhas_repetir", {}))
    for i, secao in enumerate(dados.get("secoes_opcionais", []), start=1):
        valores[f"SECAO_OPCIONAL_{i}_TITULO"] = secao["titulo"]
        if "topicos" in secao:
            token = f"SECAO_OPCIONAL_{i}_CORPO"
            linhas_repetir[token] = [{token: topico} for topico in secao["topicos"]]
        else:
            valores[f"SECAO_OPCIONAL_{i}_CORPO"] = secao["corpo"]

    with zipfile.ZipFile(template_path) as z_in:
        xml = z_in.read("word/document.xml").decode("utf-8")
        outros = {n: z_in.read(n) for n in z_in.namelist() if n != "word/document.xml"}

    xml = _remove_mapa_mental_se_vazio(xml, valores)

    for ancora_token, linhas in linhas_repetir.items():
        achado = _acha_bloco_tr(xml, ancora_token) or _acha_bloco_p(xml, ancora_token)
        if achado is None:
            continue
        inicio, fim, molde = achado
        clones = []
        for linha_valores in linhas:
            clone = molde
            for token, valor in linha_valores.items():
                clone = clone.replace("{{" + token + "}}", _escapa(str(valor)))
            clones.append(clone)
        xml = xml[:inicio] + "".join(clones) + xml[fim:]

    for token, valor in valores.items():
        xml = xml.replace("{{" + token + "}}", _escapa(str(valor)))

    xml = _remove_secoes_opcionais_nao_usadas(xml)
    xml = _remove_tabela_condicional(xml, "CERT_RA", "Disciplinas Certificadoras")
    xml = _remove_tabela_condicional(xml, "IM_RA", "Disciplinas Internalizadoras e Mobilizadoras")

    restantes = set(re.findall(r"\{\{(\w+)\}\}", xml))
    if restantes:
        print(f"aviso: placeholders não preenchidos: {sorted(restantes)}", file=sys.stderr)

    with zipfile.ZipFile(saida_path, "w", zipfile.ZIP_DEFLATED) as z_out:
        for nome, conteudo in outros.items():
            z_out.writestr(nome, conteudo)
        z_out.writestr("word/document.xml", xml.encode("utf-8"))


def main():
    if len(sys.argv) != 4:
        print("uso: python3 preencher_template.py template.docx dados.json saida.docx", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[2], encoding="utf-8") as f:
        dados = json.load(f)
    preenche(sys.argv[1], dados, sys.argv[3])
    print(f"gerado {sys.argv[3]}")


def demo():
    """Auto-checagem: monta um template com placeholder escalar + linha
    repetível de tabela, preenche e valida o resultado — inclusive que a
    troca preserva um mc:Ignorable com prefixo não-registrado intacto
    (simula o cenário real que corrompia via ElementTree.tostring).
    python3 preencher_template.py --demo"""
    import os
    import tempfile

    sys.path.insert(0, os.path.dirname(__file__))
    from gerar_docx import gera_docx

    blocos_template = [
        {"tipo": "titulo1", "texto": "{{DISCIPLINA}}"},
        {"tipo": "paragrafo", "texto": "{{PROFESSOR}}"},
        {"tipo": "titulo2", "texto": "Disciplinas Internalizadoras e Mobilizadoras"},
        {"tipo": "tabela", "cabecalho": ["Competência", "RA"],
         "linhas": [["{{IM_COMPETENCIA}}", "{{IM_RA}}"]]},
        {"tipo": "titulo2", "texto": "Disciplinas Certificadoras"},
        {"tipo": "tabela", "cabecalho": ["RA", "Temas"],
         "linhas": [["{{CERT_RA}}", "{{CERT_TEMAS}}"]]},
        {"tipo": "titulo2", "texto": "Mapa Mental (opcional - se não utilizar, retirar este item)"},
        {"tipo": "paragrafo", "texto": "{{MAPA_MENTAL}}"},
        {"tipo": "titulo2", "texto": "Cronograma"},
        {"tipo": "tabela", "cabecalho": ["Data", "RA", "Descrição"],
         "linhas": [["{{CRONO_DATA}}", "{{CRONO_RA}}", "{{CRONO_INDICE}} {{CRONO_DESC}}"]]},
        {"tipo": "titulo2", "texto": "{{SECAO_OPCIONAL_1_TITULO}}"},
        {"tipo": "paragrafo", "texto": "{{SECAO_OPCIONAL_1_CORPO}}"},
        {"tipo": "titulo2", "texto": "{{SECAO_OPCIONAL_2_TITULO}}"},
        {"tipo": "paragrafo", "texto": "{{SECAO_OPCIONAL_2_CORPO}}"},
    ]

    with tempfile.TemporaryDirectory() as tmp:
        template_path = os.path.join(tmp, "template.docx")
        saida_path = os.path.join(tmp, "saida.docx")
        gera_docx(blocos_template, template_path)

        # injeta um mc:Ignorable com prefixo não-registrado no root, como um
        # .docx real do Word — a troca de string não pode mexer nisso
        with zipfile.ZipFile(template_path) as z:
            xml = z.read("word/document.xml").decode("utf-8")
            outros = {n: z.read(n) for n in z.namelist() if n != "word/document.xml"}
        xml = xml.replace(
            "<w:document ",
            '<w:document xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
            'mc:Ignorable="w14" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" ',
            1,
        )
        with zipfile.ZipFile(template_path, "w", zipfile.ZIP_DEFLATED) as z:
            for nome, conteudo in outros.items():
                z.writestr(nome, conteudo)
            z.writestr("word/document.xml", xml.encode("utf-8"))

        dados = {
            # DISCIPLINA/PROFESSOR preenchidos; MAPA_MENTAL de propósito
            # ausente (deve remover o heading do Mapa Mental sozinho);
            # CERT_RA/CERT_TEMAS de propósito ausentes de valores/
            # linhas_repetir (deve remover a tabela Certificadora inteira,
            # só a Internalizadora/Mobilizadora sobrevive).
            "valores": {"DISCIPLINA": "Testes de Software", "PROFESSOR": "Marina de Lara"},
            "linhas_repetir": {
                "IM_RA": [
                    {"IM_COMPETENCIA": "Competência X", "IM_RA": "RA1"},
                ],
                "CRONO_INDICE": [
                    {"CRONO_INDICE": "1", "CRONO_DATA": "04/08/2026", "CRONO_RA": "RA1", "CRONO_DESC": "Introdução"},
                    {"CRONO_INDICE": "2", "CRONO_DATA": "11/08/2026", "CRONO_RA": "RA1", "CRONO_DESC": "Pirâmide de Testes"},
                ]
            },
            # só 1 seção opcional fornecida — o template tem 2 slots, o
            # segundo (sem entrada correspondente na lista) deve ser removido.
            # "topicos" clona o parágrafo do corpo uma vez por item, em vez
            # de um único parágrafo corrido.
            "secoes_opcionais": [
                {"titulo": "REGRAS DA DISCIPLINA", "topicos": ["Diagnóstica: exemplo.", "Formativa: exemplo."]},
            ],
        }
        preenche(template_path, dados, saida_path)

        with zipfile.ZipFile(saida_path) as z:
            xml_saida = z.read("word/document.xml").decode("utf-8")

        assert 'mc:Ignorable="w14"' in xml_saida, "mc:Ignorable foi alterado — reserialização vazou de novo"
        assert "Testes de Software" in xml_saida
        assert "Marina de Lara" in xml_saida
        assert "{{" not in xml_saida, "sobrou placeholder não substituído"
        assert xml_saida.count("<w:tr") == 5, f"esperava 5 linhas (IM: cabeçalho+1 | cronograma: cabeçalho+2), achei {xml_saida.count('<w:tr')}"
        assert "11/08/2026" in xml_saida and "Pirâmide de Testes" in xml_saida

        assert "Mapa Mental" not in xml_saida, "heading Mapa Mental deveria ter sido removido (MAPA_MENTAL vazio)"
        assert "Disciplinas Certificadoras" not in xml_saida, "tabela Certificadora não usada deveria ter sido removida por inteiro"
        assert "Disciplinas Internalizadoras e Mobilizadoras" in xml_saida and "Competência X" in xml_saida, "tabela IM usada não deveria ter sido removida"

        assert "REGRAS DA DISCIPLINA" in xml_saida, "seção opcional usada não foi preenchida"
        assert "Diagnóstica: exemplo." in xml_saida and "Formativa: exemplo." in xml_saida, "tópicos não foram clonados em parágrafos separados"
        assert xml_saida.count("Diagnóstica: exemplo.") == 1 and xml_saida.count("Formativa: exemplo.") == 1, "clonagem de tópico duplicou conteúdo"
        assert "SECAO_OPCIONAL_2" not in xml_saida, "slot de seção opcional não usado deveria ter sido removido por inteiro"

    print("demo ok — template preenchido, mc:Ignorable preservado, placeholders, linha de tabela e seções opcionais corretos")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--demo":
        demo()
    else:
        main()

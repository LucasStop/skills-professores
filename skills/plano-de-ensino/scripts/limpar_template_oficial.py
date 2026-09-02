#!/usr/bin/env python3
"""Tokeniza o .docx oficial vazio da PUCPR ("Plano de ensino PUCPR - novo
template (2026)") pra virar o template usado por preencher_template.py —
troca os colchetes de instrução por {{PLACEHOLDER}}, reduz as tabelas de
seção 3/4/cronograma a 1 linha-molde. Mesma técnica de substituição de string
no XML bruto (nunca reserializa a árvore inteira) documentada em
preencher_template.py.

Roda uma vez só, quando o `../assets/template-oficial-pucpr.docx` mudar (ex:
a PUCPR atualizar o template) — o resultado já fica versionado em
`../assets/template-oficial-tokenizado.docx`, não precisa rodar de novo a
cada plano de ensino gerado.

Uso:
    python3 limpar_template_oficial.py [origem.docx] [saida.docx]
    (default: ../assets/template-oficial-pucpr.docx -> ../assets/template-oficial-tokenizado.docx)
"""
import os
import re
import sys
import zipfile

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
ORIGEM_PADRAO = os.path.join(ASSETS, "template-oficial-pucpr.docx")
SAIDA_PADRAO = os.path.join(ASSETS, "template-oficial-tokenizado.docx")

BLOCO_P = re.compile(r"<w:p(?:\s[^>]*)?>.*?</w:p>", re.DOTALL)
BLOCO_TC = re.compile(r"<w:tc(?:\s[^>]*)?>.*?</w:tc>", re.DOTALL)
BLOCO_TR = re.compile(r"<w:tr(?:\s[^>]*)?>.*?</w:tr>", re.DOTALL)
BLOCO_TBL = re.compile(r"<w:tbl(?:\s[^>]*)?>.*?</w:tbl>", re.DOTALL)
BLOCO_R = re.compile(r"<w:r(?:\s[^>]*)?>.*?</w:r>", re.DOTALL)
BLOCO_RPR = re.compile(r"<w:rPr>.*?</w:rPr>", re.DOTALL)
BLOCO_T = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.DOTALL)


def _escapa(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _texto_bloco(bloco):
    return "".join(BLOCO_T.findall(bloco))


def _define_texto(bloco, texto):
    """bloco é um <w:p> ou algo que contém um — seta o texto no 1º run,
    colapsando runs extras se houver, ou criando um run novo se o parágrafo
    estiver vazio (sem nenhum <w:r>, comum nas células em branco do template
    oficial)."""
    p_m = re.search(r"<w:p(?:\s[^>]*)?>.*?</w:p>", bloco, re.DOTALL)
    if p_m is None:
        return bloco
    p_bloco = p_m.group(0)
    runs = list(BLOCO_R.finditer(p_bloco))
    if runs:
        rpr_m = BLOCO_RPR.search(runs[0].group(0))
        rpr = rpr_m.group(0) if rpr_m else ""
        novo_run = f'<w:r>{rpr}<w:t xml:space="preserve">{_escapa(texto)}</w:t></w:r>'
        novo_p = p_bloco[: runs[0].start()] + novo_run + p_bloco[runs[-1].end() :]
    else:
        novo_run = f'<w:r><w:t xml:space="preserve">{_escapa(texto)}</w:t></w:r>'
        novo_p = p_bloco[: -len("</w:p>")] + novo_run + "</w:p>"
    return bloco[: p_m.start()] + novo_p + bloco[p_m.end() :]


def substitui_paragrafo_exato(xml, texto_alvo, novo_texto, descricao):
    for m in BLOCO_P.finditer(xml):
        if _texto_bloco(m.group(0)) == texto_alvo:
            return xml[: m.start()] + _define_texto(m.group(0), novo_texto) + xml[m.end() :]
    print(f"aviso: parágrafo não encontrado: {descricao}", file=sys.stderr)
    return xml


def substitui_paragrafo_prefixo(xml, prefixo, novo_texto, descricao):
    for m in BLOCO_P.finditer(xml):
        if _texto_bloco(m.group(0)).startswith(prefixo):
            return xml[: m.start()] + _define_texto(m.group(0), novo_texto) + xml[m.end() :]
    print(f"aviso: parágrafo (prefixo) não encontrado: {descricao}", file=sys.stderr)
    return xml


def remove_sufixo_paragrafo(xml, prefixo, sufixo, descricao):
    """Alguns headings do template vêm com uma nota de instrução do NDE
    colada no fim do MESMO parágrafo (não é um parágrafo à parte, então
    `remove_paragrafo_prefixo` não pega) — remove só o sufixo, mantém o
    heading."""
    for m in BLOCO_P.finditer(xml):
        texto = _texto_bloco(m.group(0))
        if texto.startswith(prefixo) and sufixo in texto:
            novo_texto = texto.replace(sufixo, "").rstrip()
            return xml[: m.start()] + _define_texto(m.group(0), novo_texto) + xml[m.end() :]
    print(f"aviso: parágrafo (sufixo) não encontrado: {descricao}", file=sys.stderr)
    return xml


def remove_paragrafo_prefixo(xml, prefixo, descricao):
    """Remove um parágrafo de instrução do NDE (texto de orientação de como
    preencher o template, não conteúdo do plano de ensino em si) por
    inteiro — sobrando ele no documento final causa espaçamento/paginação
    estranha (blocos de texto grandes empurrando tabelas curtas pra páginas
    seguintes, deixando páginas quase em branco)."""
    for m in BLOCO_P.finditer(xml):
        if _texto_bloco(m.group(0)).startswith(prefixo):
            return xml[: m.start()] + xml[m.end() :]
    print(f"aviso: parágrafo (p/ remover, prefixo) não encontrado: {descricao}", file=sys.stderr)
    return xml


def tokeniza_linha_por_indice(tr_bloco, mapa_indice_texto):
    celulas = list(BLOCO_TC.finditer(tr_bloco))
    for i in sorted(mapa_indice_texto, reverse=True):
        if i >= len(celulas):
            continue
        c = celulas[i]
        novo_tc = _define_texto(c.group(0), mapa_indice_texto[i])
        tr_bloco = tr_bloco[: c.start()] + novo_tc + tr_bloco[c.end() :]
    return tr_bloco


def acha_tbl(xml, cabecalho_exato=None, primeira_celula_prefixo=None):
    for m in BLOCO_TBL.finditer(xml):
        bloco = m.group(0)
        trs = list(BLOCO_TR.finditer(bloco))
        if not trs:
            continue
        cels0 = list(BLOCO_TC.finditer(trs[0].group(0)))
        textos0 = tuple(_texto_bloco(c.group(0)) for c in cels0)
        if cabecalho_exato is not None and textos0 == cabecalho_exato:
            return m.start(), m.end(), bloco, trs
        if primeira_celula_prefixo is not None and textos0 and textos0[0].startswith(primeira_celula_prefixo):
            return m.start(), m.end(), bloco, trs
    return None


def remove_instrucao_e_tokeniza_vazia(xml, cabecalho_exato, tokens, descricao):
    """Tabelas com 3 linhas (header, instrução-exemplo, vazia de verdade) —
    remove a linha de instrução, tokeniza a vazia (linha-molde)."""
    achado = acha_tbl(xml, cabecalho_exato=cabecalho_exato)
    if achado is None:
        print(f"aviso: tabela não encontrada: {descricao}", file=sys.stderr)
        return xml
    inicio, fim, bloco, trs = achado
    molde = tokeniza_linha_por_indice(trs[2].group(0), dict(enumerate(tokens)))
    novo_bloco = bloco[: trs[0].end()] + molde + bloco[trs[2].end() :]
    return xml[:inicio] + novo_bloco + xml[fim:]


def tokeniza_linha_existente(xml, cabecalho_exato, tokens, descricao):
    """Tabela com só 2 linhas (header + a própria linha de instrução, sem
    linha vazia separada) — tokeniza a linha de instrução direto."""
    achado = acha_tbl(xml, cabecalho_exato=cabecalho_exato)
    if achado is None:
        print(f"aviso: tabela não encontrada: {descricao}", file=sys.stderr)
        return xml
    inicio, fim, bloco, trs = achado
    novo_tr = tokeniza_linha_por_indice(trs[1].group(0), dict(enumerate(tokens)))
    novo_bloco = bloco[: trs[1].start()] + novo_tr + bloco[trs[1].end() :]
    return xml[:inicio] + novo_bloco + xml[fim:]


def _estiliza_celula_cronograma(tc_bloco, alinhamento):
    """Cor padrão preta (o template original vinha com C0504D/accent2 —
    vermelho — em todas as células, herdado do exemplo de instrução) +
    alinhamento por coluna (Período/RA/Carga horária centralizados,
    Descrição à esquerda)."""
    tc_bloco = re.sub(r'<w:jc w:val="[^"]*"/>', f'<w:jc w:val="{alinhamento}"/>', tc_bloco)
    tc_bloco = re.sub(r'<w:color w:val="C0504D"(?: w:themeColor="accent2")?/>', "", tc_bloco)
    return tc_bloco


def tokeniza_cronograma(xml, tokens):
    achado = acha_tbl(xml, primeira_celula_prefixo="Período")
    if achado is None:
        print("aviso: tabela de cronograma não encontrada", file=sys.stderr)
        return xml
    inicio, fim, bloco, trs = achado
    molde = tokeniza_linha_por_indice(trs[1].group(0), dict(enumerate(tokens)))

    alinhamentos = ["center", "center", "left", "center"]  # Período, RA, Descrição, Carga horária
    pares = list(zip(BLOCO_TC.finditer(molde), alinhamentos))
    for tc_m, alinhamento in reversed(pares):
        nova_tc = _estiliza_celula_cronograma(tc_m.group(0), alinhamento)
        molde = molde[: tc_m.start()] + nova_tc + molde[tc_m.end() :]

    novo_bloco = bloco[: trs[0].end()] + molde + bloco[trs[-1].end() :]
    return xml[:inicio] + novo_bloco + xml[fim:]


def insere_quebra_de_pagina_antes(xml, texto_exato, descricao):
    """Marca o parágrafo de heading com `w:pageBreakBefore` — controla em
    que página cada seção começa, independente de quanto texto/tabela vem
    antes (layout fixo pedido pelo professor: capa+tabela sozinha na 1ª
    página, Ementa+Contexto juntos, Competências sozinha, Alinhamento
    Construtivo sozinha, Cronograma sozinha, Bibliografia+Orientações
    Gerais juntas — a ausência de quebra antes de Contexto/Orientações
    Gerais é o que mantém esses pares na mesma página do heading anterior)."""
    for m in BLOCO_P.finditer(xml):
        p_bloco = m.group(0)
        if _texto_bloco(p_bloco) != texto_exato:
            continue
        if "<w:pPr>" in p_bloco:
            novo_p = p_bloco.replace("<w:pPr>", "<w:pPr><w:pageBreakBefore/>", 1)
        else:
            abertura = re.match(r"<w:p(?:\s[^>]*)?>", p_bloco).group(0)
            novo_p = p_bloco[: len(abertura)] + "<w:pPr><w:pageBreakBefore/></w:pPr>" + p_bloco[len(abertura) :]
        return xml[: m.start()] + novo_p + xml[m.end() :]
    print(f"aviso: parágrafo não encontrado p/ quebra de página: {descricao}", file=sys.stderr)
    return xml


def insere_slot_secao_opcional(xml, antes_de_texto, indice):
    """Insere um par heading+corpo tokenizado (ex: {{SECAO_OPCIONAL_1_TITULO}}
    / {{SECAO_OPCIONAL_1_CORPO}}) logo antes do parágrafo com texto ==
    antes_de_texto — clona o pPr de um heading real do documento (mesmo
    pStyle "Titulo1linha") pra manter o mesmo padrão visual das outras
    seções. preencher_template.py remove o par inteiro se o professor não
    pedir essa seção (ver _remove_secoes_opcionais_nao_usadas lá)."""
    heading_ref = None
    for m in BLOCO_P.finditer(xml):
        if _texto_bloco(m.group(0)) == "BIBLIOGRAFIA":
            heading_ref = m.group(0)
            break
    if heading_ref is None:
        print("aviso: heading de referência (BIBLIOGRAFIA) não encontrado pra clonar estilo", file=sys.stderr)
        return xml

    titulo_tok = "{{SECAO_OPCIONAL_" + str(indice) + "_TITULO}}"
    corpo_tok = "{{SECAO_OPCIONAL_" + str(indice) + "_CORPO}}"
    novo_heading = _define_texto(heading_ref, titulo_tok)
    novo_corpo = f'<w:p><w:r><w:t xml:space="preserve">{corpo_tok}</w:t></w:r></w:p>'

    for m in BLOCO_P.finditer(xml):
        if _texto_bloco(m.group(0)) == antes_de_texto:
            return xml[: m.start()] + novo_heading + novo_corpo + xml[m.start() :]
    print(f"aviso: parágrafo de referência p/ inserir seção opcional não encontrado: {antes_de_texto!r}", file=sys.stderr)
    return xml


def tokeniza_tabela_identificacao(xml):
    posicoes = {
        0: {1: "{{ESCOLA}}", 3: "{{CURSO}}"},
        1: {1: "{{PERIODO}}", 3: "{{TURMA}}", 5: "{{TURNO}}"},
        2: {1: "{{CARGA_HORARIA}}", 3: "{{CREDITOS}}", 5: "{{CARGA_EXTENSAO}}"},
        3: {1: "{{REQUISITOS}}"},
    }
    for m in BLOCO_TBL.finditer(xml):
        bloco = m.group(0)
        trs = list(BLOCO_TR.finditer(bloco))
        if not trs:
            continue
        primeira_tc = BLOCO_TC.search(trs[0].group(0))
        if not primeira_tc or _texto_bloco(primeira_tc.group(0)).strip() != "Escola/ Câmpus:":
            continue
        novo_bloco = bloco
        for i in sorted(posicoes, reverse=True):
            tr_m = trs[i]
            novo_tr = tokeniza_linha_por_indice(tr_m.group(0), posicoes[i])
            novo_bloco = novo_bloco[: tr_m.start()] + novo_tr + novo_bloco[tr_m.end() :]
        return xml[: m.start()] + novo_bloco + xml[m.end() :]
    print("aviso: tabela de identificação não encontrada", file=sys.stderr)
    return xml


def main():
    origem = sys.argv[1] if len(sys.argv) > 1 else ORIGEM_PADRAO
    saida = sys.argv[2] if len(sys.argv) > 2 else SAIDA_PADRAO
    with zipfile.ZipFile(origem) as z_in:
        nomes = z_in.namelist()
        conteudos = {n: z_in.read(n) for n in nomes}
    xml = conteudos["word/document.xml"].decode("utf-8")

    xml = substitui_paragrafo_exato(xml, "NOME DA DISCIPLINA", "{{DISCIPLINA}}", "disciplina")
    xml = substitui_paragrafo_exato(xml, "NOME DO(A) PROFESSOR(A)", "{{PROFESSOR}}", "professor")
    xml = substitui_paragrafo_exato(xml, "Ano/semestre de oferta da disciplina", "{{ANO_SEMESTRE}}", "ano/semestre")

    # Ementa e Contexto começam com o mesmo texto de instrução do NDE — a 1ª
    # chamada tokeniza a ocorrência da Ementa, a 2ª (já sem o prefixo antigo
    # na 1ª) acha a do Contexto.
    prefixo_nde = "[Texto construído pelo NDE do curso"
    xml = substitui_paragrafo_prefixo(xml, prefixo_nde, "{{EMENTA}}", "ementa")
    xml = substitui_paragrafo_prefixo(xml, prefixo_nde, "{{CONTEXTO}}", "contexto da disciplina")

    xml = substitui_paragrafo_prefixo(xml, "[Representação gráfica das aprendizagens", "{{MAPA_MENTAL}}", "mapa mental")

    # Parágrafos de instrução do NDE (orientação de como preencher, não
    # conteúdo do plano de ensino) — sobrando no documento final, distorcem
    # a paginação (blocos de texto grandes empurrando tabelas curtas pra
    # páginas seguintes). Removidos por inteiro, um por um.
    for prefixo, descricao in [
        ("Utilizar este quadro caso a disciplina não seja certificadora", "instrução — quadro IM"),
        ("Em caso de disciplinas certificadoras, apagar o quadro anterior", "instrução — quadro certificadora"),
        ("Observação: Em caso de disciplina mista", "instrução — disciplina mista"),
        ("Clique aqui e relembre como funciona o modelo de Ensino por Competências", "instrução — link ensino por competências"),
        ("(Inserir uma linha para cada Resultado de Aprendizagem", "instrução — alinhamento construtivo"),
        ("Detalhamento das atividades pedagógicas propostas para o período", "instrução — cronograma intro"),
        ("As datas previstas para a realização das avaliações de 2ª chamada", "instrução — 2ª chamada"),
        ("A(s) atividade(s)", "instrução — TDE"),
        ("Atividades extensionistas: Descrever as etapas", "instrução — extensão"),
        ("Acrescente o número de linha(s) que julgar necessário", "instrução — cronograma linhas"),
        ("No mínimo 3 títulos por disciplina", "instrução — bibliografia básica"),
        ("[Sugestão para o docente", "instrução — orientações gerais"),
    ]:
        xml = remove_paragrafo_prefixo(xml, prefixo, descricao)

    xml = remove_sufixo_paragrafo(
        xml,
        "COMPETÊNCIA(S), TEMAS DE ESTUDO",
        " [Este item é construído pelo NDE do curso, caso haja sugestões de "
        "ajustes o professor deverá contatar o NDE ou a coordenação do curso.]",
        "sufixo — heading seção 3",
    )

    # Slot de seção opcional (ex: "Regras da Disciplina") — não existe no
    # template oficial, mas todos os planos reais da Escola Politécnica têm
    # essa seção nessa posição (entre Cronograma e Bibliografia). Fica
    # tokenizado e é removido em runtime por preencher_template.py se o
    # professor não pedir (ver Bloco 1 de references/entrevista.md).
    xml = insere_slot_secao_opcional(xml, "BIBLIOGRAFIA", 1)

    xml = substitui_paragrafo_prefixo(xml, "[As Referências Bibliográficas", "{{BIBLIOGRAFIA_BASICA}}", "bibliografia básica")
    xml = substitui_paragrafo_prefixo(xml, "[No mínimo 5 títulos", "{{BIBLIOGRAFIA_COMPLEMENTAR}}", "bibliografia complementar")

    xml = tokeniza_tabela_identificacao(xml)

    xml = remove_instrucao_e_tokeniza_vazia(
        xml,
        cabecalho_exato=("Competência e Elementos de Competência", "I/M", "Temas de Estudo", "Resultados de Aprendizagem"),
        tokens=["{{IM_COMPETENCIA}}", "{{IM_CLASSIFICACAO}}", "{{IM_TEMAS}}", "{{IM_RA}}"],
        descricao="seção 3 — Internalizadoras/Mobilizadoras",
    )
    xml = tokeniza_linha_existente(
        xml,
        cabecalho_exato=("Resultado de Aprendizagem (Competência)", "Temas de Estudo"),
        tokens=["{{CERT_RA}}", "{{CERT_TEMAS}}"],
        descricao="seção 3 — Certificadoras",
    )
    xml = remove_instrucao_e_tokeniza_vazia(
        xml,
        cabecalho_exato=("Resultado(s) de aprendizagem", "Indicadores de desempenho",
                          "Metodologias, recursos e estratégias de ensino-aprendizagem",
                          "Processos de avaliação e recuperação de aprendizagem"),
        tokens=["{{MET_RA}}", "{{MET_ID}}", "{{MET_METODOLOGIA}}", "{{MET_AVALIACAO}}"],
        descricao="seção 4 — Alinhamento Construtivo",
    )
    xml = tokeniza_cronograma(xml, ["{{CRONO_PERIODO}}", "{{CRONO_RA}}", "{{CRONO_DESC}}", "{{CRONO_CH}}"])

    # Layout fixo por seção, pedido pelo professor: 1ª página só capa+tabela
    # de identificação; Ementa+Contexto juntos; Competências sozinha;
    # Alinhamento Construtivo sozinha; Cronograma sozinha (pode espalhar por
    # várias páginas, mas sempre começa numa nova); Bibliografia+Orientações
    # Gerais juntas (sem quebra entre elas).
    for texto, descricao in [
        ("EMENTA: ", "seção 1 — Ementa"),
        ("COMPETÊNCIA(S), TEMAS DE ESTUDO E RESULTADOS DE APRENDIZAGEM", "seção 3 — Competências"),
        ("ALINHAMENTO CONSTRUTIVO: METODOLOGIA E AVALIAÇÃO ", "seção 4 — Alinhamento Construtivo"),
        ("CRONOGRAMA DE ATIVIDADES PEDAGÓGICAS", "seção 5 — Cronograma"),
        ("BIBLIOGRAFIA", "seção 6 — Bibliografia"),
    ]:
        xml = insere_quebra_de_pagina_antes(xml, texto, descricao)

    conteudos["word/document.xml"] = xml.encode("utf-8")
    with zipfile.ZipFile(saida, "w", zipfile.ZIP_DEFLATED) as z_out:
        for nome in nomes:
            z_out.writestr(nome, conteudos[nome])

    print(f"gerado {saida}")


def demo():
    """Auto-checagem das duas transformações novas (quebra de página fixa
    por seção + estilo da linha do cronograma) sobre um XML mínimo, sem
    depender do .docx oficial. python3 limpar_template_oficial.py --demo"""
    p_sem_pPr = '<w:p w:rsidR="1"><w:r><w:t>BIBLIOGRAFIA</w:t></w:r></w:p>'
    p_com_pPr = '<w:p><w:pPr><w:pStyle w:val="x"/></w:pPr><w:r><w:t>CRONOGRAMA DE ATIVIDADES PEDAGÓGICAS</w:t></w:r></w:p>'
    xml = f"<root>{p_sem_pPr}{p_com_pPr}</root>"

    xml = insere_quebra_de_pagina_antes(xml, "BIBLIOGRAFIA", "teste — sem pPr")
    xml = insere_quebra_de_pagina_antes(xml, "CRONOGRAMA DE ATIVIDADES PEDAGÓGICAS", "teste — com pPr")
    assert xml.count("<w:pageBreakBefore/>") == 2, "quebra de página não aplicada nos 2 parágrafos"
    assert "<w:pPr><w:pageBreakBefore/></w:pPr><w:r><w:t>BIBLIOGRAFIA" in xml, "parágrafo sem pPr não ganhou pPr novo corretamente"
    assert "<w:pPr><w:pageBreakBefore/><w:pStyle" in xml, "parágrafo com pPr existente não teve a quebra inserida como 1º filho"

    xml_sem_quebra = insere_quebra_de_pagina_antes("<root></root>", "NÃO EXISTE", "teste — heading ausente")
    assert xml_sem_quebra == "<root></root>", "heading ausente não deveria alterar o xml"

    tc = (
        '<w:tc><w:tcPr><w:tcW w:w="100" w:type="dxa"/></w:tcPr>'
        '<w:p><w:pPr><w:jc w:val="both"/><w:rPr><w:color w:val="C0504D" w:themeColor="accent2"/></w:rPr></w:pPr>'
        '<w:r><w:rPr><w:color w:val="C0504D" w:themeColor="accent2"/></w:rPr><w:t>{{CRONO_DESC}}</w:t></w:r></w:p></w:tc>'
    )
    tc_centralizada = _estiliza_celula_cronograma(tc, "center")
    assert 'w:jc w:val="center"' in tc_centralizada, "alinhamento não trocado"
    assert "C0504D" not in tc_centralizada, "cor vermelha não removida"
    tc_esquerda = _estiliza_celula_cronograma(tc, "left")
    assert 'w:jc w:val="left"' in tc_esquerda, "alinhamento à esquerda não aplicado"

    print("demo ok — quebra de página fixa por seção e estilo do cronograma (cor preta, alinhamento por coluna)")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--demo":
        demo()
    else:
        main()

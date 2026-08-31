#!/usr/bin/env python3
"""Gera um .docx válido (Office Open XML) só com a biblioteca padrão do
Python — zipfile + xml.etree.ElementTree. Sem pip install, sem LibreOffice,
sem pacote npm.

Uso:
    python3 gerar_docx.py documento.json saida.docx

Formato de documento.json — lista de blocos:
[
  {"tipo": "titulo1", "texto": "Plano de Ensino - Data Analytics"},
  {"tipo": "titulo2", "texto": "1. Ementa"},
  {"tipo": "paragrafo", "texto": "..."},
  {"tipo": "tabela", "cabecalho": ["#", "Data", "RA", "Descrição", "Carga horária"],
   "linhas": [["1", "04/08", "RA1", "Introdução", "04:00"]],
   "larguras": [5, 12, 8, 55, 20]}
]

O mesmo documento.json também é aceito por gerar_pdf.py — os dois formatos
saem do mesmo conteúdo, renderizados por motores diferentes (não é uma
conversão docx->pdf).
"""
import json
import sys
import zipfile
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML_NS = "http://www.w3.org/XML/1998/namespace"
ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)

RODAPE_PADRAO = "Percursos Formativos - Centro de Ensino e Aprendizagem da PUCPR (2026)"


def w(tag):
    return f"{{{W_NS}}}{tag}"


def r_(tag):
    return f"{{{R_NS}}}{tag}"


def _text_run(parent, texto, negrito=False):
    r = ET.SubElement(parent, w("r"))
    if negrito:
        rPr = ET.SubElement(r, w("rPr"))
        ET.SubElement(rPr, w("b"))
    t = ET.SubElement(r, w("t"))
    t.set(f"{{{XML_NS}}}space", "preserve")
    t.text = texto
    return r


def _paragrafo(body, texto, estilo=None, negrito=False):
    p = ET.SubElement(body, w("p"))
    if estilo:
        pPr = ET.SubElement(p, w("pPr"))
        ET.SubElement(pPr, w("pStyle"), {w("val"): estilo})
    _text_run(p, texto, negrito=negrito)
    return p


def _larguras_colunas(n_cols, largura_total, pesos=None):
    """pesos: lista de números relativos (ex: [15, 10, 55, 20]) ou None p/ igual."""
    if not pesos:
        pesos = [1] * n_cols
    soma = sum(pesos)
    return [int(largura_total * p / soma) for p in pesos]


def _tabela(body, cabecalho, linhas, pesos=None):
    n_cols = len(cabecalho)
    largura_total = 9000  # twips (~ largura útil de uma página A4 com margens de 2cm)
    larguras = _larguras_colunas(n_cols, largura_total, pesos)

    tbl = ET.SubElement(body, w("tbl"))
    tblPr = ET.SubElement(tbl, w("tblPr"))
    ET.SubElement(tblPr, w("tblW"), {w("w"): "0", w("type"): "auto"})
    bordas = ET.SubElement(tblPr, w("tblBorders"))
    for aresta in ("top", "left", "bottom", "right", "insideH", "insideV"):
        ET.SubElement(bordas, w(aresta), {w("val"): "single", w("sz"): "4", w("space"): "0", w("color"): "auto"})

    grid = ET.SubElement(tbl, w("tblGrid"))
    for largura in larguras:
        ET.SubElement(grid, w("gridCol"), {w("w"): str(largura)})

    def linha(valores, negrito=False):
        tr = ET.SubElement(tbl, w("tr"))
        for valor, largura in zip(valores, larguras):
            tc = ET.SubElement(tr, w("tc"))
            tcPr = ET.SubElement(tc, w("tcPr"))
            ET.SubElement(tcPr, w("tcW"), {w("w"): str(largura), w("type"): "dxa"})
            if negrito:
                ET.SubElement(tcPr, w("shd"), {w("val"): "clear", w("color"): "auto", w("fill"): "D9D9D9"})
            p = ET.SubElement(tc, w("p"))
            _text_run(p, str(valor), negrito=negrito)

    linha(cabecalho, negrito=True)
    for l in linhas:
        linha(l)
    return tbl


def monta_document_xml(blocos):
    document = ET.Element(w("document"))
    body = ET.SubElement(document, w("body"))

    for bloco in blocos:
        tipo = bloco["tipo"]
        if tipo == "titulo1":
            _paragrafo(body, bloco["texto"], estilo="Heading1")
        elif tipo == "titulo2":
            _paragrafo(body, bloco["texto"], estilo="Heading2")
        elif tipo == "paragrafo":
            _paragrafo(body, bloco["texto"])
        elif tipo == "tabela":
            _tabela(body, bloco["cabecalho"], bloco["linhas"], pesos=bloco.get("larguras"))
        else:
            raise ValueError(f"tipo de bloco desconhecido: {tipo!r}")

    sectPr = ET.SubElement(body, w("sectPr"))
    ET.SubElement(sectPr, w("footerReference"), {w("type"): "default", r_("id"): "rId2"})
    ET.SubElement(sectPr, w("pgSz"), {w("w"): "11906", w("h"): "16838"})  # A4
    ET.SubElement(sectPr, w("pgMar"), {
        w("top"): "1417", w("right"): "1417", w("bottom"): "1417", w("left"): "1417",
        w("header"): "708", w("footer"): "708", w("gutter"): "0",
    })

    xml_bytes = ET.tostring(document, encoding="UTF-8")
    return b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + xml_bytes


CONTENT_TYPES_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
</Types>
"""

RELS_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

DOCUMENT_RELS_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
</Relationships>
"""

FOOTER_XML = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="{W_NS}">
  <w:p>
    <w:pPr><w:jc w:val="center"/></w:pPr>
    <w:r><w:rPr><w:sz w:val="16"/><w:color w:val="595959"/></w:rPr><w:t xml:space="preserve">{RODAPE_PADRAO} &#183; Página </w:t></w:r>
    <w:fldSimple w:instr="PAGE"><w:r><w:rPr><w:sz w:val="16"/><w:color w:val="595959"/></w:rPr><w:t>1</w:t></w:r></w:fldSimple>
  </w:p>
</w:ftr>
""".encode("utf-8")

STYLES_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault><w:rPr><w:sz w:val="22"/></w:rPr></w:rPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr><w:b/><w:sz w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr><w:b/><w:sz w:val="26"/></w:rPr>
  </w:style>
</w:styles>
"""


def gera_docx(blocos, caminho_saida):
    document_xml = monta_document_xml(blocos)
    with zipfile.ZipFile(caminho_saida, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        z.writestr("_rels/.rels", RELS_XML)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/_rels/document.xml.rels", DOCUMENT_RELS_XML)
        z.writestr("word/styles.xml", STYLES_XML)
        z.writestr("word/footer1.xml", FOOTER_XML)


def main():
    if len(sys.argv) != 3:
        print("uso: python3 gerar_docx.py documento.json saida.docx", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        blocos = json.load(f)
    gera_docx(blocos, sys.argv[2])
    print(f"gerado {sys.argv[2]}")


def demo():
    """Auto-checagem: gera um .docx num arquivo temporário e valida a
    estrutura do zip/XML. python3 gerar_docx.py --demo"""
    import os
    import tempfile

    blocos = [
        {"tipo": "titulo1", "texto": "Plano de Ensino - Disciplina Teste"},
        {"tipo": "titulo2", "texto": "1. Ementa"},
        {"tipo": "paragrafo", "texto": "Texto de ementa de exemplo com acentuação:ç, ã, é."},
        {"tipo": "titulo2", "texto": "5. Cronograma"},
        {"tipo": "tabela", "cabecalho": ["Data", "RA", "Descrição", "Carga horária"],
         "linhas": [["04/08", "RA1", "Introdução", "4h"], ["11/08", "RA1", "Fundamentos", "4h"]]},
    ]

    with tempfile.TemporaryDirectory() as tmp:
        caminho = os.path.join(tmp, "teste.docx")
        gera_docx(blocos, caminho)

        assert zipfile.is_zipfile(caminho), "arquivo gerado não é um zip válido"
        with zipfile.ZipFile(caminho) as z:
            nomes = set(z.namelist())
            esperados = {"[Content_Types].xml", "_rels/.rels", "word/document.xml",
                         "word/_rels/document.xml.rels", "word/styles.xml", "word/footer1.xml"}
            assert esperados <= nomes, f"faltam entradas no zip: {esperados - nomes}"

            footer_bytes = z.read("word/footer1.xml")
            assert RODAPE_PADRAO.encode("utf-8") in footer_bytes, "rodapé institucional ausente no footer1.xml"

            xml_bytes = z.read("word/document.xml")
            root = ET.fromstring(xml_bytes)
            paragrafos = root.findall(f".//{w('p')}")
            tabelas = root.findall(f".//{w('tbl')}")
            linhas_tabela = root.findall(f".//{w('tbl')}/{w('tr')}")
            assert len(paragrafos) >= 3, f"esperava >=3 parágrafos, achei {len(paragrafos)}"
            assert len(tabelas) == 1, f"esperava 1 tabela, achei {len(tabelas)}"
            assert len(linhas_tabela) == 3, f"esperava 3 linhas (cabeçalho + 2), achei {len(linhas_tabela)}"

            textos = [t.text for t in root.findall(f".//{w('t')}")]
            assert "Plano de Ensino - Disciplina Teste" in textos
            assert "Introdução" in textos

    print("demo ok — .docx gerado e estrutura validada (zip + XML)")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--demo":
        demo()
    else:
        main()

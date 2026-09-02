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

Uso:
    python3 preencher_template.py template.docx dados.json saida.docx

dados.json:
{
  "valores": {"DISCIPLINA": "Testes de Software", "PROFESSOR": "Marina de Lara"},
  "linhas_repetir": {
    "CRONO_INDICE": [
      {"CRONO_INDICE": "1", "CRONO_DATA": "04/08/2026", "CRONO_RA": "RA1", "CRONO_DESC": "Introdução", "CRONO_CH": "04:00"}
    ]
  }
}
"""
import json
import re
import sys
import zipfile

TR_RE = re.compile(r"<w:tr(?:\s[^>]*)?>.*?</w:tr>", re.DOTALL)


def _escapa(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _acha_bloco_tr(xml, ancora_token):
    marcador = "{{" + ancora_token + "}}"
    for m in TR_RE.finditer(xml):
        if marcador in m.group(0):
            return m.start(), m.end(), m.group(0)
    return None


def preenche(template_path, dados, saida_path):
    valores = dados.get("valores", {})
    linhas_repetir = dados.get("linhas_repetir", {})

    with zipfile.ZipFile(template_path) as z_in:
        xml = z_in.read("word/document.xml").decode("utf-8")
        outros = {n: z_in.read(n) for n in z_in.namelist() if n != "word/document.xml"}

    for ancora_token, linhas in linhas_repetir.items():
        achado = _acha_bloco_tr(xml, ancora_token)
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
        {"tipo": "titulo2", "texto": "Cronograma"},
        {"tipo": "tabela", "cabecalho": ["Data", "RA", "Descrição"],
         "linhas": [["{{CRONO_DATA}}", "{{CRONO_RA}}", "{{CRONO_INDICE}} {{CRONO_DESC}}"]]},
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
            "valores": {"DISCIPLINA": "Testes de Software", "PROFESSOR": "Marina de Lara"},
            "linhas_repetir": {
                "CRONO_INDICE": [
                    {"CRONO_INDICE": "1", "CRONO_DATA": "04/08/2026", "CRONO_RA": "RA1", "CRONO_DESC": "Introdução"},
                    {"CRONO_INDICE": "2", "CRONO_DATA": "11/08/2026", "CRONO_RA": "RA1", "CRONO_DESC": "Pirâmide de Testes"},
                ]
            },
        }
        preenche(template_path, dados, saida_path)

        with zipfile.ZipFile(saida_path) as z:
            xml_saida = z.read("word/document.xml").decode("utf-8")

        assert 'mc:Ignorable="w14"' in xml_saida, "mc:Ignorable foi alterado — reserialização vazou de novo"
        assert "Testes de Software" in xml_saida
        assert "Marina de Lara" in xml_saida
        assert "{{" not in xml_saida, "sobrou placeholder não substituído"
        assert xml_saida.count("<w:tr") == 3, f"esperava 3 linhas (cabeçalho + 2 clonadas), achei {xml_saida.count('<w:tr')}"
        assert "11/08/2026" in xml_saida and "Pirâmide de Testes" in xml_saida

    print("demo ok — template preenchido, mc:Ignorable preservado, placeholders e linha de tabela corretos")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--demo":
        demo()
    else:
        main()

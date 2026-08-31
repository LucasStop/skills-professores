#!/usr/bin/env python3
"""Gera um .pdf a partir do zero (sintaxe PDF crua: objetos, content stream,
xref) só com a biblioteca padrão do Python. Sem reportlab, sem LibreOffice,
sem pacote nenhum — fontes-base do próprio PDF (Helvetica/Helvetica-Bold via
WinAnsiEncoding, cobre acentuação do português sem precisar embutir fonte).

Uso:
    python3 gerar_pdf.py documento.json saida.pdf

Mesmo formato de documento.json de gerar_docx.py (ver docstring lá) — os
dois formatos saem do mesmo conteúdo, renderizados por motores diferentes
(não é conversão docx->pdf).

Ponytail: layout simples (texto corrido + tabela com grade, sem imagem,
sem formatação rica) — teto conhecido, suficiente pro plano de ensino.
Se um dia precisar de fidelidade visual rica, reconsiderar LibreOffice.
"""
import json
import sys
import textwrap

PAGE_W, PAGE_H = 595.28, 841.89  # A4 em pontos
MARGIN = 56.0  # ~2cm
CONTENT_W = PAGE_W - 2 * MARGIN
LINE_HEIGHT_FACTOR = 1.25
CELL_PADDING = 4.0

TAMANHOS = {"titulo1": 16, "titulo2": 13, "paragrafo": 10, "tabela": 9}
LARGURA_MEDIA_CHAR = {"F1": 0.50, "F2": 0.56}  # fração do font-size, aproximação Helvetica


def _escapa_pdf_string(texto):
    b = texto.encode("cp1252", errors="replace")
    b = b.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
    return b


def _largura_texto(texto, size, fonte):
    return len(texto) * size * LARGURA_MEDIA_CHAR[fonte]


def _quebra_linhas(texto, size, fonte, largura_max):
    fator = LARGURA_MEDIA_CHAR[fonte]
    max_chars = max(1, int(largura_max / (size * fator)))
    linhas = textwrap.wrap(texto, width=max_chars) if texto else [""]
    return linhas or [""]


def _larguras_colunas(n_cols, largura_total, pesos=None):
    if not pesos:
        pesos = [1] * n_cols
    soma = sum(pesos)
    return [largura_total * p / soma for p in pesos]


class Layout:
    """Fase 1: decide onde cada linha de texto/tabela cai, já paginando.
    Produz `self.paginas`: lista de páginas, cada uma uma lista de ops
    ('text', x, y, fonte, size, texto) ou ('line', x1, y1, x2, y2)."""

    def __init__(self):
        self.paginas = [[]]
        self.y = PAGE_H - MARGIN

    def _pagina_atual(self):
        return self.paginas[-1]

    def nova_pagina(self):
        self.paginas.append([])
        self.y = PAGE_H - MARGIN

    def _garante_espaco(self, altura):
        if self.y - altura < MARGIN:
            self.nova_pagina()

    def texto(self, texto, size, fonte, negrito_ignora=False):
        line_height = size * LINE_HEIGHT_FACTOR
        for linha in _quebra_linhas(texto, size, fonte, CONTENT_W):
            self._garante_espaco(line_height)
            self._pagina_atual().append(("text", MARGIN, self.y - size, fonte, size, linha))
            self.y -= line_height

    def espaco(self, altura):
        self.y -= altura

    def tabela(self, cabecalho, linhas, pesos=None):
        size = TAMANHOS["tabela"]
        line_height = size * LINE_HEIGHT_FACTOR
        larguras = _larguras_colunas(len(cabecalho), CONTENT_W, pesos)
        x_bordas = [MARGIN]
        for lg in larguras:
            x_bordas.append(x_bordas[-1] + lg)

        def desenha_linha(valores, negrito):
            fonte = "F2" if negrito else "F1"
            linhas_por_cel = [
                _quebra_linhas(str(v), size, fonte, larguras[i] - 2 * CELL_PADDING)
                for i, v in enumerate(valores)
            ]
            n_linhas = max(len(l) for l in linhas_por_cel)
            altura_linha = n_linhas * line_height + 2 * CELL_PADDING
            self._garante_espaco(altura_linha)
            y_topo = self.y
            ops = self._pagina_atual()
            for x in x_bordas:
                ops.append(("line", x, y_topo, x, y_topo - altura_linha))
            ops.append(("line", x_bordas[0], y_topo, x_bordas[-1], y_topo))
            ops.append(("line", x_bordas[0], y_topo - altura_linha, x_bordas[-1], y_topo - altura_linha))
            for i, celula_linhas in enumerate(linhas_por_cel):
                cx = x_bordas[i] + CELL_PADDING
                cy = y_topo - CELL_PADDING - size
                for linha in celula_linhas:
                    ops.append(("text", cx, cy, fonte, size, linha))
                    cy -= line_height
            self.y -= altura_linha

        desenha_linha(cabecalho, negrito=True)
        for linha_dados in linhas:
            if self.y - line_height - 2 * CELL_PADDING < MARGIN:
                self.nova_pagina()
                desenha_linha(cabecalho, negrito=True)  # repete cabeçalho na página nova
            desenha_linha(linha_dados, negrito=False)


def monta_layout(blocos):
    layout = Layout()
    for bloco in blocos:
        tipo = bloco["tipo"]
        if tipo == "titulo1":
            layout.espaco(6)
            layout.texto(bloco["texto"], TAMANHOS["titulo1"], "F2")
            layout.espaco(4)
        elif tipo == "titulo2":
            layout.espaco(8)
            layout.texto(bloco["texto"], TAMANHOS["titulo2"], "F2")
            layout.espaco(2)
        elif tipo == "paragrafo":
            layout.texto(bloco["texto"], TAMANHOS["paragrafo"], "F1")
            layout.espaco(4)
        elif tipo == "tabela":
            layout.tabela(bloco["cabecalho"], bloco["linhas"], pesos=bloco.get("larguras"))
            layout.espaco(8)
        else:
            raise ValueError(f"tipo de bloco desconhecido: {tipo!r}")
    return layout.paginas


def _stream_da_pagina(ops):
    partes = [b"q\n"]
    for op in ops:
        if op[0] == "text":
            _, x, y, fonte, size, texto = op
            partes.append(f"BT\n/{fonte} {size} Tf\n{x:.2f} {y:.2f} Td\n".encode("ascii"))
            partes.append(b"(" + _escapa_pdf_string(texto) + b") Tj\n")
            partes.append(b"ET\n")
        elif op[0] == "line":
            _, x1, y1, x2, y2 = op
            partes.append(f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S\n".encode("ascii"))
    partes.append(b"Q\n")
    return b"".join(partes)


def gera_pdf(blocos, caminho_saida):
    paginas_ops = monta_layout(blocos)

    objetos = {}  # numero -> bytes do corpo do objeto (sem "N 0 obj"/"endobj")
    objetos[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objetos[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    objetos[4] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"

    kids = []
    for i, ops in enumerate(paginas_ops):
        content_num = 5 + 2 * i
        page_num = 6 + 2 * i
        stream = _stream_da_pagina(ops)
        objetos[content_num] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"endstream"
        )
        objetos[page_num] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W:.2f} {PAGE_H:.2f}] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_num} 0 R >>"
        ).encode("ascii")
        kids.append(f"{page_num} 0 R")

    objetos[2] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>".encode("ascii")

    buf = bytearray()
    buf += b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = {}
    for num in sorted(objetos):
        offsets[num] = len(buf)
        buf += f"{num} 0 obj\n".encode("ascii")
        buf += objetos[num]
        buf += b"\nendobj\n"

    xref_offset = len(buf)
    total_objs = max(objetos) + 1
    buf += f"xref\n0 {total_objs}\n".encode("ascii")
    buf += b"0000000000 65535 f \n"
    for num in range(1, total_objs):
        offset = offsets.get(num)
        if offset is None:
            buf += b"0000000000 00000 f \n"
        else:
            buf += f"{offset:010d} 00000 n \n".encode("ascii")
    buf += b"trailer\n"
    buf += f"<< /Size {total_objs} /Root 1 0 R >>\n".encode("ascii")
    buf += b"startxref\n"
    buf += f"{xref_offset}\n".encode("ascii")
    buf += b"%%EOF"

    with open(caminho_saida, "wb") as f:
        f.write(buf)


def main():
    if len(sys.argv) != 3:
        print("uso: python3 gerar_pdf.py documento.json saida.pdf", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        blocos = json.load(f)
    gera_pdf(blocos, sys.argv[2])
    print(f"gerado {sys.argv[2]}")


def demo():
    """Auto-checagem: gera um .pdf num arquivo temporário e valida a
    estrutura mínima (header, %%EOF, xref, objetos, conteúdo esperado no
    stream). python3 gerar_pdf.py --demo"""
    import os
    import tempfile

    muitas_linhas = [[f"{d:02d}/08", "RA1", f"Tema {d}", "4h"] for d in range(1, 61)]
    blocos = [
        {"tipo": "titulo1", "texto": "Plano de Ensino - Disciplina Teste"},
        {"tipo": "titulo2", "texto": "1. Ementa"},
        {"tipo": "paragrafo", "texto": "Texto de ementa de exemplo com acentuação: ç, ã, é. " * 6},
        {"tipo": "titulo2", "texto": "5. Cronograma"},
        {"tipo": "tabela", "cabecalho": ["Data", "RA", "Descrição", "Carga horária"],
         "linhas": muitas_linhas, "larguras": [15, 10, 55, 20]},
    ]

    with tempfile.TemporaryDirectory() as tmp:
        caminho = os.path.join(tmp, "teste.pdf")
        gera_pdf(blocos, caminho)

        with open(caminho, "rb") as f:
            conteudo = f.read()

        assert conteudo.startswith(b"%PDF-1.4"), "header PDF ausente"
        assert conteudo.rstrip().endswith(b"%%EOF"), "%%EOF ausente"
        assert b"xref" in conteudo, "tabela xref ausente"
        assert b"/Type /Catalog" in conteudo, "catalog ausente"
        n_paginas = conteudo.count(b"/Type /Page ") + conteudo.count(b"/Type /Page/") + conteudo.count(b"/Type /Page\n")
        # conta via /Type /Page (sem "s", que também bate em "/Type /Pages") de forma simples:
        n_paginas = conteudo.count(b"/Type /Page /Parent")
        assert n_paginas >= 2, f"esperava pelo menos 2 páginas (cronograma longo força quebra), achei {n_paginas}"
        assert b"Disciplina Teste" in conteudo, "texto do titulo1 não apareceu no stream"
        assert b"Tema 1" in conteudo, "conteudo da tabela nao apareceu no stream"

        # confere que os offsets do xref batem com onde cada "N 0 obj" realmente comeca
        linhas = conteudo.split(b"\nxref\n", 1)[1].split(b"\ntrailer")[0].splitlines()
        entradas = [l for l in linhas if l.endswith(b" n ")]
        for entrada in entradas:
            offset = int(entrada[:10])
            trecho = conteudo[offset:offset + 20]
            assert b" obj" in trecho, f"offset do xref não aponta pra um objeto: {offset} -> {trecho!r}"

    print(f"demo ok — .pdf gerado ({len(conteudo)} bytes, {n_paginas} páginas), estrutura e xref validados")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--demo":
        demo()
    else:
        main()

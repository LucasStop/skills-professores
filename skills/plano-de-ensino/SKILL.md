---
name: plano-de-ensino
description: Monta o plano de ensino completo de uma disciplina universitária no template PUCPR "Percursos Formativos" (Ementa, Contexto da Disciplina, Competências/RA, Metodologia e Avaliação, Cronograma, Bibliografia, Orientações Gerais), calcula o cronograma automaticamente a partir de datas/RAs/dias de aula, e exporta .docx + .pdf prontos pra editar. Use quando o professor pedir "monta o plano de ensino de [disciplina]", "gera o cronograma da disciplina", "preciso montar/atualizar o plano de ensino", ou pedir pra recalcular o cronograma com novas datas. Não use pra criar uma skill nova do zero (isso é a `criar-skill-professor`).
metadata:
  repo: skills-professores
  template: percursos-formativos-pucpr-2026
---

# Plano de ensino

Gera o documento completo a partir de uma entrevista curta + um cálculo de cronograma, e exporta `.docx`+`.pdf` sem depender de nada instalado além do Python 3. Leia `references/template-pucpr.md` (estrutura oficial de 7 seções + "Regras da Disciplina" opcional, confirmada contra o `.docx` editável oficial da PUCPR e os 7 planos reais em `references/planos-exemplo/`) e `references/entrevista.md` (roteiro completo de perguntas por bloco) antes de rodar o fluxo abaixo.

O template oficial já está no repo (`assets/template-oficial-tokenizado.docx`, com a arte institucional: faixa, selo, cores) — **não gere do zero**, use `scripts/preencher_template.py` pra preencher os campos direto nesse arquivo (ver nota no fim de `references/template-pucpr.md`). `gerar_docx.py`/`gerar_pdf.py` são o caminho de reserva se esse asset não estiver disponível.

## 0. Checagem de pré-requisito

Antes de qualquer coisa, confirme que há Python 3 disponível:
```
python3 --version
```
Se o comando falhar (não encontrado), **pare e pergunte ao professor se quer instalar** (não instale sozinho sem confirmação — no Mac seria `brew install python3` ou o instalador oficial em python.org). Sem Python 3 os scripts desta skill não rodam.

## 1. Entrevista

Siga `references/entrevista.md` — 5 blocos curtos (Identificação, Conteúdo pedagógico, Avaliação, Cronograma, Regras/Bibliografia/Orientações), 2-3 perguntas por rodada, assert-then-confirm quando o contexto já sugerir a resposta. O Bloco 4 (Cronograma) é o que alimenta o cálculo — não pule nenhuma das 11 perguntas dele (inclui granularidade, formato de data, feriados como linha e 2ª chamada). O Bloco 3 (Avaliação) pergunta o tipo de disciplina (Certificadora/Internalizadora-Mobilizadora/Mista — decide a estrutura oficial da seção 3) e, se aplicável, o estilo visual — não assume nenhum dos dois. "Regras da Disciplina" **é opcional** — o template oficial da PUCPR não tem essa seção, o Bloco 1 pergunta se a Escola do professor exige (se sim, ela vira seção 6, deslocando Bibliografia/Orientações Gerais pra 7/8).

Monte um brief resumido (identificação, RAs e %, range de datas, nº de encontros) e **confirme com o professor antes de gerar qualquer arquivo**.

## 2. Cronograma

Depois de confirmado o brief, monte o JSON de entrada (formato documentado no topo de `scripts/gerar_cronograma.py`) com os dados do Bloco 4 — inclua `granularidade` (`"dia"`/`"semana"`/`"quinzena"`/`"mes"`), `formato_data` (`"dd_mm"` ou `"dd_mm_aaaa"`, só relevante se granularidade `"dia"`), `feriados_como_linha` (`true`/`false`) e `datas_2a_chamada` (lista, opcional) conforme as respostas do professor — e rode:
```
python3 scripts/gerar_cronograma.py dados_cronograma.json > cronograma.json
```
Leia os `avisos` do resultado (feriados não encontrados, temas insuficientes, TDE estourando a carga do RA) e resolva com o professor antes de seguir — não gere o documento final com aviso pendente sem avisar explicitamente que ficou uma lacuna.

## 3. Montar o documento

Monte `documento.json` (lista de blocos `titulo1`/`titulo2`/`paragrafo`/`tabela`, formato no topo de `scripts/gerar_docx.py`) seguindo a ordem de `assets/plano-template.md`, usando o `cronograma.json` gerado no passo anterior pra preencher a tabela da seção 5 — colunas **# | Data (ou Período, se granularidade ≠ "dia") | RA | Descrição das atividades pedagógicas | Carga horária** (`larguras: [5, 12, 8, 55, 20]`), usando os campos `indice`/`data`/`ra`/`descricao`/`carga_horaria_fmt` de cada linha do `cronograma.json` (não `carga_horaria` nem `data_iso`, que são só pro cálculo). Linha com `indice: null` entra com a célula `#` vazia. Se o professor pediu datas institucionais sem RA (Acolhida Cultural, Semana Acadêmica), insira essas linhas manualmente na posição cronológica certa, com `RA: "-"`.

A coluna `RA` do cronograma aceita múltiplos valores (`RA1, RA2`) ou o literal `Todos` pra linhas que não pertencem a um RA só (revisão, feedback) — ajuste manual, nenhum script gera isso sozinho.

Se o Bloco 1 confirmou que a Escola exige "Regras da Disciplina", inclua essa seção (usar o boilerplate documentado em `references/template-pucpr.md`) antes da Bibliografia, e ajuste a numeração dos títulos (Bibliografia vira 7, Orientações Gerais vira 8); senão, segue a numeração oficial (Bibliografia 6, Orientações Gerais 7).

Bibliografia: se o professor pediu lista numerada ou bullets (em vez de tabela), monte como sequência de blocos `"paragrafo"` com o número/bullet já no texto (`"1. Autor..."` ou `"• Autor..."`) em vez de um bloco `"tabela"`.

Orientações Gerais: use o texto literal de `references/template-pucpr.md`, não parafraseie.

Se estiver preenchendo o `.docx` oficial via `scripts/preencher_template.py` em vez de gerar do zero, o formato de entrada é diferente (`{"valores": {...}, "linhas_repetir": {...}}`, ver docstring do script) — os mesmos dados acima, só reorganizados pro formato de placeholder.

## 4. Exportar

Antes de gerar os arquivos finais, **pergunte onde salvar** — padrão `~/Desktop` se o professor não especificar outra pasta.

Caminho principal (template oficial, via `scripts/preencher_template.py`):
```
python3 scripts/preencher_template.py assets/template-oficial-tokenizado.docx dados_preenchimento.json "<pasta escolhida>/Plano de Ensino - <Disciplina>.docx"
```
Gera só `.docx` (com a arte institucional) — não existe conversor pra `.pdf` que preserve essa arte sem depender de LibreOffice (fora do escopo desta skill). Se o professor também quiser um `.pdf`, ofereça gerar via `gerar_pdf.py` a partir do mesmo `documento.json` — sai só texto/tabelas, sem a arte institucional.

Caminho de reserva (sem o template oficial, gera do zero):
```
python3 scripts/gerar_docx.py documento.json "<pasta escolhida>/Plano de Ensino - <Disciplina>.docx"
python3 scripts/gerar_pdf.py documento.json "<pasta escolhida>/Plano de Ensino - <Disciplina>.pdf"
```
Por padrão gera os dois formatos junto. Os dois vêm do mesmo `documento.json` (não é conversão de um pro outro) — o `.docx` é a fonte editável, o `.pdf` é pra distribuição/leitura.

Não commita/dá push no repo `skills-professores` sozinho — só se o professor pedir.

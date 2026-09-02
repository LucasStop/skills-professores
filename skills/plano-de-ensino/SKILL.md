---
name: plano-de-ensino
description: Monta o plano de ensino completo de uma disciplina universitária no template PUCPR "Percursos Formativos" (Ementa, Contexto da Disciplina, Competências/RA, Metodologia e Avaliação, Cronograma, Bibliografia, Orientações Gerais), calcula o cronograma automaticamente a partir de datas/RAs/dias de aula, e exporta .docx + .pdf prontos pra editar. Use quando o professor pedir "monta o plano de ensino de [disciplina]", "gera o cronograma da disciplina", "preciso montar/atualizar o plano de ensino", ou pedir pra recalcular o cronograma com novas datas. Não use pra criar uma skill nova do zero (isso é a `criar-skill-professor`).
metadata:
  repo: skills-professores
  template: percursos-formativos-pucpr-2026
---

# Plano de ensino

Gera o documento completo a partir de uma entrevista curta + um cálculo de cronograma, e exporta `.docx`+`.pdf` sem depender de nada instalado além do Python 3. Leia `references/template-pucpr.md` (estrutura das 8 seções, confirmada num plano real — Data Analytics/Marina de Lara, 2026/2 — inclui o texto literal da seção 8) e `references/entrevista.md` (roteiro completo de perguntas por bloco) antes de rodar o fluxo abaixo.

Se o professor já tiver (ou conseguir) o `.docx` editável oficial do template (com a arte institucional: faixa, selo, cores), **não gere do zero** — preencha os campos direto nesse arquivo (ver nota no fim de `references/template-pucpr.md`). Os scripts abaixo são o caminho pra quando esse arquivo ainda não existe.

## 0. Checagem de pré-requisito

Antes de qualquer coisa, confirme que há Python 3 disponível:
```
python3 --version
```
Se o comando falhar (não encontrado), **pare e pergunte ao professor se quer instalar** (não instale sozinho sem confirmação — no Mac seria `brew install python3` ou o instalador oficial em python.org). Sem Python 3 os scripts desta skill não rodam.

## 1. Entrevista

Siga `references/entrevista.md` — 5 blocos curtos (Identificação, Conteúdo pedagógico, Avaliação, Cronograma, Regras/Bibliografia/Orientações), 2-3 perguntas por rodada, assert-then-confirm quando o contexto já sugerir a resposta. O Bloco 4 (Cronograma) é o que alimenta o cálculo — não pule nenhuma das 9 perguntas dele (inclui formato de data e se feriados aparecem como linha). O Bloco 3 (Avaliação) não assume um layout único pra seção 3 nem uma forma única de apresentar % de RA — pergunta qual o professor quer, ver as variações em `references/template-pucpr.md`. No Bloco 5, a seção 6 (Regras da Disciplina) **não é opcional** — é seção padrão do template atual, só o número da Instrução Normativa e o contato da secretaria variam por escola.

Monte um brief resumido (identificação, RAs e %, range de datas, nº de encontros) e **confirme com o professor antes de gerar qualquer arquivo**.

## 2. Cronograma

Depois de confirmado o brief, monte o JSON de entrada (formato documentado no topo de `scripts/gerar_cronograma.py`) com os dados do Bloco 4 — inclua `formato_data` (`"dd_mm"` ou `"dd_mm_aaaa"`) e `feriados_como_linha` (`true`/`false`) conforme as respostas do professor — e rode:
```
python3 scripts/gerar_cronograma.py dados_cronograma.json > cronograma.json
```
Leia os `avisos` do resultado (feriados não encontrados, temas insuficientes, TDE estourando a carga do RA) e resolva com o professor antes de seguir — não gere o documento final com aviso pendente sem avisar explicitamente que ficou uma lacuna.

## 3. Montar o documento

Monte `documento.json` (lista de blocos `titulo1`/`titulo2`/`paragrafo`/`tabela`, formato no topo de `scripts/gerar_docx.py`) seguindo a ordem de `assets/plano-template.md`, usando o `cronograma.json` gerado no passo anterior pra preencher a tabela da seção 5 — colunas **# | Data | RA | Descrição das atividades pedagógicas | Carga horária** (`larguras: [5, 12, 8, 55, 20]`), usando os campos `indice`/`data`/`ra`/`descricao`/`carga_horaria_fmt` de cada linha do `cronograma.json` (não `carga_horaria` nem `data_iso`, que são só pro cálculo). Linha com `indice: null` entra com a célula `#` vazia. Se o professor pediu datas institucionais sem RA (Acolhida Cultural, Semana Acadêmica), insira essas linhas manualmente na posição cronológica certa, com `RA: "-"`.

A coluna `RA` do cronograma aceita múltiplos valores (`RA1, RA2`) ou o literal `Todos` pra linhas que não pertencem a um RA só (revisão, feedback) — ajuste manual, nenhum script gera isso sozinho.

Bibliografia (seção 7): se o professor pediu lista numerada ou bullets (em vez de tabela), monte como sequência de blocos `"paragrafo"` com o número/bullet já no texto (`"1. Autor..."` ou `"• Autor..."`) em vez de um bloco `"tabela"`.

Seção 8 (Orientações Gerais): use o texto literal de `references/template-pucpr.md`, não parafraseie.

## 4. Exportar

```
python3 scripts/gerar_docx.py documento.json "Plano de Ensino - <Disciplina>.docx"
python3 scripts/gerar_pdf.py documento.json "Plano de Ensino - <Disciplina>.pdf"
```
Por padrão gera os dois formatos junto. Os dois vêm do mesmo `documento.json` (não é conversão de um pro outro) — o `.docx` é a fonte editável, o `.pdf` é pra distribuição/leitura.

Não commita/dá push no repo `skills-professores` sozinho — só se o professor pedir.

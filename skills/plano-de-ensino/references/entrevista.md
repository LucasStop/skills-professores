# Entrevista — plano de ensino

Rodadas curtas (2-3 perguntas via `AskUserQuestion`), assert-then-confirm quando o contexto já sugerir a resposta. Uma rodada por bloco abaixo; só repete um bloco se a resposta deixar lacuna real. Ao final, monta um brief (resumo do que foi entendido) e confirma antes de gerar qualquer arquivo.

## Bloco 1 — Identificação
- Nome da disciplina, semestre (ex: "2026/2"), professor.
- Curso/Período/Turma/Turno — "Curso" é campo livre (Bacharelado, Tecnólogo, etc), não assumir Bacharelado por padrão.
- Carga horária, créditos, carga horária de extensão.
- Requisitos/código da disciplina, disciplinas pré-requisito e disciplinas beneficiadas depois (seção 2 — Contexto da Disciplina).
- **Se a Escola exige seção "Regras da Disciplina"**: o template oficial da PUCPR (7 seções) não tem essa seção, mas os 7 planos de referência (todos Escola Politécnica) sempre têm, como seção 6 — deslocando Bibliografia pra 7 e Orientações Gerais pra 8. Pergunta se a Escola do professor exige; se não souber, sugere que sim (é o padrão observado) mas confirma.

## Bloco 2 — Conteúdo pedagógico
- Ementa (parágrafo descritivo — pode ser rascunhado a partir de uma lista de tópicos que o professor der, e volta pra confirmação).
- Competências/Elementos de Competência e Resultados de Aprendizagem (RA) — quantos RAs, nome/descrição de cada um.
- Metodologia (expositiva, PjBL, TBL, estudo de caso, laboratório — pode ser mais de uma).
- Se quer incluir uma imagem/diagrama no fim da seção 3 (opcional — nos 7 planos mapeados, todos têm alguma imagem ali, mas só 2 rotulam como "Mapa Mental"; os outros a colocam sem título, e o conteúdo varia — mapa mental, diagrama de processo, até screenshot de aplicativo). Se sim, pergunta o título (ou "sem título") e o que ela representa; a skill não gera a imagem, só reserva o espaço/heading — o professor insere depois de aberto o .docx.

## Bloco 3 — Avaliação
- **Tipo de disciplina (seção 3)**: pergunta se é **Certificadora** (o Resultado de Aprendizagem É a própria competência — tabela oficial de 2 colunas: Resultado de Aprendizagem/Competência | Temas de Estudo), **Internalizadora/Mobilizadora** (tabela oficial de 5 colunas: Competência | Elementos de Competência | I/M | Temas de Estudo | RA — **padrão sugerido**, os 7 planos de referência são todos desse tipo) ou **Mista** (mantém as duas tabelas). Ver `template-pucpr.md` seção 3.
- Se Internalizadora/Mobilizadora ou Mista: **estilo visual** da tabela — 3 tabelas separadas (Temas de Estudo / Competências / RA, visto em 3 dos 7 planos de referência) ou tabela única de 5 colunas (visto nos outros 4) — mesma estrutura de dado, só apresentação diferente.
- Como cada RA compõe a nota final: % simples por RA, % por instrumento dentro do RA (com fórmula final), pontos absolutos somando 10, % embutido no rótulo do próprio RA (ex: "RA1... (30%)"), tabela dedicada "Avaliações Somativas" antes do cronograma, ou nenhuma fórmula (prosa vaga) — pergunta qual o professor quer, sem assumir uma única forma. Ver exemplos em `template-pucpr.md` seção 4/6.
- Critério de recuperação (2ª chamada, prazo, formato).

## Bloco 4 — Cronograma (o bloco com lógica de verdade — ver `scripts/gerar_cronograma.py`)
Perguntas objetivas, sem deixar implícito:
1. **Range de datas**: início e fim do período letivo (ex: "05/08/2026 a 05/12/2026").
2. **Dias de aula e carga horária de cada um**: quais dias da semana tem aula e quantas horas em cada — se for igual todo dia, uma resposta só; se variar (ex: terça 2h, quinta 2h), pedir por dia.
3. **Granularidade do cronograma**: o template oficial chama a coluna de "Período (dia, semana, quinzena ou mês)" — pergunta qual granularidade o professor quer: dia específico (**padrão sugerido**, é o que os 7 planos de referência usam), semana, quinzena ou mês. Se não for "dia", os encontros continuam calculados dia a dia por baixo dos panos (a % de cada RA não muda), mas as linhas do cronograma final agrupam os encontros do mesmo período — descrição soma os temas do bucket, carga horária soma as horas, e a coluna vira "Período" em vez de "Data". Vira `granularidade` em `dados.json`.
4. **Formato de data** (só relevante se granularidade = "dia"): `DD/MM` (padrão sugerido, sem ano) ou `DD/MM/AAAA` (com ano) — vira `formato_data` em `dados.json`.
5. **RAs e distribuição de tempo**: os RAs já vieram do Bloco 2 — agora pergunta o % (ou peso) de carga horária de cada um dentro do cronograma (ex: "RA1 30%, RA2 30%, RA3 40%"). Confirma que soma 100%.
6. **Temas por RA**: lista de temas/conteúdos de cada RA, na ordem que devem ser ensinados — vira a coluna "Descrição das atividades pedagógicas". Se a lista de temas for mais curta que o número de aulas calculado pro RA, a skill sinaliza a lacuna em vez de inventar conteúdo.
7. **TDE**: quantos TDEs por RA, carga horária de cada um, e se cada TDE tem uma descrição própria (ex: "Solicitação" e "Apresentação" como TDEs separados) em vez do rótulo genérico "TDE". A data exata de cada TDE fica em aberto ("[professor define a data]", sem número de sessão) — quem decide o dia é o professor, não a skill.
8. **Feriados nacionais no cronograma**: pergunta se o professor quer que apareçam como linha visível no cronograma (numerada, `RA: -`, carga horária do dia — não consome a meta de nenhum RA) ou fiquem omitidos (comportamento padrão atual). Vira `feriados_como_linha` em `dados.json`.
9. **Recessos/pontos facultativos institucionais** (não são feriado nacional — feriados nacionais entram sozinhos via BrasilAPI, não precisa perguntar a lista): pede se há alguma data assim conhecida no período (ex: recesso acadêmico da Semana Santa). Seguem o mesmo tratamento do item 8 (omitido ou linha visível, conforme a resposta anterior).
10. **Datas de 2ª chamada**: o template oficial exige (Art. 29, Resolução 414/2024) sinalizar no cronograma as datas previstas de avaliação de 2ª chamada — pergunta se há datas já conhecidas. Se a data cai num encontro já calculado, anota nele (`+ " [2ª Chamada]"`); se não cai em nenhum, entra como linha própria. Vira `datas_2a_chamada` em `dados.json`.
11. **Datas institucionais sem RA** (opcional): se o professor quiser marcar no cronograma datas fixas de atividades institucionais que não pertencem a nenhum RA (Acolhida Cultural, Semana Acadêmica, Feedback de notas finais) — entram na tabela com `RA: -`, inseridas manualmente na posição certa depois que `gerar_cronograma.py` monta a base (o calculador não sabe essas datas de antemão).

A tabela final tem 5 colunas: **# | Data (ou Período, se a granularidade não for "dia") | RA | Descrição das atividades pedagógicas | Carga horária** — `#` fica em branco nas linhas sem data fixa (TDE, recuperação estendida), `RA` vira `-` nas linhas institucionais/feriado, `Carga horária` sai em formato `HH:MM`. A coluna `RA` também aceita múltiplos valores (`RA1, RA2`, pra aula de revisão cobrindo mais de um RA) ou o literal `Todos` — ajuste manual ao montar `documento.json` a partir da saída de `gerar_cronograma.py`, o calculador não gera isso sozinho. Ver `template-pucpr.md` seção 5.

## Bloco 5 — Regras da disciplina, bibliografia e orientações gerais
- **Regras da Disciplina**: só entra como seção própria (nº 6) se o professor confirmou no Bloco 1 que a Escola exige — nesse caso, confirmar o número da Instrução Normativa de recuperação vigente e o contato da secretaria da escola/câmpus pra 2ª chamada (varia por escola — não assumir os valores de outra disciplina). O resto do texto (Diagnóstica/Formativa/Somativa/Recuperação/honestidade intelectual) é praticamente padrão — usar como boilerplate e só ajustar a fórmula da nota final. Se a Escola não exige, pula direto de Cronograma pra Bibliografia (numeração oficial de 7 seções).
- Bibliografia básica e complementar (título, autor — justificativa é opcional; lembrar que no template oficial essas referências normalmente já vêm do PPC/NDE do curso, o professor tende a colar texto existente em vez de compor do zero). Pergunta o formato preferido: tabela `Nº | Referência` (**padrão sugerido**), lista numerada, ou bullets — os dois últimos viram uma sequência de blocos `"paragrafo"` no `documento.json` (número/bullet já embutido no texto), sem precisar de tipo de bloco novo em `gerar_docx.py`/`gerar_pdf.py`. É a seção 6 (sem Regras da Disciplina) ou 7 (com). Ver `template-pucpr.md` seção 6.
- Orientações Gerais (seção 7 sem Regras da Disciplina, 8 com): usar o texto oficial literal de `template-pucpr.md` (declaração padrão de uso de IA + link) — só perguntar se o professor quer uma variação própria, não reescrever por padrão.

## Brief final
Antes de gerar o documento, resume: identificação, nº de RAs e % de cada, range de datas e dias de aula, nº de encontros calculado, se há lacunas sinalizadas (temas insuficientes, feriados não confirmados). Só gera depois de confirmado.

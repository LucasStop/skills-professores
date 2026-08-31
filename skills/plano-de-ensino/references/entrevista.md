# Entrevista — plano de ensino

Rodadas curtas (2-3 perguntas via `AskUserQuestion`), assert-then-confirm quando o contexto já sugerir a resposta. Uma rodada por bloco abaixo; só repete um bloco se a resposta deixar lacuna real. Ao final, monta um brief (resumo do que foi entendido) e confirma antes de gerar qualquer arquivo.

## Bloco 1 — Identificação
- Nome da disciplina, semestre (ex: "2026/2"), professor.
- Curso/Período/Turma/Turno.
- Carga horária, créditos, carga horária de extensão.
- Requisitos/código da disciplina, disciplinas pré-requisito e disciplinas beneficiadas depois (seção 2 — Contexto da Disciplina).

## Bloco 2 — Conteúdo pedagógico
- Ementa (parágrafo descritivo — pode ser rascunhado a partir de uma lista de tópicos que o professor der, e volta pra confirmação).
- Competências/Elementos de Competência e Resultados de Aprendizagem (RA) — quantos RAs, nome/descrição de cada um.
- Metodologia (expositiva, PjBL, TBL, estudo de caso, laboratório — pode ser mais de uma).
- Se usa Mapa Mental (seção 3.1, opcional).

## Bloco 3 — Avaliação
- Como cada RA compõe a nota final: % simples por RA, % por instrumento dentro do RA (com fórmula final), ou pontos absolutos somando 10 — ver exemplos em `template-pucpr.md` seção 4.
- Critério de recuperação (2ª chamada, prazo, formato).

## Bloco 4 — Cronograma (o bloco com lógica de verdade — ver `scripts/gerar_cronograma.py`)
Perguntas objetivas, sem deixar implícito:
1. **Range de datas**: início e fim do período letivo (ex: "05/08/2026 a 05/12/2026").
2. **Dias de aula e carga horária de cada um**: quais dias da semana tem aula e quantas horas em cada — se for igual todo dia, uma resposta só; se variar (ex: terça 2h, quinta 2h), pedir por dia.
3. **RAs e distribuição de tempo**: os RAs já vieram do Bloco 2 — agora pergunta o % (ou peso) de carga horária de cada um dentro do cronograma (ex: "RA1 30%, RA2 30%, RA3 40%"). Confirma que soma 100%.
4. **Temas por RA**: lista de temas/conteúdos de cada RA, na ordem que devem ser ensinados — vira a coluna "Descrição das atividades pedagógicas". Se a lista de temas for mais curta que o número de aulas calculado pro RA, a skill sinaliza a lacuna em vez de inventar conteúdo.
5. **TDE**: quantos TDEs por RA, carga horária de cada um. A data exata de cada TDE fica em aberto ("[professor define a data]", sem número de sessão) — quem decide o dia é o professor, não a skill.
6. **Recessos/pontos facultativos institucionais** (não são feriado nacional — feriados nacionais entram sozinhos via BrasilAPI, não precisa perguntar): pede se há alguma data assim conhecida no período (ex: recesso acadêmico da Semana Santa).
7. **Datas institucionais sem RA** (opcional): se o professor quiser marcar no cronograma datas fixas de atividades institucionais que não pertencem a nenhum RA (Acolhida Cultural, Semana Acadêmica, Feedback de notas finais) — entram na tabela com `RA: -`, inseridas manualmente na posição certa depois que `gerar_cronograma.py` monta a base (o calculador não sabe essas datas de antemão).

A tabela final tem 5 colunas: **# | Data | RA | Descrição das atividades pedagógicas | Carga horária** — `#` fica em branco nas linhas sem data fixa (TDE, recuperação estendida), `RA` vira `-` nas linhas institucionais, `Carga horária` sai em formato `HH:MM`. Ver `template-pucpr.md` seção 5.

## Bloco 5 — Regras da disciplina, bibliografia e orientações gerais
- **Regras da Disciplina (seção 6, padrão do template — não pular)**: confirmar o número da Instrução Normativa de recuperação vigente e o contato da secretaria da escola/câmpus pra 2ª chamada (varia por escola — não assumir os valores de outra disciplina). O resto do texto (Diagnóstica/Formativa/Somativa/Recuperação/honestidade intelectual) é praticamente padrão — usar como boilerplate e só ajustar a fórmula da nota final.
- Bibliografia básica e complementar (título, autor — justificativa é opcional).
- Orientações Gerais (seção 8): usar o texto oficial literal de `template-pucpr.md` (declaração padrão de uso de IA + link) — só perguntar se o professor quer uma variação própria, não reescrever por padrão.

## Brief final
Antes de gerar o documento, resume: identificação, nº de RAs e % de cada, range de datas e dias de aula, nº de encontros calculado, se há lacunas sinalizadas (temas insuficientes, feriados não confirmados). Só gera depois de confirmado.

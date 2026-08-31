# Fluxo de entrevista — detalhe por fase

Baseado no `skill-creator` oficial da Anthropic (github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md), simplificado: sem a fase de eval/benchmark com subagentes em paralelo — over-engineering pro tamanho normal de uma skill de professor. O que sobra é o núcleo que já funciona localmente na skill `impeccable`: entrevista em rodadas curtas, assert-then-confirm, brief como gate.

## Fase 1 — Capturar intenção

Regras de cadência (vale pra toda fase de pergunta neste fluxo):
- No máximo 2-3 perguntas por rodada. Não despeje um questionário inteiro de uma vez.
- **Assert-then-confirm, não menu com fuga**: quando o contexto já sugere uma resposta óbvia, afirme e peça confirmação/correção, não liste como se fosse uma escolha em aberto.
- Uma rodada é o padrão. Só faz uma segunda se a primeira deixar lacuna real.

Perguntas-base:
1. O que a skill deve fazer (tarefa docente concreta — "gerar X", "calcular Y", "revisar Z").
2. Gatilho — que pedido do professor deve acionar essa skill (vira a `description` do frontmatter).
3. Formato de saída — documento formatado (.docx/.pdf), planilha, texto solto, tabela markdown.

## Fase 2 — Entrevista e pesquisa leve

Se a tarefa gera um documento com estrutura institucional fixa (é o caso mais comum — plano de ensino, rubrica, ata, ficha de avaliação):
- Peça pelo menos 2-3 exemplos reais preenchidos antes de escrever qualquer instrução da skill.
- Extraia a estrutura comum (seções, campos, tabelas) e as variações entre os exemplos — variação não é ruído, é sinal de onde a skill precisa perguntar em vez de assumir.
- Pergunte especificamente sobre: campos opcionais (aparecem em uns exemplos e não em outros — a skill deve perguntar se usa ou não), qualquer cálculo/lógica embutida no documento (ex: cronograma calculado a partir de datas — não é preenchimento de texto, é lógica que merece um script), e dependências externas (a skill final vai precisar buscar algo de fora — calendário, API, arquivo local?).

Se a tarefa NÃO envolve documento com template fixo (ex: "revisa esse texto de prova e aponta ambiguidade"), pule a coleta de exemplos e vá direto pra perguntar critérios de sucesso — o que separa uma saída boa de uma ruim, pra guiar a instrução da skill.

## Fase 3 — Rascunho + brief

Anatomia padrão de uma skill (mesma convenção usada em `docx`, `pdf`, `council`, `impeccable` já instaladas localmente):
```
skills/<nome>/
  SKILL.md              # frontmatter (name = nome da pasta, description) + corpo
  references/            # markdown de apoio, carregado só quando o SKILL.md manda ler
  scripts/                # código executável (só quando há lógica de verdade, não pra prosa)
  assets/                 # templates de saída, dados estáticos
```
Regras de frontmatter: `name` até 64 caracteres, minúsculo, hífens, bate exatamente com o nome da pasta. `description` até 1024 caracteres, cobre o quê a skill faz E quando usar — é o único texto usado pra decidir se a skill dispara, então "pushy" é melhor que vago (cite explicitamente frases-gatilho).

Mantenha o `SKILL.md` enxuto (não precisa de limite rígido, mas se passar de ~300-400 linhas, é sinal de que parte do conteúdo devia estar em `references/`). O brief apresentado ao professor antes de escrever deve ter: o que a skill faz, quando dispara, e a árvore de arquivos proposta — nada além disso, é um resumo pra aprovação, não a skill inteira.

## Fase 4 — Empacotar

1. Escreve os arquivos em `skills/<nome>/` neste repo.
2. `mkdir -p ~/.claude/skills ~/.agents/skills` (idempotente, não falha se já existir).
3. `ln -s "$(pwd)/skills/<nome>" ~/.claude/skills/<nome>` e o equivalente em `~/.agents/skills/<nome>` — se o symlink já existir apontando pro mesmo lugar, não faz nada; se apontar pra outro lugar, avisa o professor antes de sobrescrever.
4. Acrescenta uma linha no `README.md` do repo descrevendo a skill nova.

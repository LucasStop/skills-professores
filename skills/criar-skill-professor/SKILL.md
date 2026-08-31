---
name: criar-skill-professor
description: Cria uma nova skill de IA pra automatizar uma tarefa docente (plano de ensino, rubrica, banco de questões, feedback de aluno, etc), entrevistando o professor sobre o que ela deve fazer, quando disparar e qual o formato de saída, e gerando o SKILL.md correspondente. Use quando o professor pedir "cria uma skill pra...", "monta uma automação pra...", "preciso de algo que gere [documento docente] automaticamente", ou quando quiser expandir o kit de skills-professores com uma nova tarefa. Não use pra rodar uma skill já existente (ex: "monta o plano de ensino de Cálculo" já dispara a skill `plano-de-ensino` direto, não esta).
metadata:
  repo: skills-professores
  type: meta-skill
---

# Criar skill pra professor

Gera uma nova skill dentro deste repo (`skills/<nome>/`) a partir de uma entrevista curta com o professor. Fluxo em 4 fases — cada uma é um gate, não avança sem a anterior fechar. Detalhe de cada fase em `references/fluxo-entrevista.md`.

## Fase 1 — Capturar intenção
Pergunte em uma rodada (2-3 perguntas via `AskUserQuestion`, não mais que isso de uma vez):
1. O que a skill deve permitir fazer (a tarefa docente concreta).
2. Quando ela deve disparar — que frases/pedidos do professor a acionam.
3. Qual o formato de saída esperado (documento .docx/.pdf? tabela? texto solto?).

Se o pedido já veio com esses três pontos claros na mensagem do professor, não pergunte de novo — confirme o que você entendeu (assert-then-confirm) e siga.

## Fase 2 — Entrevista e material de referência
Se a tarefa envolve gerar um documento com estrutura fixa (template institucional, formulário, rubrica padrão), peça exemplo(s) reais do professor ANTES de escrever qualquer instrução, e extraia a estrutura comum deles (ver `references/fluxo-entrevista.md` pro roteiro completo, incluindo perguntas de edge case: variações entre exemplos, campos opcionais, dependências externas).

## Fase 3 — Rascunho + brief
Monte o `SKILL.md` da nova skill (frontmatter `name`+`description` obrigatórios — description cobrindo o quê e quando usar, sem menção a "Anthropic"/"Claude"), mais `references/`/`scripts/`/`assets/` conforme a tarefa pedir. Apresente um brief resumido (o que a skill vai fazer, estrutura de arquivos proposta) e **pare** — a confirmação do professor é o gate antes de escrever qualquer arquivo de verdade.

## Fase 4 — Empacotar
Depois de confirmado:
1. Cria `skills/<nome>/` neste repo com os arquivos do brief.
2. Symlinka em `~/.claude/skills/<nome>` e `~/.agents/skills/<nome>` (cria `~/.agents/skills/` se não existir).
3. Atualiza o `README.md` do repo com uma linha descrevendo a skill nova.

Não commita/faz push sozinho — só se o professor pedir.

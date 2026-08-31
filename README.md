# skills-professores

Kit de skills de IA (formato aberto [Agent Skills / `SKILL.md`](https://agentskills.io)) pra apoiar professores universitários dentro e fora do período de aulas. Lido nativamente por Claude Code (`.claude/skills/`) e Codex CLI (`.agents/skills/`) sem tradução nenhuma — mesma pasta, dois symlinks.

## Skills

- **`skills/criar-skill-professor/`** — meta-skill: entrevista o professor sobre uma nova tarefa docente que ele quer automatizar, monta um brief, confirma, e gera a skill (`SKILL.md` + `references/`/`scripts/`/`assets/`) dentro deste repo.
- **`skills/plano-de-ensino/`** — primeira skill gerada. Monta o plano de ensino completo (template PUCPR "Percursos Formativos") a partir de uma entrevista curta, calcula o cronograma automaticamente (datas × RAs × feriados) e exporta `.docx` + `.pdf` com Python puro (sem instalar nada além do Python 3).

## Instalar localmente

```bash
mkdir -p ~/.claude/skills ~/.agents/skills
for skill in criar-skill-professor plano-de-ensino; do
  ln -s "$(pwd)/skills/$skill" ~/.claude/skills/$skill
  ln -s "$(pwd)/skills/$skill" ~/.agents/skills/$skill
done
```

Symlink, não cópia — editar a skill aqui atualiza os dois lados automaticamente.

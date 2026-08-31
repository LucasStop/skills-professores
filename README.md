# skills-professores

Kit de skills de IA (formato aberto [Agent Skills / `SKILL.md`](https://agentskills.io)) pra apoiar professores universitários dentro e fora do período de aulas. Lido nativamente por Claude Code (`.claude/skills/`) e Codex CLI (`.agents/skills/`) sem tradução nenhuma — mesma pasta, dois symlinks.

## Skills

- **`skills/criar-skill-professor/`** — meta-skill: entrevista o professor sobre uma nova tarefa docente que ele quer automatizar, monta um brief, confirma, e gera a skill (`SKILL.md` + `references/`/`scripts/`/`assets/`) dentro deste repo.
- **`skills/plano-de-ensino/`** — primeira skill gerada. Monta o plano de ensino completo (template PUCPR "Percursos Formativos") a partir de uma entrevista curta, calcula o cronograma automaticamente (datas × RAs × feriados) e exporta `.docx` + `.pdf` com Python puro (sem instalar nada além do Python 3).

## Instalar

Precisa de `git` e do Claude Code e/ou Codex CLI já instalados.

```bash
git clone https://github.com/LucasStop/skills-professores.git
cd skills-professores
./install.sh
```

Abra uma sessão nova do Claude Code ou do Codex CLI — as skills já aparecem disponíveis (peça algo como "monta o plano de ensino de [disciplina]", a skill dispara sozinha, ou invoque direto com `/plano-de-ensino`).

`install.sh` faz symlink (não cópia) de cada pasta em `skills/` pra `~/.claude/skills/` e `~/.agents/skills/`. É seguro rodar de novo a qualquer momento — depois de um `git pull`, ou depois que a `criar-skill-professor` gerar uma skill nova — sem duplicar nada.

**Windows**: symlink exige modo desenvolvedor habilitado (ou clonar com `git clone -c core.symlinks=true`). Se `install.sh` não rodar, copie as pastas de `skills/` manualmente pra `%USERPROFILE%\.claude\skills\` e `%USERPROFILE%\.agents\skills\` — só perde a atualização automática ao editar o repo.

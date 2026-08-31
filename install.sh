#!/usr/bin/env bash
# Instala (ou atualiza) os symlinks de todas as skills deste repo em
# ~/.claude/skills (Claude Code) e ~/.agents/skills (Codex CLI).
# Idempotente: pode rodar de novo a qualquer momento (ex: depois de um
# `git pull`, ou depois que a skill criar-skill-professor gerar uma nova
# skill dentro de skills/) sem duplicar nada.
set -e
cd "$(dirname "$0")"

mkdir -p ~/.claude/skills ~/.agents/skills

for pasta in skills/*/; do
  nome="$(basename "$pasta")"
  ln -sfn "$(pwd)/$pasta" ~/.claude/skills/"$nome"
  ln -sfn "$(pwd)/$pasta" ~/.agents/skills/"$nome"
  echo "instalado: $nome"
done

echo
echo "Pronto. Abra uma sessão nova do Claude Code ou do Codex CLI — as skills já aparecem disponíveis."

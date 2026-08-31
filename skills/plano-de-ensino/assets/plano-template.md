# Esqueleto do Plano de Ensino (template "Percursos Formativos")

Modelo de referência pra montar o `documento.json` (blocos `titulo1`/`titulo2`/`paragrafo`/`tabela`) que alimenta `scripts/gerar_docx.py` e `scripts/gerar_pdf.py`. Estrutura completa de cada seção em `../references/template-pucpr.md` (inclui o texto literal da seção 8).

```
[titulo1] <Disciplina>
[paragrafo] <Professor> · <Ano> – <Nº>º Semestre

[paragrafo] Escola/Câmpus: <...> · Curso: <...> · Período: <...> · Turma: <...> · Turno: <...>
[paragrafo] Carga Horária: <...> · Créditos: <...> · Carga Horária de Extensão: <...> · Requisitos: <...>

[titulo2] 1. Ementa
[paragrafo] <ementa>

[titulo2] 2. Contexto da Disciplina
[paragrafo ou tabela] <disciplinas precedentes recomendadas e disciplinas beneficiadas depois>

[titulo2] 3. Competência(s), Temas de Estudo e Resultados de Aprendizagem
[tabela] Nº | Descrição do tema  (Temas de Estudo)
[tabela] Nº C | Competência | Nº EC | Elementos de Competência | Classificação
[tabela] EC | Nº RA | Resultado de aprendizagem | Tema de estudo

[titulo2] 4. Alinhamento Construtivo: Metodologia e Avaliação
[tabela por RA] Resultado(s) de aprendizagem | Indicadores de Desempenho | Metodologia | Processos de avaliação e recuperação

[titulo2] 5. Cronograma de Atividades Pedagógicas
[tabela] # | Data | RA | Descrição das atividades pedagógicas | Carga horária
        <- gerado por scripts/gerar_cronograma.py, não preenchido à mão
[paragrafo] *O cronograma está sujeito a alterações conforme necessidade.

[titulo2] 6. Regras da Disciplina
[paragrafo] <texto introdutório remetendo à seção 4>
[paragrafo] Diagnóstica: ... / Formativa: ... / Somativa: ... / Recuperação ao longo do semestre: ... / Recuperação Estendida: ... / Nota da Disciplina: <fórmula>
[paragrafo] Segunda chamada: <resolução vigente + contato da secretaria da escola>
[paragrafo] Regras de entrega: meio de entrega, autoria, honestidade intelectual

[titulo2] 7. Bibliografia
[tabela] Nº | Referência  (7.1 Básica)
[tabela] Nº | Referência  (7.2 Complementar)

[titulo2] 8. Orientações Gerais
[paragrafo] 8.1 — texto literal da declaração de uso de IAGen (Resolução 274/2024 CONSUN) — ver template-pucpr.md
[paragrafo] 8.2 — link para documentos institucionais (avaliações, faltas, tratamento especial, Prêmio Marcelino Champagnat)
```

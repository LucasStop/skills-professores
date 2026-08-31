# Esqueleto do Plano de Ensino (template "Percursos Formativos")

Modelo de referência pra montar o `documento.json` (blocos `titulo1`/`titulo2`/`paragrafo`/`tabela`) que alimenta `scripts/gerar_docx.py` e `scripts/gerar_pdf.py`. Ver a estrutura completa de cada seção em `../references/template-pucpr.md`.

```
[titulo1] Plano de Ensino - <Disciplina> - <Semestre>

[paragrafo] <Escola/Câmpus> · <Curso> · <Período> · <Turma> · <Turno> · CH: <horas> · Créditos: <n>

[titulo2] 1. Ementa
[paragrafo] <ementa>

[titulo2] 2. Contexto da Disciplina
[paragrafo ou tabela] <pré-requisitos e disciplinas beneficiadas>

[titulo2] 3. Competência(s), Temas de Estudo e Resultados de Aprendizagem
[tabela] Competência/EC | I/M/Certifica | Tema de Estudo | RA

[titulo2] 4. Alinhamento Construtivo: Metodologia e Avaliação
[tabela] RA | Indicador de Desempenho | Metodologia | Processo de Avaliação/Recuperação
[paragrafo] <fórmula de composição da nota final, se houver>

[titulo2] 5. Cronograma de Atividades Pedagógicas
[tabela] Data | RA | Descrição das atividades pedagógicas | Carga horária
        <- gerado por scripts/gerar_cronograma.py, não preenchido à mão

[titulo2] 6. Bibliografia
[paragrafo] Básica: <itens>
[paragrafo] Complementar: <itens>

[titulo2] 7. Orientações Gerais
[paragrafo] <texto padrão sobre uso de IA Generativa — Resolução 274/2024 CONSUN — ou variação própria>
[paragrafo] <link para documentos institucionais>
```

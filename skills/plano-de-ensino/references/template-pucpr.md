# Template PUCPR "Percursos Formativos" (vigente desde 2026/1)

Estrutura mapeada a partir de planos de ensino reais (LGPD, DevOps, Design Patterns, Mobile Development Framework, Data Analytics, Especificação de Software, Back-End Cloud Computing, AI-Assisted Python, Big Data 2026/1, Análise e Design de Sistemas de Informação 2026/1). Rodapé constante: "Percursos Formativos - Centro de Ensino e Aprendizagem da PUCPR (2026)".

## Seções

### Cabeçalho / Identificação
Tabela: Escola/Câmpus, Curso, Período, Turma, Turno, Carga Horária, Créditos, Carga Horária de Extensão, Requisitos/Código. Nome da disciplina e do professor, semestre (ex: "2026/2").

### 1. Ementa
Parágrafo descritivo do que a disciplina cobre.

### 2. Contexto da Disciplina
Disciplinas pré-requisito e disciplinas beneficiadas depois. Formato varia: tabela formal (Código/Período/Nome), lista simples, ou texto corrido — depende do professor. Se a disciplina é eletiva/sem pré-requisito, vira uma nota genérica em vez de tabela.

### 3. Competência(s), Temas de Estudo e Resultados de Aprendizagem
Tabela: Competência/Elementos de Competência (EC), classificação I/M/Certifica (Internaliza/Mobiliza/Certifica), Temas de Estudo (TE), Resultados de Aprendizagem (RA).

**3.1 Mapa Mental** (opcional — template original tem a nota "(opcional - se não utilizar, retirar este item)"; perguntar ao professor se quer incluir).

### 4. Alinhamento Construtivo: Metodologia e Avaliação
Tabela cruzando RA → Indicadores de Desempenho (ID) → Metodologias/estratégias de ensino → Processos de avaliação e recuperação. É AQUI que entra a % (ou pontos) de cada RA na nota final — nunca dentro da tabela de cronograma (seção 5). Formatos observados: % simples por RA (ex. 50/50), % por instrumento dentro de cada RA com fórmula ponderada final (ex. `Nota = (35×RA1 + 65×RA2)/100`), ou pontos absolutos somando 10.

### 5. Cronograma de Atividades Pedagógicas
Tabela: Data | RA | Descrição das atividades pedagógicas | Carga horária. Ver `entrevista.md` e `scripts/gerar_cronograma.py` — essa seção é calculada, não preenchida à mão. TDE entra como linha própria dentro do bloco do RA correspondente, carga horária em formato `HH:MM` (ex. `04:00`).

### 6. Bibliografia
Básica e Complementar, cada item podendo ter uma justificativa curta de por que foi escolhido.

### 7. Orientações Gerais
Seção nova desta geração do template. Inclui texto padrão sobre uso de IA Generativa (cita a Resolução 274/2024 CONSUN — pedir ao professor se quer o texto padrão institucional ou uma variação própria) e link para documentos institucionais (faltas, tratamento especial, Prêmio Marcelino Champagnat).

## Nota sobre a geração anterior do template ("CrEAre", até 2025)

Planos de ensino de 2024/2025 seguem um template mais antigo (rodapé "CrEAre – Centro de Ensino e Aprendizagem da PUCPR"), com 10 seções incluindo "Acessibilidade" e "Adaptações para práticas profissionais" como itens separados (não existem mais na versão atual — foram incorporados/removidos em "Orientações Gerais"). A skill gera sempre no formato atual (Percursos Formativos); a geração antiga só é relevante se o professor pedir explicitamente pra consultar/migrar um plano legado.

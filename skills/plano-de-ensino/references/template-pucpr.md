# Template PUCPR "Percursos Formativos" (vigente desde 2026/1)

Duas fontes: o **template oficial vazio** ("Plano de ensino PUCPR - novo template (2026)", conseguido pelo usuário — a estrutura de fundo, com texto entre colchetes indicando o que é preenchido pelo NDE vs. pelo professor) e **7 planos reais preenchidos** (`references/planos-exemplo/`, todos Escola Politécnica, prof. Marina de Lara — usados pra ver como professores de fato preenchem/estilizam por cima da estrutura oficial). Rodapé constante em toda página: "Percursos Formativos - Centro de Ensino e Aprendizagem da PUCPR (2026)" + logo "creare".

**Identidade visual**: faixa decorativa no topo de cada página com círculos em tom de roxo/magenta sobre fundo bordô/pink, selo circular vermelho da PUCPR na capa, título "Pontifícia Universidade Católica do Paraná" e títulos de seção em roxo/magenta. `scripts/preencher_template.py` preenche esse `.docx` oficial preservando a arte; `scripts/gerar_docx.py`/`gerar_pdf.py` geram do zero (só texto/tabelas, sem a arte) quando não há o template oficial disponível.

## Capa
Nome da disciplina (grande), nome do professor, "AAAA – Nº Semestre" (ex: "2026 – 2º Semestre"). Logo abaixo, tabela: Escola/Câmpus, Curso, Período, Turma, Turno, Carga Horária, Créditos, Carga Horária de Extensão, Requisitos.

## 1. Ementa
Parágrafo descritivo do que a disciplina cobre.

## 2. Contexto da Disciplina
No template oficial vazio é só texto corrido — "[Texto construído pelo NDE do curso...]". Na prática, os planos reais formalizam isso em tabelas (Código | Disciplina): disciplinas precedentes recomendadas e disciplinas que a atual prepara/beneficia depois. Se não houver pré-requisito formal, vira um texto corrido ("Esta disciplina não possui pré-requisitos, porém é recomendado que o estudante tenha cursado..."). Variação vista em alguns planos: tabela de 3 colunas (Código | Período | Nome da disciplina) — ambas são válidas.

## 3. Competência(s), Temas de Estudo e Resultados de Aprendizagem
Conteúdo normalmente construído pelo NDE do curso (ajuste passa por eles, não é o professor que inventa). O template oficial define **2 tabelas mutuamente exclusivas por tipo de disciplina** (apaga a que não usa; disciplina mista mantém as duas):

**Disciplinas Internalizadoras e Mobilizadoras** (não certificam competência) — tabela de 5 colunas: Competência | Elementos de Competência | I/M (Internaliza/Mobiliza) | Temas de Estudo | Resultados de Aprendizagem.

**Disciplinas Certificadoras** (o Resultado de Aprendizagem É a própria competência a certificar) — tabela de 2 colunas: Resultado de Aprendizagem (Competência) | Temas de Estudo.

Os 7 planos reais mapeados são **todos do tipo Internalizadora/Mobilizadora** — nenhum exemplo real de Certificadora ainda (perguntar à Marina se ela tem algum, pra validar essa tabela). Dentro do tipo Internalizadora/Mobilizadora, o **estilo visual** varia por professor — mesma estrutura de dado, apresentação diferente:

| Disciplina | Estilo visual |
|---|---|
| Data Analytics, Inteligência Artificial, Raciocínio Algorítmico (Turma U) | 3 tabelas separadas: **Temas de Estudo** (Nº \| Descrição), **Competências** (Nº C \| Competência \| Nº EC \| Elementos de Competência \| classificação I/M/Certifica), **Resultados de Aprendizagem** (EC \| Nº RA \| descrição \| Tema de estudo) |
| Desenvolvimento de Carreira, Desenvolvimento de Jogos com Unreal, Raciocínio Algorítmico (Turma A), Resolução de Problemas Estruturados | Tabela única de 5 colunas (Competência \| Elementos de Competência \| I/M \| Temas de Estudo \| RA), igual à estrutura oficial |

- **Imagem/diagrama de fechamento** (opcional, template oficial diz literalmente "se não utilizar, retirar este item"): nos 7 planos mapeados, todos têm alguma imagem no fim da seção 3, mas só 2 (Data Analytics, Inteligência Artificial) rotulam como "Mapa Mental". Os outros 5 colocam a imagem direto, sem título, e o conteúdo varia — mapa mental, diagrama de processo (ex: pipeline ETL), até screenshot de aplicativo (Unreal). Não é convenção fixa da PUCPR, é escolha por professor — a entrevista pergunta se quer incluir, com que título (ou nenhum). A skill não gera a imagem em si, só reserva o espaço no documento.

## 4. Alinhamento Construtivo: Metodologia e Avaliação
Uma tabela por RA: Resultado(s) de aprendizagem | Indicadores de desempenho (IDx.y) | Metodologias/recursos/estratégias de ensino-aprendizagem | Processos de avaliação e recuperação de aprendizagem — este último detalha por tipo: `[Diagnóstica]`, `[Formativa]`, `[Somativa]`, `[Recuperação]` (ao longo do semestre e/ou estendida), cada um com o feedback e formato descritos.

**% de cada RA na nota final** aparece de formas diferentes conforme o professor — a entrevista (Bloco 3) pergunta qual usar, sem assumir uma única:
- % simples por RA, ou % por instrumento dentro do RA com fórmula ponderada final (`Nota = (35×RA1 + 65×RA2)/100`).
- Pontos absolutos somando 10 (ex: RA1 = 3 pontos, RA2 = 7 pontos).
- % embutido entre parênteses no próprio rótulo do RA dentro desta tabela (ex: `RA1. ... (30%)`), sem tabela/fórmula separada.
- Tabela dedicada **"Avaliações Somativas"** logo antes do cronograma: `RA | Somativa | Nota das atividades no RA | Nota do RA na nota semestral (%)`.
- Sem fórmula nenhuma — só prosa vaga ("Nota da Disciplina calculada a partir das atividades propostas").

## 5. Cronograma de Atividades Pedagógicas
No template oficial a coluna se chama **"Período (dia, semana, quinzena ou mês)"** — não "Data", e sem coluna "#". Os 7 planos reais, na prática, sempre usam dia específico com "Data" (`DD/MM`) + "#" numerado — por isso é o padrão sugerido da skill, mas a entrevista pergunta a granularidade (Bloco 4, item 3) porque o template oficial permite as outras.

Tabela com 5 colunas: **# | Data/Período | RA | Descrição das atividades pedagógicas | Carga horária**.
- `#`: número sequencial da sessão — **em branco** para linhas administrativas sem data de aula fixa (ex: "Semana de Recuperação Estendida").
- `Data` (granularidade "dia", padrão): formato brasileiro `DD/MM` (padrão sugerido, sem ano) ou `DD/MM/AAAA` (com ano) — confirmado na entrevista, vira `formato_data` em `dados.json`. Intervalo de datas (`DD/MM–DD/MM`, visto em 1 caso) não é gerado automaticamente — ajuste manual se o professor pedir.
- `Período` (granularidade "semana"/"quinzena"/"mês"): rótulo do bucket (ex: "Semana de 04/08 a 08/08") — a carga horária e a descrição da linha somam/agrupam os encontros daquele período; a matemática de % por RA não muda, só a apresentação.
- `RA`: `-` para atividades institucionais não ligadas a um RA específico (Acolhida Cultural, Semana Acadêmica, Feedback de notas) e para linhas de feriado. Também aceita múltiplos valores (`RA1, RA2`, aula que revisa mais de um RA) ou o literal `Todos` — ajuste manual, o calculador não gera isso sozinho.
- `Carga horária`: formato `HH:MM` (ex: `04:00`).
- **Feriados nacionais**: por padrão somem do cronograma (excluídos via BrasilAPI). Se o professor pedir (`feriados_como_linha: true` em `dados.json`), aparecem como linha normal numerada, `RA: -`, descrição `Feriado`, com a carga horária do dia — sem consumir a meta de nenhum RA.
- **2ª chamada** (exigência do template oficial, Art. 29 da Resolução 414/2024 CONSUN): as datas previstas devem estar sinalizadas no cronograma. Se caem num encontro já calculado, anota na descrição (`+ " [2ª Chamada]"`); se não, entram como linha própria. Vira `datas_2a_chamada` em `dados.json`.
- **TDE**: sinalizado com a sigla "TDE" antes da descrição, carga horária na coluna própria — template oficial menciona também "TDE integrado entre disciplinas" como caso possível (carga horária atribuída a ele mencionada igual).
- Linhas de avaliação somativa e datas institucionais (Acolhida Cultural, Semana Acadêmica) costumam vir destacadas com uma cor de fundo diferente nos planos reais — a skill não replica isso (cosmético, sem prejuízo de conteúdo).
- Nota de rodapé da tabela: `*O cronograma está sujeito a alterações conforme necessidade.`
- Ver `../scripts/gerar_cronograma.py` — essa seção é calculada, não preenchida à mão.

## Regras da Disciplina (seção opcional, fora do template oficial)
**Achado importante**: o template oficial vazio da PUCPR **não tem essa seção** — vai direto de Cronograma (5) pra Bibliografia (6) e Orientações Gerais (7). Mas os 7 planos reais mapeados (todos Escola Politécnica) **sempre a têm**, como seção 6 (deslocando Bibliografia pra 7, Orientações Gerais pra 8) — parece ser convenção adicionada pela Escola, não parte do template central. A entrevista (Bloco 1) pergunta se a Escola do professor exige.

Quando presente, estrutura fixa observada, com pequenas variações de escola/curso:
- Texto introdutório remetendo aos RAs/IDs/metodologia da seção 4.
- Lista com marcadores, negrito no rótulo: **Diagnóstica**, **Formativa**, **Somativa** (o que cada uma é e se compõe a nota), **Recuperação ao longo do semestre** (cita a Instrução Normativa vigente — conferir o número correto com o professor, ex: "01/2026" em Data Analytics), **Recuperação Estendida** (regras de nota mínima/máxima), **Nota da Disciplina** (fórmula, ex: `Nota = RA1 + RA2 + RA3` ou com pesos).
- **Segunda chamada**: cita a Resolução institucional vigente (ex: "414/2024") e o contato da secretaria da escola/câmpus responsável — **pedir ao professor o contato correto da sua escola**, não é o mesmo em todo curso.
- Regras de entrega: meio de entrega (AVA), autoria em atividades em grupo, honestidade intelectual.

## 6. Bibliografia (nº 7 se a disciplina tiver seção "Regras da Disciplina")
**Básica** e **Complementar** — no template oficial não há subseções numeradas (6.1/6.2), embora os planos reais costumem numerar (7.1/7.2). Referência completa (autor, título, edição, cidade, editora, ano, ISBN quando houver), em um de 3 formatos, confirmado na entrevista: tabela `Nº | Referência` (padrão sugerido), lista numerada, ou bullets — os últimos dois vistos com mais frequência nos planos reais mapeados. Template oficial: mínimo 3 títulos na Básica (priorizando biblioteca virtual) + 1 periódico; mínimo 5 na Complementar + 1 periódico. Igual à Ementa/Contexto/Competências, normalmente vem pronta do PPC/NDE do curso — o professor cola o texto existente.

## 7. Orientações Gerais (nº 8 se a disciplina tiver seção "Regras da Disciplina")
**Orientações para uso de Inteligência Artificial Generativa (IAGen)** — texto oficial, usar literal (só ajustar o número da resolução se a instituição atualizar):

> De acordo com a Resolução nº 274/2024 CONSUN, a utilização de ferramentas de Inteligência Artificial Generativa (IAGen) no ensino, aprendizagem e pesquisa da PUCPR deverá ocorrer de acordo com orientações explícitas do docente, que indicará quando, se e de que forma o uso pode acontecer. Ao utilizar qualquer ferramenta de IA, o estudante deve declarar explicitamente o uso, incluindo a seguinte declaração padrão nos materiais produzidos:
>
> "Durante a preparação deste [TIPO DE CONTEÚDO], o(s) autor(es) usaram [FERRAMENTA, VERSÃO] para [EXPLICITAR MOTIVOS]. Após usar essa ferramenta, o(s) autor(es) revisaram e editaram o conteúdo conforme necessário e assumem total responsabilidade pelo conteúdo."
>
> Clique aqui para acessar as Diretrizes para uso de IA (Inteligência Artificial) na PUCPR

**Link para documentos institucionais** sobre avaliações, faltas, tratamento especial, Prêmio Marcelino Champagnat e outros — texto padrão + link.

## Nota sobre a geração anterior do template ("CrEAre", até 2025)

Planos de ensino de 2024/2025 seguem um template mais antigo (rodapé "CrEAre – Centro de Ensino e Aprendizagem da PUCPR"), com seções e nomes diferentes (ex: "Acessibilidade" e "Adaptações para práticas profissionais" como itens separados, sem "Orientações Gerais"/IAGen). A skill gera sempre no formato atual (Percursos Formativos); a geração antiga só é relevante se o professor pedir explicitamente pra consultar/migrar um plano legado.

## Sobre o `.docx` editável oficial

Conseguido — "Plano de ensino PUCPR - novo template (2026)". Sem content controls nem comentários, só texto entre colchetes indicando o que o NDE/professor preenche. Fonte de verdade pra estrutura oficial (seções, nomes de coluna, tabelas de seção 3) documentada acima. Três arquivos em `assets/`:
- `assets/template-oficial-pucpr.docx` — o arquivo original, intocado (referência, e fonte se a PUCPR atualizar o template).
- `assets/template-oficial-tokenizado.docx` — o mesmo arquivo com os colchetes de instrução trocados por `{{PLACEHOLDER}}` (ver `scripts/limpar_template_oficial.py`), pronto pra `scripts/preencher_template.py` consumir. Roda a limpeza de novo só se o template oficial mudar.
- `scripts/preencher_template.py` preenche o tokenizado com os dados da entrevista, preservando a arte institucional (faixa, selo, cores, logo "creare") — via substituição de string no XML bruto, nunca reserializando a árvore inteira (ver docstring do script pro porquê).

`scripts/gerar_docx.py`/`gerar_pdf.py` continuam existindo como alternativa sem a arte institucional (só texto, tabelas e rodapé), útil se algum dia o `.docx` oficial não estiver disponível.

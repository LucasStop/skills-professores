# Template PUCPR "Percursos Formativos" (vigente desde 2026/1)

Estrutura confirmada lendo um plano oficial real e atual — Data Analytics (PJD117A, 2026/2, prof. Marina de Lara), mais os outros planos do semestre (LGPD, DevOps, Design Patterns, Mobile Development Framework, Especificação de Software, Back-End Cloud Computing, AI-Assisted Python) e os de 2026/1 (Big Data, Análise e Design de Sistemas de Informação). Rodapé constante em toda página: "Percursos Formativos - Centro de Ensino e Aprendizagem da PUCPR (2026)" + logo "creare".

**Identidade visual do template oficial** (relevante quando o professor tiver o `.docx` editável pra preencher direto nele — ver nota no fim): faixa decorativo no topo de cada página com círculos em tom de roxo/magenta sobre fundo bordô/pink, selo circular vermelho da PUCPR na capa, título "Pontifícia Universidade Católica do Paraná" e títulos de seção em roxo/magenta. Sem o arquivo editável, a skill gera um documento com a mesma estrutura de conteúdo mas sem essa arte institucional.

## Capa
Nome da disciplina (grande), nome do professor, "AAAA – Nº Semestre" (ex: "2026 – 2º Semestre"). Logo abaixo, tabela: Escola/Câmpus, Curso, Período, Turma, Turno, Carga Horária, Créditos, Carga Horária de Extensão, Requisitos.

## 1. Ementa
Parágrafo descritivo do que a disciplina cobre.

## 2. Contexto da Disciplina
Duas tabelas (Código | Disciplina): disciplinas precedentes recomendadas e disciplinas que a atual prepara/beneficia depois. Se não houver pré-requisito formal, vira um texto corrido ("Esta disciplina não possui pré-requisitos, porém é recomendado que o estudante tenha cursado..."). Variação vista em alguns planos: tabela de 3 colunas (Código | Período | Nome da disciplina) — ambas são válidas.

## 3. Competência(s), Temas de Estudo e Resultados de Aprendizagem
A skill pergunta na entrevista (Bloco 3) qual dos 3 layouts reais usar — não é sempre o mesmo entre disciplinas/professores:

**(a) 3 tabelas separadas** (padrão sugerido):
- Tabela **Temas de Estudo**: Nº (TE1, TE2...) | Descrição do tema.
- Tabela **Competências**: Nº C | Competência | Nº EC | Elementos de Competência | classificação (Internaliza/Mobiliza/Certifica, com legenda de cor amarelo/laranja/vermelho).
- Tabela **Resultados de Aprendizagem**: EC | Nº (RA1, RA2...) | Resultado de aprendizagem (descrição) | Tema de estudo (quais TEs cobre). Inclui indicação de qual RA tem "RA de Recuperação" ao longo do semestre.

**(b) Tabela única de 4 colunas**: Competência (com o Elemento de Competência mesclado no mesmo texto) | I/M (Internaliza/Mobiliza) | Temas de Estudo | RA.

**(c) Tabela única de 5 colunas**: Competência | Elemento de Competência (coluna própria) | I/M | Temas de Estudo | RA.

- **Imagem/diagrama de fechamento** (opcional): nos 7 planos mapeados, todos têm alguma imagem no fim da seção 3, mas só 2 (as duas da Marina — Data Analytics, Inteligência Artificial) rotulam como "Mapa Mental". Os outros 5 colocam a imagem direto, sem título, e o conteúdo varia — mapa mental, diagrama de processo (ex: pipeline ETL), até screenshot de aplicativo (Unreal). Não é convenção fixa da PUCPR, é escolha por professor — a entrevista pergunta se quer incluir, com que título (ou nenhum). A skill não gera a imagem em si, só reserva o espaço no documento.

## 4. Alinhamento Construtivo: Metodologia e Avaliação
Uma tabela por RA: Resultado(s) de aprendizagem | Indicadores de desempenho (IDx.y) | Metodologias/recursos/estratégias de ensino-aprendizagem | Processos de avaliação e recuperação de aprendizagem — este último detalha por tipo: `[Diagnóstica]`, `[Formativa]`, `[Somativa]`, `[Recuperação]` (ao longo do semestre e/ou estendida), cada um com o feedback e formato descritos.

**% de cada RA na nota final** aparece de formas diferentes conforme o professor — a entrevista (Bloco 3) pergunta qual usar, sem assumir uma única:
- % simples por RA, ou % por instrumento dentro do RA com fórmula ponderada final (`Nota = (35×RA1 + 65×RA2)/100`).
- Pontos absolutos somando 10 (ex: RA1 = 3 pontos, RA2 = 7 pontos).
- % embutido entre parênteses no próprio rótulo do RA dentro desta tabela (ex: `RA1. ... (30%)`), sem tabela/fórmula separada.
- Tabela dedicada **"Avaliações Somativas"** logo antes do cronograma: `RA | Somativa | Nota das atividades no RA | Nota do RA na nota semestral (%)`.
- Sem fórmula nenhuma — só prosa vaga ("Nota da Disciplina calculada a partir das atividades propostas").

## 5. Cronograma de Atividades Pedagógicas
Tabela com 5 colunas: **# | Data | RA | Descrição das atividades pedagógicas | Carga horária**.
- `#`: número sequencial da sessão — **em branco** para linhas administrativas sem data de aula fixa (ex: "Semana de Recuperação Estendida").
- `Data`: formato brasileiro `DD/MM` (padrão sugerido, sem ano) ou `DD/MM/AAAA` (com ano) — confirmado na entrevista, vira `formato_data` em `dados.json`. Intervalo de datas (`DD/MM–DD/MM`, visto em 1 caso) não é gerado automaticamente — ajuste manual se o professor pedir.
- `RA`: `-` para atividades institucionais não ligadas a um RA específico (Acolhida Cultural, Semana Acadêmica, Feedback de notas) e para linhas de feriado. Também aceita múltiplos valores (`RA1, RA2`, aula que revisa mais de um RA) ou o literal `Todos` — ajuste manual, o calculador não gera isso sozinho.
- `Carga horária`: formato `HH:MM` (ex: `04:00`).
- **Feriados nacionais**: por padrão somem do cronograma (excluídos via BrasilAPI). Se o professor pedir (`feriados_como_linha: true` em `dados.json`), aparecem como linha normal numerada, `RA: -`, descrição `Feriado`, com a carga horária do dia — sem consumir a meta de nenhum RA. Comportamento visto nos planos reais mais recentes.
- Linhas de avaliação somativa e datas institucionais (Acolhida Cultural, Semana Acadêmica) costumam vir destacadas com uma cor de fundo diferente — a skill não replica isso (cosmético, sem prejuízo de conteúdo).
- Nota de rodapé da tabela: `*O cronograma está sujeito a alterações conforme necessidade.`
- Ver `../scripts/gerar_cronograma.py` — essa seção é calculada, não preenchida à mão.

## 6. Regras da Disciplina
**Seção padrão do template atual, não opcional** (aparece em Data Analytics, LGPD e outros planos 2026 — versões antigas do template a omitiam ou variavam o nome). Estrutura fixa, com pequenas variações de escola/curso:
- Texto introdutório remetendo aos RAs/IDs/metodologia da seção 4.
- Lista com marcadores, negrito no rótulo: **Diagnóstica**, **Formativa**, **Somativa** (o que cada uma é e se compõe a nota), **Recuperação ao longo do semestre** (cita a Instrução Normativa vigente — conferir o número correto com o professor, ex: "01/2026" em Data Analytics), **Recuperação Estendida** (regras de nota mínima/máxima), **Nota da Disciplina** (fórmula, ex: `Nota = RA1 + RA2 + RA3` ou com pesos).
- **Segunda chamada**: cita a Resolução institucional vigente (ex: "414/2024") e o contato da secretaria da escola/câmpus responsável — **pedir ao professor o contato correto da sua escola**, não é o mesmo em todo curso.
- Regras de entrega: meio de entrega (AVA), autoria em atividades em grupo, honestidade intelectual.

## 7. Bibliografia
**7.1 Básica** e **7.2 Complementar** — referência completa (autor, título, edição, cidade, editora, ano, ISBN quando houver), em um de 3 formatos, confirmado na entrevista: tabela `Nº | Referência` (padrão sugerido), lista numerada, ou bullets — os últimos dois vistos com mais frequência nos planos reais mapeados.

## 8. Orientações Gerais
**8.1 Orientações para uso de Inteligência Artificial Generativa (IAGen)** — texto oficial, usar literal (só ajustar o número da resolução se a instituição atualizar):

> De acordo com a Resolução nº 274/2024 CONSUN, a utilização de ferramentas de Inteligência Artificial Generativa (IAGen) no ensino, aprendizagem e pesquisa da PUCPR deverá ocorrer de acordo com orientações explícitas do docente, que indicará quando, se e de que forma o uso pode acontecer. Ao utilizar qualquer ferramenta de IA, o estudante deve declarar explicitamente o uso, incluindo a seguinte declaração padrão nos materiais produzidos:
>
> "Durante a preparação deste [TIPO DE CONTEÚDO], o(s) autor(es) usaram [FERRAMENTA, VERSÃO] para [EXPLICITAR MOTIVOS]. Após usar essa ferramenta, o(s) autor(es) revisaram e editaram o conteúdo conforme necessário e assumem total responsabilidade pelo conteúdo."
>
> Clique aqui para acessar as Diretrizes para uso de IA (Inteligência Artificial) na PUCPR

**8.2 Link para documentos institucionais** sobre avaliações, faltas, tratamento especial, Prêmio Marcelino Champagnat e outros — texto padrão + link.

## Nota sobre a geração anterior do template ("CrEAre", até 2025)

Planos de ensino de 2024/2025 seguem um template mais antigo (rodapé "CrEAre – Centro de Ensino e Aprendizagem da PUCPR"), com seções e nomes diferentes (ex: "Acessibilidade" e "Adaptações para práticas profissionais" como itens separados, sem "Orientações Gerais"/IAGen). A skill gera sempre no formato atual (Percursos Formativos); a geração antiga só é relevante se o professor pedir explicitamente pra consultar/migrar um plano legado.

## Sobre o `.docx` editável oficial

Se o professor conseguir o arquivo `.docx` editável do template (com a arte institucional — faixa, selo, cores, logo "creare"), a forma correta de usar é abrir esse arquivo e substituir só o conteúdo dos campos/tabelas nele (reaproveitando o padrão `unpack.py`/`pack.py` da skill `docx` local), não gerar do zero — preserva a identidade visual real sem reconstruir manualmente. Enquanto esse arquivo não existir, `scripts/gerar_docx.py`/`gerar_pdf.py` geram um documento com a mesma estrutura de conteúdo, mas sem a arte institucional (só texto, tabelas e rodapé).

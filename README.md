# MeetingCenter

O **MeetingCenter** é um worker de background que automatiza a geração de atas de reuniões do Microsoft Teams.

**Objetivo:** A cada 10 minutos ele consulta a Microsoft Graph API, identifica reuniões do dia que possuem transcrição disponível, gera uma ata estruturada usando Azure OpenAI (GPT-4o), e persiste o resultado no PostgreSQL.

**Aplicação:** Esses dados são consumidos por um dashboard, onde cada usuário tem permissão de listar, consultar e compartilhar o resumo/análise das reuniões as quais ele foi o organizador ou participou.

**Fluxo de funcionamento:**

1. O worker SAQ dispara `batch_call_transcript` a cada 10 minutos via cron.
2. Ele busca todos os `callRecords` do dia atual na Graph API.
3. Filtra apenas chamadas em grupo (`groupCall`) organizadas por usuários do tenant, descartando as que já estão no banco.
4. Para cada chamada válida, verifica se existe transcrição disponível via `getAllTranscripts`.
5. Baixa o arquivo VTT da transcrição, parseia as falas por participante e agrupa falas consecutivas do mesmo speaker.
6. Enriquece os dados com lista de convidados (via evento de calendário) e participantes reais (via `callRecords/participants_v2`).
7. Envia o transcript enriquecido ao GPT-4o com structured output, que devolve um JSON com `goal` (objetivo da reunião), `topics` (temas tratados) e `tasks` (compromissos assumidos com prazos).
8. Salva tudo na tabela `portal_reunioes` do PostgreSQL: metadados da reunião, participantes, convidados, ata gerada e transcript bruto.

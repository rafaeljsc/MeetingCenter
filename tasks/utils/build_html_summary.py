import re
from pathlib import Path

import pandas as pd


def build_html_summary(data: dict, img_header: str) -> Path:
    """Converte o json da ata gerada por IA em html.

    Args:
      data (dict): Json da ata gerada pela IA.
      img_header (str): Link da imagem a ser exibida no topo do html
    """

    raw_transcript = data.get("raw_transcript")
    txt_transcript = ""
    for item in raw_transcript:
        user = next(iter(item))
        txt = next(iter(item.values()))
        txt_transcript += f"<p><b>{user}</b>: {txt}</p>"

    participants_name = data.get("participants_name", []) or []
    participants_mail = data.get("participants_mail", []) or []
    participants = [
        {
            "Nome": participants_name[participants_mail.index(i)],
            "E-mail": i,
            "Empresa": i.split("@")[1].split(".")[0].title(),
        }
        for i in participants_mail
    ]

    df_participants = pd.DataFrame(participants)

    tasks = data.get("tasks", []) or []
    topics = data.get("topics", []) or []

    df_tasks = pd.DataFrame(tasks).rename(
        columns={
            "owner": "Responsável",
            "task": "Tarefa",
            "due_date": "Prazo",
        },
    )

    df_tasks.drop(columns="company", inplace=True)  # noqa: PD002

    df_topics = pd.DataFrame(topics).rename(
        columns={
            "topic": "Tópico",
            "content": "Conteúdo",
        },
    )

    if "Prazo" in df_tasks.columns:
        df_tasks["Prazo"] = df_tasks["Prazo"].replace("N/A", "—").fillna("—")
    else:
        df_tasks["Prazo"] = "—"

    def df_to_editable_table(df: pd.DataFrame, table_id: str) -> str:
        if df.empty:
            return "<p><i>Nenhum dado disponível.</i></p>"
        df = df.copy()
        df["Remover"] = '<span class="remove-btn" onclick="removeRow(this)">✖</span>'
        cols = df.columns.tolist()
        header_cells = "".join(f"<th>{col}</th>" for col in cols[:-1])
        header_cells += '<th class="remove-col">Remover</th>'
        body_rows = []
        for _, row in df.iterrows():
            cells = "".join(f'<td><div contenteditable="true">{row.get(col, "")}</div></td>' for col in cols[:-1])
            remove_cell = f'<td class="remove-col">{row["Remover"]}</td>'
            body_rows.append(f"<tr>{cells}{remove_cell}</tr>")
        rows_html = "".join(body_rows)
        return f"""
    <table id="{table_id}">
        <thead><tr>{header_cells}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    <button onclick="addRow('{table_id}')">Adicionar Linha</button>
    """

    call_title = data.get("call_title", "")
    start_date = data.get("start_date", "").strftime("%d/%m/%Y, %H:%M")
    end_date = data.get("end_date", "").strftime("%d/%m/%Y, %H:%M")
    call_duration_min = data.get("call_duration_min", "")
    call_duration = (
        f"{call_duration_min}min"
        if call_duration_min / 60 <= 1
        else f"{int(call_duration_min / 60)}h{(call_duration_min % 60)}min"
    )
    organizer = data.get("organizer", "")
    participants_count = data.get("participants_count", "")
    invites_count = data.get("invites_count", "")
    companies = ", ".join(data.get("companies", []))
    goal = data.get("goal", "")

    style = f"""
<style>
    :root {{
    --primary: #00a88e;
    --secondary: #4b4b4b;
    --accent: #f5f7f8;
    --danger: #c0392b;
    --font: "Segoe UI", Roboto, Arial, sans-serif;
    }}
    body {{
    font-family: var(--font);
    color: #212529;
    margin: 0;
    background-color: #fff;
    }}
    header {{
    background-color: #e9f7f5;
    background-image: url('{img_header}');
    background-size: 50%;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    height: 140px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px 0;
    }}
    main {{
    max-width: 950px;
    margin: 40px auto;
    padding: 0 20px;
    }}
    h1, h2 {{
    color: var(--primary);
    border-bottom: 2px solid var(--accent);
    padding-bottom: 6px;
    margin-top: 30px;
    }}
    ul {{
    list-style: none;
    padding: 0;
    }}
    li {{
    margin-bottom: 6px;
    }}
    table {{
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    font-size: 14px;
    }}
    th, td {{
    border: 1px solid #dee2e6;
    padding: 10px 12px;
    vertical-align: top;
    }}
    th {{
    background-color: var(--accent);
    color: var(--primary);
    font-weight: 600;
    text-transform: uppercase;
    font-size: 13px;
    }}
    td div[contenteditable] {{
    outline: none;
    }}
    .remove-btn {{
    cursor: pointer;
    color: var(--danger);
    font-weight: bold;
    }}
    button {{
    background-color: var(--primary);
    color: white;
    border: none;
    padding: 8px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-family: var(--font);
    font-size: 13px;
    margin: 6px 8px 20px 0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    transition: all 0.2s ease;
    }}
    button:hover {{
    background-color: #008f7a;
    transform: translateY(-1px);
    }}
    .hide-remove th.remove-col,
    .hide-remove td.remove-col {{
    display: none;
    }}
    p i {{
    color: var(--secondary);
    }}
    footer {{
    text-align: center;
    margin: 60px 0 30px;
    font-size: 12px;
    color: var(--secondary);
    }}
    .modal {{
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0; top: 0; width: 100%; height: 100%;
        background-color: rgba(0,0,0,0.6);
    }}
    .modal-content {{
        background-color: #fff;
        margin: 5% auto;
        padding: 20px;
        border-radius: 8px;
        width: 80%;
        max-width: 850px;
        max-height: 80vh;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: monospace;
        font-size: 13px;
        position: relative;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }}
    .close-modal {{
        float: right;
        font-size: 24px;
        font-weight: bold;
        cursor: pointer;
        color: var(--secondary);
    }}
    .transcript-link {{
        color: var(--primary);
        text-decoration: underline;
        cursor: pointer;
    }}
    @media print {{
    button, .remove-btn, .transcript-link, .modal {{
        display: none !important;
    }}
    header {{
        background-size: 40%;
        background-position: center center;
        height: 100px;
    }}
    }}
</style>
"""

    script = """
<script>
    function removeRow(btn) { btn.closest('tr').remove(); }
    function addRow(tableId) {
        const table = document.getElementById(tableId);
        const newRow = table.insertRow(-1);
        const colCount = table.rows[0].cells.length;
        for (let i = 0; i < colCount; i++) {
            const cell = newRow.insertCell(i);
            if (table.rows[0].cells[i].classList.contains('remove-col')) {
                cell.className = 'remove-col';
                cell.innerHTML = '<span class="remove-btn" onclick="removeRow(this)">✖</span>';
            } else {
                cell.innerHTML = '<div contenteditable="true"></div>';
            }
        }
    }
    function toggleRemoveColumns() {
        document.querySelectorAll('table').forEach(t => t.classList.toggle('hide-remove'));
    }
    function openTranscript() { document.getElementById('transcriptModal').style.display = 'block'; }
    function closeTranscript() { document.getElementById('transcriptModal').style.display = 'none'; }
    window.onclick = function(event) {
        let modal = document.getElementById('transcriptModal');
        if (event.target == modal) modal.style.display = 'none';
    }
    window.onbeforeprint = () => document.querySelectorAll('table').forEach(t => t.classList.add('hide-remove'));
    window.onafterprint = () => document.querySelectorAll('table').forEach(t => t.classList.remove('hide-remove'));
</script>
"""

    html = f"""
<html lang="pt-BR">
    <head>
    <meta charset="utf-8">
    <title>{call_title}</title>
    {style}
    </head>
    <body>
    <header></header>
    <main>
        <button onclick="toggleRemoveColumns()">Mostrar/Ocultar coluna de remoção</button>

        <h2>Detalhes da Reunião</h2>
        <ul>
            <li><strong>Título:</strong> <span contenteditable="true">{call_title}</span></li>
            <li><strong>Início:</strong> <span contenteditable="true">{start_date}</span></li>
            <li><strong>Término:</strong> <span contenteditable="true">{end_date}</span></li>
            <li><strong>Duração:</strong> <span contenteditable="true">{call_duration}</span></li>
            <li><strong>Organizador:</strong> <span contenteditable="true">{organizer}</span></li>
            <li><strong>Total de Convidados:</strong> <span contenteditable="true">{invites_count}</span></li>
            <li><strong>Total de Participantes:</strong> <span contenteditable="true">{participants_count}</span></li>
            <li><strong>Empresas:</strong> <span contenteditable="true">{companies}</span></li>
            <li><strong>Transcrição:</strong> <span class="transcript-link" onclick="openTranscript()">Clique aqui</span></li>
        </ul>

        <h2>Objetivo</h2>
        <p contenteditable="true">{goal}</p>

        <h2>Participantes</h2>
        {df_to_editable_table(df_participants, "tabela_participantes")}

        <h2>Temas Tratados</h2>
        {df_to_editable_table(df_topics, "tabela_temas")}

        <h2>Compromissos</h2>
        {df_to_editable_table(df_tasks, "tabela_compromissos")}

        <footer>
        <p><i>Documento gerado automaticamente pelo sistema de atas corporativas.</i></p>
        </footer>

        <div id="transcriptModal" class="modal">
            <div class="modal-content">
                <span class="close-modal" onclick="closeTranscript()">&times;</span>
                <h3 style="color: var(--primary); margin-top: 0;">Transcrição Completa</h3>
                <hr style="border: 0; border-top: 1px solid var(--accent); margin-bottom: 15px;">
                <div>{txt_transcript}</div>
            </div>
        </div>
    </main>
    {script}
    </body>
</html>
"""
    output = Path(re.sub(r'[<>:"/\\|?*]', "_", f"{data['call_title']}.html"))
    output.write_text(html, encoding="utf-8")
    return output

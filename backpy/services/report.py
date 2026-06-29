# services/report.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.units import mm
from io import BytesIO
from datetime import datetime

def generate_practice_pdf(practice_id, question_text, transcription, code, evaluation, language='python', extra_meta=None):
    """
    Gera um PDF em memória e retorna bytes (BytesIO).
    evaluation: dict com text_scores, code_info, code_score, final_score, feedback (lista)
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    heading = styles['Heading1']
    small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9)

    flow = []

    # Header
    title = Paragraph("Relatório de Avaliação — PrepWise", heading)
    flow.append(title)
    flow.append(Spacer(1, 6))

    meta_text = f"<b>Prática ID:</b> {practice_id} &nbsp;&nbsp; <b>Data:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if extra_meta:
        meta_text += f" &nbsp;&nbsp; <b>Info:</b> {extra_meta}"
    flow.append(Paragraph(meta_text, small))
    flow.append(Spacer(1, 12))

    # Questão
    flow.append(Paragraph("<b>Questão</b>", styles['Heading3']))
    flow.append(Spacer(1, 4))
    flow.append(Paragraph(question_text or "—", normal))
    flow.append(Spacer(1, 8))

    # Transcrição
    flow.append(Paragraph("<b>1. Transcrição</b>", styles['Heading4']))
    flow.append(Spacer(1, 4))
    flow.append(Preformatted(transcription or "—", normal))
    flow.append(Spacer(1, 8))

    # Código
    flow.append(Paragraph("<b>2. Código enviado</b>", styles['Heading4']))
    flow.append(Spacer(1, 4))
    flow.append(Preformatted(code or "—", normal))
    flow.append(Spacer(1, 8))

    # Avaliação
    flow.append(Paragraph("<b>3. Avaliação automática</b>", styles['Heading4']))
    flow.append(Spacer(1, 4))
    # text scores
    text_scores = evaluation.get('text_scores', {}) if evaluation else {}
    flow.append(Paragraph(f"<b>Conteúdo técnico:</b> {text_scores.get('content', '-')} / 4", normal))
    flow.append(Paragraph(f"<b>Clareza:</b> {text_scores.get('clarity', '-')} / 4", normal))
    flow.append(Paragraph(f"<b>Palavras-chave encontradas:</b> {text_scores.get('found_keywords', 0)} / {text_scores.get('total_keywords', 0)}", normal))
    flow.append(Spacer(1, 6))
    code_info = evaluation.get('code_info', {}) if evaluation else {}
    flow.append(Paragraph(f"<b>Lint / issues:</b> {code_info.get('total_issues', code_info.get('heuristic_issues', '-'))}", normal))
    flow.append(Paragraph(f"<b>Nota do código:</b> {evaluation.get('code_score', '-') if evaluation else '-'} / 4", normal))
    flow.append(Paragraph(f"<b>Nota final:</b> {evaluation.get('final_score', '-') if evaluation else '-'}", normal))
    flow.append(Spacer(1, 8))

    # Feedback textual
    flow.append(Paragraph("<b>4. Feedback</b>", styles['Heading4']))
    flow.append(Spacer(1, 4))
    feedback_list = evaluation.get('feedback', []) if evaluation else []
    if feedback_list:
        for item in feedback_list:
            flow.append(Paragraph(f"• {item}", normal))
            flow.append(Spacer(1, 2))
    else:
        flow.append(Paragraph("—", normal))
    flow.append(Spacer(1, 12))

    # Observações
    flow.append(Paragraph("<b>Observações</b>", styles['Heading4']))
    flow.append(Spacer(1, 4))
    flow.append(Paragraph("Relatório gerado automaticamente pelo MVP do PrepWise.", small))

    doc.build(flow)
    buffer.seek(0)
    return buffer

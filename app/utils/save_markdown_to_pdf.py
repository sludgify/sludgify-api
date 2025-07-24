import markdown
from weasyprint import HTML
import io


def save_markdown_to_pdf(responses):
    html_content = markdown.markdown(responses)
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(target=pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

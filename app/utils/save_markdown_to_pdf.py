import markdown
from weasyprint import HTML
import io


def save_markdown_to_pdf(responses):
    combined_text = "\n\n".join(resp.text for resp in responses)
    html_content = markdown.markdown(combined_text)
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(target=pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

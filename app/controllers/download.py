from flask import send_from_directory
import os
from .. import app


class DownloadController:
    def __init__(self):
        pass

    async def download_report(self):
        return send_from_directory(
            os.path.join(app.static_folder, "pdf"),
            "Sludge_Disclosure_Report_by_Sludgify.pdf",
            as_attachment=True,
        )

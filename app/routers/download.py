from flask import Blueprint
from ..controllers import DownloadController

download_router = Blueprint("download_router", __name__)
download_controller = DownloadController()


@download_router.route("/download/sludgify/report")
async def download_report():
    return await download_controller.download_report()

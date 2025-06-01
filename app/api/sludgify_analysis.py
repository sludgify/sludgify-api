from flask import Blueprint, request
from ..utils import jwt_required
from ..controllers import SludgifyAnalysisController

sludgify_analysis_router = Blueprint("sludgify_analysis_router", __name__)


@sludgify_analysis_router.get("/sludgify/analysis/total-sludge")
@jwt_required()
async def total_sludge():
    user = request.user
    return await SludgifyAnalysisController.total_sludge(user)


@sludgify_analysis_router.get("/sludgify/analysis/emission-reductions")
@jwt_required()
async def emission_reductions():
    user = request.user
    return await SludgifyAnalysisController.emission_reductions(user)


@sludgify_analysis_router.get("/sludgify/analysis/project-completed")
@jwt_required()
async def project_completed():
    user = request.user
    return await SludgifyAnalysisController.project_completed(user)


@sludgify_analysis_router.get("/sludgify/analysis/management-summary")
@jwt_required()
async def management_summary():
    user = request.user
    return await SludgifyAnalysisController.management_summary(user)


@sludgify_analysis_router.get("/sludgify/analysis/emission-comparison")
@jwt_required()
async def emission_comparison():
    user = request.user
    return await SludgifyAnalysisController.emission_comparison(user)

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.applications import router as applications_router
from app.api.v1.cover_letters import router as cover_letters_router
from app.api.v1.interviews import router as interviews_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.ai import router as ai_router
from app.api.v1.admin import router as admin_router
from app.api.v1.matching import router as matching_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(resumes_router, prefix="/resumes", tags=["Resumes"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(matching_router, prefix="/matching", tags=["Matching / Dashboard"])
api_router.include_router(applications_router, prefix="/applications", tags=["Applications"])
api_router.include_router(cover_letters_router, prefix="/cover-letters", tags=["Cover Letters"])
api_router.include_router(interviews_router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])

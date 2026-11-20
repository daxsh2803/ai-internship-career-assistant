
from fastapi import APIRouter

from app.api.v1.endpoints import applications, auth, jobs, profiles, resume

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router)
api_v1_router.include_router(profiles.router)
api_v1_router.include_router(resume.router)
api_v1_router.include_router(jobs.router)
api_v1_router.include_router(applications.router)

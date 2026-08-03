import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.services.incident_service.app.api.routes import router as incident_router, evidence_router
from backend.services.shared.exceptions import sentinel_exception_handler, SentinelException
from backend.services.shared.config import settings

app = FastAPI(
    title="Sentinel AI - Incident Service",
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(SentinelException, sentinel_exception_handler)

app.include_router(incident_router, prefix="/api/v1")
app.include_router(evidence_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("backend.services.incident_service.main:app", host="0.0.0.0", port=8003, reload=True)

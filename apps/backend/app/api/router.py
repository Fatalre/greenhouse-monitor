from fastapi import APIRouter

from app.api.routes import auth, devices, experiments, measurements, system, ws

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(measurements.router)
api_router.include_router(devices.router)
api_router.include_router(experiments.router)
api_router.include_router(system.router)
api_router.include_router(ws.router)

#backend/main.py
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.auth import routes as auth_routes
from src.farmer import routes as farmer_routes
from src.auditor import auditor_api as auditor_routes
from src.ingestion import routes as ingestion_routes
from src.uploads import routes as uploads_routes
from src.iot import routes as iot_routes
from src.ml import routes as ml_routes
from src.fl import routes as fl_routes
from src.mrv import routes as mrv_routes
from src.db.init_db import init_db
from src.carbon_engine.ipcc_methods import calculate_emissions
from src.fpo import dashboard_api 




# Create FastAPI instance
app = FastAPI(
    title="AgroCarbon360 Backend",
    description="API's for carbon MRV solutions in agroforestry aand rice systems",
    version="0.1.0",
)

# CORS setup (alllowing frontend mobile apps to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to frontend domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(farmer_routes.router)
app.include_router(auditor_routes.router)
app.include_router(ingestion_routes.router)
app.include_router(uploads_routes.router)
app.include_router(iot_routes.router)
app.include_router(ml_routes.router)
app.include_router(fl_routes.router)
app.include_router(mrv_routes.router)

@app.on_event("startup")
def on_startup():
    """Initialize database when app starts"""
    init_db()


@app.get("/")
def read_root():
    return {"message": "Welcome to the AgroCarbon360 Backend API"}

# Health check route
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running!"}

app.include_router(dashboard_api.router)
#backend/main.py
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.auth import routes as auth_routes
from src.db.init_db import init_db



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
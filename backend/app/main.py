from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import engine

from app.routers import resumes
from app.routers import jobs
from app.routers import matching
from app.routers import auth


app = FastAPI(
    title="DStarix RecruitAI",
    description="AI-powered Recruitment & Candidate Matching Platform",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(matching.router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "DStarix RecruitAI API is running",
        "status": "success"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

@app.get("/health/database")
def database_health_check():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text(
                    "SELECT current_database(), current_user;"
                )
            )

            database_name, username = result.fetchone()

        return {
            "status": "healthy",
            "database": database_name,
            "user": username
        }

    except Exception as error:

        return {
            "status": "unhealthy",
            "error": str(error)
        }
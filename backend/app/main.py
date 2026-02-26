from dotenv import load_dotenv
load_dotenv()
import os
from fastapi.middleware.cors import CORSMiddleware




from fastapi import FastAPI
from app.db.session import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.api.routes.analytics import router as analytics_router

app.include_router(analytics_router)
from app.api.routes.intent import router as intent_router
app.include_router(intent_router)
from app.api.routes.query import router as query_router
app.include_router(query_router)




@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def health():
    return {"status": "running"}


from app.db.session import SessionLocal
from sqlalchemy.exc import IntegrityError
from app.models.member import Member



from app.db.session import SessionLocal
from sqlalchemy import text

@app.get("/health/db")
def db_health():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"db_status": "healthy"}
    except Exception as e:
        return {"db_status": "error", "detail": str(e)}


from app.db.session import SessionLocal
from app.models.organization import Organization
from app.models.member import Member


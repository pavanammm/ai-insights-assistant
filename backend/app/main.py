from fastapi import FastAPI
from app.db.session import init_db

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def health():
    return {"status": "running"}


from app.db.session import SessionLocal
from sqlalchemy.exc import IntegrityError
from app.models.member import Member

@app.get("/test/fk")
def test_fk():
    db = SessionLocal()
    try:
        # Insert a member with non-existent organization_uuid
        m = Member(
            organization_uuid="non-existent-uuid",
            code="TEST123",
            name="Test Member"
        )
        db.add(m)
        db.commit()
        return {"result": "FK NOT enforced ❌"}
    except IntegrityError:
        db.rollback()
        return {"result": "FK enforced ✅"}
    finally:
        db.close()


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

@app.get("/test/relationship")
def test_relationship():
    db = SessionLocal()

    # Create org
    org = Organization(name="Test Org")
    db.add(org)
    db.commit()

    # Create member linked to org
    member = Member(
        organization_uuid=org.organization_uuid,
        code="REL123",
        name="Rel Member"
    )
    db.add(member)
    db.commit()

    db.refresh(org)

    count = len(org.members)

    db.close()

    return {"member_count_on_org": count}

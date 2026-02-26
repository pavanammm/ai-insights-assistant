from time import time
from app.db.session import SessionLocal, init_db
from app.data.generator import (
    generate_organizations,
    generate_members,
    generate_response_codes,
    generate_tickets,
    generate_dispatches_and_responses
)
from app.db.base import Base
from app.db.session import engine


def seed():
    start = time()

    db = SessionLocal()

    print("Generating organizations...")
    orgs = generate_organizations(db)

    print("Generating members...")
    members = generate_members(db, orgs)

    print("Generating response codes...")
    generate_response_codes(db)

    print("Generating tickets...")
    tickets = generate_tickets(db)

    print("Generating dispatches and responses...")
    generate_dispatches_and_responses(db, tickets, members)

    db.close()

    end = time()
    print(f"Seeding completed in {round(end - start, 2)} seconds.")


if __name__ == "__main__":
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)

    print("Recreating tables...")
    Base.metadata.create_all(bind=engine)

    seed()

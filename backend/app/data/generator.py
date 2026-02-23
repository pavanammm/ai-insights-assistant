import random
from datetime import datetime, timedelta
from faker import Faker
from app.models import (
    Organization,
    Member,
    ResponseCode,
    Ticket,
    Dispatch,
    Response,
    ResponseDue
)

fake = Faker()

TICKET_COUNT = 5000

TICKET_TYPES = ["EMER", "NORMAL", "UPDATE", "CANCEL"]
TICKET_TYPE_WEIGHTS = [0.08, 0.80, 0.10, 0.02]

PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
PRIORITY_WEIGHTS = [0.40, 0.35, 0.20, 0.05]

CATEGORIES = ["ROUTINE", "LOCATE", "DAMAGE", "DESIGN"]
CATEGORY_WEIGHTS = [0.55, 0.25, 0.15, 0.05]


def weighted_choice(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def generate_organizations(db):
    orgs = []
    for _ in range(5):
        org = Organization(
            name=fake.company(),
            city=fake.city(),
            state=fake.state_abbr()
        )
        db.add(org)
        orgs.append(org)
    db.commit()
    return orgs


def generate_members(db, orgs):
    members = []
    for org in orgs:
        for _ in range(10):
            member = Member(
                organization_uuid=org.organization_uuid,
                code=fake.unique.bothify(text="M-####"),
                name=fake.company()
            )
            db.add(member)
            members.append(member)
    db.commit()
    return members


def generate_response_codes(db):
    codes = [
        ("CLEARED", "Facilities cleared"),
        ("MARKED", "Facilities marked"),
        ("NOT_APPLICABLE", "No facilities"),
        ("NO_CONFLICT", "No conflict"),
        ("UNABLE", "Unable to locate")
    ]

    for code, desc in codes:
        db.add(ResponseCode(code=code, description=desc))

    db.commit()


def generate_tickets(db):
    tickets = []

    base_date = datetime.utcnow() - timedelta(days=365)

    for i in range(TICKET_COUNT):
        created_at = base_date + timedelta(
            days=random.randint(0, 365),
            minutes=random.randint(0, 1440)
        )

        ticket = Ticket(
            ticket=f"TKT-{100000 + i}",
            revision="000",
            type=weighted_choice(TICKET_TYPES, TICKET_TYPE_WEIGHTS),
            priority=weighted_choice(PRIORITIES, PRIORITY_WEIGHTS),
            category=weighted_choice(CATEGORIES, CATEGORY_WEIGHTS),
            caller_name=fake.name(),
            caller_phone=fake.phone_number(),
            state=fake.state_abbr(),
            work_type=fake.word(),
            created_at=created_at,
            response_required=True
        )

        db.add(ticket)
        tickets.append(ticket)

        if i % 1000 == 0:
            db.commit()

    db.commit()
    return tickets


def generate_dispatches_and_responses(db, tickets, members):
    response_codes = db.query(ResponseCode).all()

    for ticket in tickets:
        assigned_members = random.sample(members, random.randint(1, 4))

        for member in assigned_members:
            dispatch = Dispatch(
                ticket_uuid=ticket.ticket_uuid,
                member_uuid=member.member_uuid,
                dispatched_at=ticket.created_at + timedelta(minutes=5)
            )
            db.add(dispatch)

            due_time = ticket.created_at + timedelta(hours=48)

            response_due = ResponseDue(
                ticket=ticket.ticket,
                revision=ticket.revision,
                member_uuid=member.member_uuid,
                due_at=due_time
            )
            db.add(response_due)

            # 90% chance of response
            if random.random() < 0.9:
                response = Response(
                    ticket=ticket.ticket,
                    revision=ticket.revision,
                    member_uuid=member.member_uuid,
                    code=random.choice(response_codes).code,
                    responded_at=ticket.created_at + timedelta(hours=random.randint(1, 40))
                )
                db.add(response)

        db.commit()

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.database import Base, SessionLocal, engine
from app.services.demo_seed import build_demo_events


def main() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    events = build_demo_events()
    with SessionLocal() as db:
        db.add_all(events)
        db.commit()
    print(
        "Seeded lifecycle messaging demo with "
        f"{len(events)} events: epsilon_greedy wins immediate reward, "
        "linucb wins long-term reward, and thompson_sampling is routed to governance review."
    )


if __name__ == "__main__":
    main()

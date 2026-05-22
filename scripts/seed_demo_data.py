import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.database import Base, SessionLocal, engine
from app.services.demo_seed import LIGHTWEIGHT_DEMO_SEED_SIZE, PORTFOLIO_DEMO_SEED_SIZE, build_demo_events


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed deterministic lifecycle messaging demo data.")
    parser.add_argument(
        "--mode",
        choices=["lightweight", "portfolio"],
        default="lightweight",
        help="lightweight keeps the original 400-event seed; portfolio defaults to 25,000 events.",
    )
    parser.add_argument("--n", type=int, default=None, help="Override event count, e.g. 100000.")
    args = parser.parse_args()
    default_n = PORTFOLIO_DEMO_SEED_SIZE if args.mode == "portfolio" else LIGHTWEIGHT_DEMO_SEED_SIZE
    event_count = args.n or default_n

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    events = build_demo_events(n=event_count)
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

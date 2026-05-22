import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.database import Base, SessionLocal, engine
from app.services.replay_engine import replay_to_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay logged bandit events.")
    parser.add_argument("--source", choices=["synthetic", "open_bandit"], default="synthetic")
    parser.add_argument("--mode", choices=["direct", "stream"], default="direct")
    parser.add_argument("--open-bandit-path", default=None)
    parser.add_argument("--n", type=int, default=250)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        count = replay_to_db(
            db,
            n=args.n,
            seed=args.seed,
            source=args.source,
            open_bandit_path=args.open_bandit_path,
            mode=args.mode,
        )
    print(f"Inserted {count} {args.source} events via {args.mode} mode.")


if __name__ == "__main__":
    main()

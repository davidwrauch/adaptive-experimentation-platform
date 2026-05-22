from pathlib import Path


OBD_URL = "https://research.zozo.com/data.html"
TARGET_DIR = Path("data/raw/open_bandit")


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print("Open Bandit Dataset download is intentionally manual for this demo.")
    print(f"1. Visit: {OBD_URL}")
    print("2. Download the Open Bandit Dataset CSV files.")
    print(f"3. Place a CSV file under: {TARGET_DIR.resolve()}")
    print("4. Replay with:")
    print(
        "   python scripts/run_replay.py --source open_bandit "
        "--open-bandit-path data/raw/open_bandit/<file>.csv --n 1000"
    )


if __name__ == "__main__":
    main()

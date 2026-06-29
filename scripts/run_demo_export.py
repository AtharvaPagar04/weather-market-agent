from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.database import SessionLocal, init_db
from app.services.evaluation_service import EvaluationService


SAFETY_MESSAGE = (
    "Paper trading only - generated files contain simulated/demo results. "
    "No real-money execution is performed."
)


def main() -> int:
    print(SAFETY_MESSAGE)
    init_db()
    db = SessionLocal()
    try:
        result = EvaluationService(db).export_demo_output()
    finally:
        db.close()

    print(f"Export status: {result['status']}")
    for path in result["files_created"]:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

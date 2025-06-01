import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


ROOT_DIR = Path(__file__).parent.parent
CSV_DIR = ROOT_DIR / "csv"
CSV_TEMPLATE = CSV_DIR / f"follow_up_boss_people_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"

API_KEY = os.getenv("API_KEY", "")

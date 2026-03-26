from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args, **_kwargs):
        return False


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "Gemini 2.5 Flash")
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(PROJECT_ROOT / 'backend' / 'app.db').as_posix()}",
    )
    data_dir: Path = Path(os.getenv("DATA_DIR", str(PROJECT_ROOT / "data"))).resolve()

    @property
    def sqlite_path(self) -> Path:
        if not self.database_url.startswith("sqlite:///"):
            raise ValueError("Only sqlite:/// DATABASE_URL values are supported.")
        raw_path = self.database_url.removeprefix("sqlite:///")
        return Path(raw_path).resolve()


settings = Settings()

from pathlib import Path
from flask_dantic.pydantic_serializer import serialize

here = Path(__file__).resolve().parent
version = (here / "VERSION").read_text(encoding="utf-8")

__version__ = version

__all__ = ("serialize", "version")

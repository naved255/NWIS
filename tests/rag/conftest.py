import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAG = ROOT / "rag"
sys.path.insert(0, str(RAG))

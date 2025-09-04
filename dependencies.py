# === dependencies.py ===
from services import TaskDatabase, AITaskAnalyzer

# Global instances
db = TaskDatabase()
ai_analyzer = AITaskAnalyzer()

def get_db() -> TaskDatabase:
    return db

def get_ai_analyzer() -> AITaskAnalyzer:
    return ai_analyzer
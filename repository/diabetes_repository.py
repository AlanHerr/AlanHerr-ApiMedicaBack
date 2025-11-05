from config.database import get_db_session
from model.diabetes import DiabetesPrediction


def create_diabetes_prediction(entry: dict) -> DiabetesPrediction:
    session = get_db_session()
    try:
        record = DiabetesPrediction(**entry)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
    finally:
        session.close()

from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from model.base import Base


class DiabetesPrediction(Base):
    __tablename__ = 'diabetes_predictions'

    id = Column(Integer, primary_key=True)

    # Entradas
    pregnancies = Column(Integer, nullable=False)
    glucose = Column(Float, nullable=False)
    blood_pressure = Column(Float, nullable=False)
    skin_thickness = Column(Float, nullable=False)
    insulin = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    diabetes_pedigree_function = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)

    # Resultados
    predicted = Column(Integer, nullable=False)  # 0/1
    probability = Column(Float, nullable=True)   # P(clase=1) si disponible

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'pregnancies': self.pregnancies,
            'glucose': self.glucose,
            'blood_pressure': self.blood_pressure,
            'skin_thickness': self.skin_thickness,
            'insulin': self.insulin,
            'bmi': self.bmi,
            'diabetes_pedigree_function': self.diabetes_pedigree_function,
            'age': self.age,
            'predicted': self.predicted,
            'probability': self.probability,
            'created_at': self.created_at.isoformat(),
        }

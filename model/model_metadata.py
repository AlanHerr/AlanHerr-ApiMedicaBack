from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from datetime import datetime
from model.base import Base


class ModelMetadata(Base):
    __tablename__ = 'models_metadata'

    id = Column(Integer, primary_key=True)
    model_id = Column(String(100), unique=True, nullable=False)  # "diabetes-v1"
    name = Column(String(255), nullable=False)  # "Diabetes Classifier v1"
    description = Column(String(1000))  # Descripción de qué hace el modelo
    version = Column(String(50))  # "1.0", "2.1", etc.
    
    model_type = Column(String(100))  # "DecisionTreeClassifier", "LogisticRegression", etc.
    
    # Información de features
    feature_names = Column(JSON, nullable=False)  # ["Pregnancies", "Glucose", ...]
    feature_types = Column(JSON, nullable=False)  # ["int", "float", "int", ...]
    n_features = Column(Integer, nullable=False)
    
    # Información de salida
    output_type = Column(String(50))  # "binary_classification", "multiclass", "regression"
    classes = Column(JSON)  # [0, 1] para clasificación binaria
    has_proba = Column(Boolean, default=False)  # ¿Puede dar probabilidades?
    
    # Almacenamiento
    model_path = Column(String(255), nullable=False)  # "/models/diabetes-v1-model.pkl"
    scaler_path = Column(String(255))  # "/models/diabetes-v1-scaler.pkl" (opcional)
    is_pipeline = Column(Boolean, default=False)  # ¿Es un Pipeline completo?
    
    is_active = Column(Boolean, default=True)
    
    # Metadata adicional del usuario
    metadata_json = Column(JSON)  # Información extra como feature_labels, etc.
    
    # Timestamps y usuario
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'model_id': self.model_id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'feature_types': self.feature_types,
            'n_features': self.n_features,
            'output_type': self.output_type,
            'classes': self.classes,
            'has_proba': self.has_proba,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }

    def get_features_with_labels(self):
        """Retorna lista de features con tipos y labels."""
        feature_labels = (self.metadata_json or {}).get('feature_labels', {})
        features = []
        for i, name in enumerate(self.feature_names):
            features.append({
                'name': name,
                'type': self.feature_types[i] if i < len(self.feature_types) else 'float',
                'label': feature_labels.get(name, name),
                'required': True,
            })
        return features

from model.model_metadata import ModelMetadata
from config.database import get_db_session
import logging

logger = logging.getLogger(__name__)


class ModelMetadataRepository:
    """Repository para acceder a la tabla models_metadata."""

    @staticmethod
    def get_by_model_id(model_id: str) -> ModelMetadata:
        """Obtiene un modelo por su ID."""
        session = get_db_session()
        try:
            model = session.query(ModelMetadata).filter_by(model_id=model_id).first()
            return model
        finally:
            session.close()

    @staticmethod
    def get_all_active() -> list:
        """Obtiene todos los modelos activos."""
        session = get_db_session()
        try:
            models = session.query(ModelMetadata).filter_by(is_active=True).all()
            return models
        finally:
            session.close()

    @staticmethod
    def get_all() -> list:
        """Obtiene todos los modelos (activos e inactivos)."""
        session = get_db_session()
        try:
            models = session.query(ModelMetadata).all()
            return models
        finally:
            session.close()

    @staticmethod
    def create(
        model_id: str,
        name: str,
        version: str,
        description: str,
        model_type: str,
        feature_names: list,
        feature_types: list,
        n_features: int,
        output_type: str,
        classes: list,
        has_proba: bool,
        model_path: str,
        scaler_path: str,
        is_pipeline: bool,
        created_by_user_id: int,
        metadata_json: dict = None
    ) -> ModelMetadata:
        """Crea un nuevo registro de modelo."""
        session = get_db_session()
        try:
            model = ModelMetadata(
                model_id=model_id,
                name=name,
                version=version,
                description=description,
                model_type=model_type,
                feature_names=feature_names,
                feature_types=feature_types,
                n_features=n_features,
                output_type=output_type,
                classes=classes,
                has_proba=has_proba,
                model_path=model_path,
                scaler_path=scaler_path,
                is_pipeline=is_pipeline,
                created_by_user_id=created_by_user_id,
                metadata_json=metadata_json or {},
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            logger.info(f"Modelo {model_id} creado exitosamente.")
            return model
        except Exception as e:
            session.rollback()
            logger.error(f"Error creando modelo: {e}")
            raise
        finally:
            session.close()

    @staticmethod
    def delete(model_id: str) -> bool:
        """Elimina un modelo (marca como inactivo)."""
        session = get_db_session()
        try:
            model = session.query(ModelMetadata).filter_by(model_id=model_id).first()
            if not model:
                return False
            
            model.is_active = False
            session.commit()
            logger.info(f"Modelo {model_id} marcado como inactivo.")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error eliminando modelo: {e}")
            raise
        finally:
            session.close()

    @staticmethod
    def exists(model_id: str) -> bool:
        """Verifica si un modelo existe."""
        session = get_db_session()
        try:
            count = session.query(ModelMetadata).filter_by(model_id=model_id).count()
            return count > 0
        finally:
            session.close()

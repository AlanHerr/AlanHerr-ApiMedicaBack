from model.model_metadata import ModelMetadata
from config.database import get_db_session, engine
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class ModelMetadataRepository:
    """Repository para acceder a la tabla models_metadata."""

    @staticmethod
    def get_by_model_id(model_id: str) -> ModelMetadata:
        session = get_db_session()
        try:
            model = session.query(ModelMetadata).filter_by(model_id=model_id).first()
            return model
        finally:
            session.close()

    @staticmethod
    def get_all_active() -> list:
        session = get_db_session()
        try:
            models = session.query(ModelMetadata).filter_by(is_active=True).all()
            return models
        finally:
            session.close()

    @staticmethod
    def get_all() -> list:
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
        """Soft delete — marca como inactivo (conservar para compatibilidad interna)."""
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
            logger.error(f"Error en soft delete del modelo: {e}")
            raise
        finally:
            session.close()

    @staticmethod
    def hard_delete(model_id: str) -> bool:
        """Hard delete — elimina físicamente el registro de metadata de la BD."""
        session = get_db_session()
        try:
            model = session.query(ModelMetadata).filter_by(model_id=model_id).first()
            if not model:
                return False
            session.delete(model)
            session.commit()
            logger.info(f"Registro de metadata del modelo {model_id} eliminado físicamente.")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error en hard_delete del modelo {model_id}: {e}")
            raise
        finally:
            session.close()

    @staticmethod
    def drop_predictions_table(model_id: str) -> bool:
        """Elimina la tabla dinámica de predicciones del modelo en PostgreSQL."""
        table_name = f"{model_id}_predictions"
        try:
            with engine.connect() as conn:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
                conn.commit()
            logger.info(f"Tabla dinámica '{table_name}' eliminada de la BD.")
            return True
        except Exception as e:
            logger.warning(f"No se pudo eliminar la tabla '{table_name}': {e}")
            return False

    @staticmethod
    def exists(model_id: str) -> bool:
        session = get_db_session()
        try:
            count = session.query(ModelMetadata).filter_by(model_id=model_id).count()
            return count > 0
        finally:
            session.close()
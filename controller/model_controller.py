import os
import shutil
import logging
import json
import tempfile
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from werkzeug.utils import secure_filename
from repository.user_repository import UserRepository
from repository.model_metadata_repository import ModelMetadataRepository
from service.model_service import ModelService, _convert_to_json_serializable, MODELS_DIR

logger = logging.getLogger(__name__)

model_bp = Blueprint('models', __name__)

ALLOWED_EXTENSIONS = {'pkl'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_admin(user_id):
    """Verifica si el usuario es admin."""
    user = UserRepository.get_by_id(user_id)
    if not user or not user.is_admin:
        return False
    return True


# ── UPLOAD ──────────────────────────────────────────────────────────────────

@model_bp.route('/admin/model/upload', methods=['POST', 'OPTIONS'])
def upload_model():
    """
    Endpoint para que un ADMIN cargue un nuevo modelo.

    Soporta:
    - Un archivo: PKL con Pipeline completo O PKL del modelo
    - Dos archivos: PKL del scaler + PKL del modelo
    - Metadata JSON complementaria (opcional)

    Form data:
      - model_file: archivo PKL (requerido)
      - scaler_file: archivo PKL (opcional)
      - metadata: JSON string con nombre, descripción, versión, etc.
    """
    if request.method == 'OPTIONS':
        return make_response(), 200

    try:
        verify_jwt_in_request()
    except Exception as e:
        return jsonify({'error': 'Token inválido o ausente', 'detail': str(e)}), 401

    user_id = get_jwt_identity()

    if not check_admin(int(user_id)):
        return jsonify({'error': 'Se requieren permisos de administrador'}), 403

    if 'model_file' not in request.files:
        return jsonify({'error': 'Archivo modelo requerido'}), 400

    model_file = request.files['model_file']
    scaler_file = request.files.get('scaler_file')

    if not model_file or model_file.filename == '':
        return jsonify({'error': 'Archivo modelo inválido'}), 400

    if not allowed_file(model_file.filename):
        return jsonify({'error': 'Solo se aceptan archivos .pkl'}), 400

    metadata_json = {}
    if request.form.get('metadata'):
        try:
            metadata_json = json.loads(request.form.get('metadata'))
        except Exception as e:
            return jsonify({'error': f'Metadata JSON inválido: {str(e)}'}), 400

    model_id = metadata_json.get('model_id') or metadata_json.get('name', 'model').replace(' ', '_').lower()
    name = metadata_json.get('name', model_id)
    version = metadata_json.get('version', '1.0')
    description = metadata_json.get('description', '')

    if ModelMetadataRepository.exists_active(model_id):
        return jsonify({'error': f'El modelo {model_id} ya existe'}), 409

    try:
        temp_dir = tempfile.mkdtemp()

        model_temp_path = os.path.join(temp_dir, secure_filename(model_file.filename))
        model_file.save(model_temp_path)

        scaler_temp_path = None
        if scaler_file and scaler_file.filename:
            scaler_temp_path = os.path.join(temp_dir, secure_filename(scaler_file.filename))
            scaler_file.save(scaler_temp_path)

        # Validación de integridad SHA-256 antes de cargar modelos serializados
        expected_model_hash = metadata_json.get('model_hash')
        expected_scaler_hash = metadata_json.get('scaler_hash')

        if expected_model_hash:
            try:
                ModelService.verify_file_hash(model_temp_path, expected_model_hash, 'modelo')
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

        if scaler_temp_path and expected_scaler_hash:
            try:
                ModelService.verify_file_hash(scaler_temp_path, expected_scaler_hash, 'scaler')
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

        metadata_json['model_hash'] = ModelService.compute_sha256(model_temp_path)
        if scaler_temp_path:
            metadata_json['scaler_hash'] = ModelService.compute_sha256(scaler_temp_path)

        model = ModelService.load_serialized_model(model_temp_path, expected_model_hash)
        model_metadata = ModelService.extract_metadata_from_model(model)

        if not model_metadata['feature_names'] and metadata_json.get('feature_names'):
            model_metadata['feature_names'] = metadata_json.get('feature_names', [])
            model_metadata['n_features'] = len(model_metadata['feature_names'])

        if not model_metadata['feature_names']:
            n_features = model_metadata['n_features']
            if n_features > 0:
                model_metadata['feature_names'] = [f'feature_{i}' for i in range(n_features)]
            else:
                logger.warning("No se pudo determinar número de features")
                return jsonify({
                    'error': 'No se pudo extraer información de features del modelo. '
                             'Proporciona feature_names en metadata.'
                }), 400

        if not model_metadata['feature_types'] or len(model_metadata['feature_types']) == 0:
            model_metadata['feature_types'] = ['float'] * len(model_metadata['feature_names'])

        is_pipeline = model_metadata.get('is_pipeline', False)

        if not is_pipeline and not scaler_temp_path:
            logger.warning("Modelo no es Pipeline y no se proporcionó scaler")

        model_final_path, scaler_final_path = ModelService.save_model_files(
            model_temp_path,
            scaler_temp_path,
            model_id,
            is_pipeline
        )

        model_record = ModelMetadataRepository.create(
            model_id=model_id,
            name=name,
            version=version,
            description=description,
            model_type=model_metadata['model_type'],
            feature_names=model_metadata['feature_names'],
            feature_types=model_metadata['feature_types'],
            n_features=model_metadata['n_features'],
            output_type=model_metadata['output_type'],
            classes=model_metadata['classes'],
            has_proba=model_metadata['has_proba'],
            model_path=model_final_path,
            scaler_path=scaler_final_path,
            is_pipeline=is_pipeline,
            created_by_user_id=int(user_id),
            metadata_json=metadata_json
        )

        response_data = _convert_to_json_serializable({
            'model_id': model_record.model_id,
            'name': model_record.name,
            'version': model_record.version,
            'model_type': model_record.model_type,
            'features': model_record.get_features_with_labels(),
            'output': {
                'type': model_record.output_type,
                'classes': _convert_to_json_serializable(model_record.classes),
                'has_probability': model_record.has_proba,
            },
            'status': 'ready',
            'created_at': model_record.created_at.isoformat(),
        })

        shutil.rmtree(temp_dir, ignore_errors=True)

        return jsonify(response_data), 201

    except Exception as e:
        logger.error(f"Error en upload_model: {e}")
        return jsonify({'error': f'Error procesando modelo: {str(e)}'}), 500


# ── LIST ─────────────────────────────────────────────────────────────────────

@model_bp.route('/models', methods=['GET'])
def list_models():
    """Lista todos los modelos disponibles."""
    try:
        models = ModelMetadataRepository.get_all_active()
        models_list = [
            {
                'model_id': m.model_id,
                'name': m.name,
                'version': m.version,
                'description': m.description,
                'model_type': m.model_type,
                'n_features': m.n_features,
                'output_type': m.output_type,
                'created_at': m.created_at.isoformat(),
            }
            for m in models
        ]
        return jsonify({'models': models_list}), 200
    except Exception as e:
        logger.error(f"Error listando modelos: {e}")
        return jsonify({'error': str(e)}), 500


# ── SCHEMA ────────────────────────────────────────────────────────────────────

@model_bp.route('/models/<model_id>/schema', methods=['GET'])
def get_model_schema(model_id):
    """
    Obtiene el schema de un modelo específico.
    Usado por el frontend para generar formularios dinámicamente.
    """
    try:
        model_metadata = ModelMetadataRepository.get_by_model_id(model_id)
        if not model_metadata:
            return jsonify({'error': 'Modelo no encontrado'}), 404

        schema = _convert_to_json_serializable({
            'model_id': model_metadata.model_id,
            'name': model_metadata.name,
            'version': model_metadata.version,
            'description': model_metadata.description,
            'model_type': model_metadata.model_type,
            'features': model_metadata.get_features_with_labels(),
            'output': {
                'type': model_metadata.output_type,
                'classes': _convert_to_json_serializable(model_metadata.classes),
                'has_probability': model_metadata.has_proba,
            }
        })
        return jsonify(schema), 200
    except Exception as e:
        logger.error(f"Error obteniendo schema: {e}")
        return jsonify({'error': str(e)}), 500


# ── DELETE ────────────────────────────────────────────────────────────────────

@model_bp.route('/admin/model/<model_id>', methods=['DELETE', 'OPTIONS'])
def delete_model(model_id):
    """
    Elimina un modelo completamente:
    1. Tabla dinámica de predicciones en PostgreSQL
    2. Archivos PKL del disco (sin borrar el directorio raíz /models/)
    3. Registro de metadata en BD (hard delete)
    Solo ADMIN.
    """
    if request.method == 'OPTIONS':
        return make_response(), 200

    try:
        verify_jwt_in_request()
    except Exception as e:
        return jsonify({'error': 'Token inválido o ausente', 'detail': str(e)}), 401

    user_id = get_jwt_identity()

    if not check_admin(int(user_id)):
        return jsonify({'error': 'Se requieren permisos de administrador'}), 403

    try:
        # 1. Obtener metadata antes de eliminar (necesitamos los paths)
        model_metadata = ModelMetadataRepository.get_by_model_id(model_id)
        if not model_metadata:
            return jsonify({'error': 'Modelo no encontrado'}), 404

        model_path = model_metadata.model_path
        scaler_path = model_metadata.scaler_path

        deleted_info = {
            'table': False,
            'model_file': False,
            'scaler_file': False,
            'metadata': False,
        }

        # 2. Eliminar tabla dinámica de predicciones en PostgreSQL
        deleted_info['table'] = ModelMetadataRepository.drop_predictions_table(model_id)

        # 3. Eliminar solo los archivos PKL — nunca el directorio raíz /models/
        models_root = str(MODELS_DIR.resolve())

        if model_path and os.path.exists(model_path):
            os.remove(model_path)
            deleted_info['model_file'] = True
            logger.info(f"Archivo modelo eliminado: {model_path}")

        if scaler_path and os.path.exists(scaler_path):
            os.remove(scaler_path)
            deleted_info['scaler_file'] = True
            logger.info(f"Archivo scaler eliminado: {scaler_path}")

        # Solo borrar subdirectorio si existe Y no es el directorio raíz
        model_dir = os.path.dirname(model_path) if model_path else None
        if model_dir and os.path.isdir(model_dir) and os.path.realpath(model_dir) != os.path.realpath(models_root):
            shutil.rmtree(model_dir, ignore_errors=True)
            logger.info(f"Subdirectorio {model_dir} eliminado")

        # Garantizar que el directorio raíz siempre existe tras el delete
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

        # 4. Hard delete del registro de metadata
        deleted_info['metadata'] = ModelMetadataRepository.hard_delete(model_id)

        logger.info(f"Modelo {model_id} eliminado completamente: {deleted_info}")

        return jsonify({
            'message': f'Modelo {model_id} eliminado completamente',
            'deleted': deleted_info
        }), 200

    except Exception as e:
        logger.error(f"Error eliminando modelo {model_id}: {e}")
        return jsonify({'error': str(e)}), 500
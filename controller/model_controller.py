import os
import joblib
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from repository.user_repository import UserRepository
from repository.model_metadata_repository import ModelMetadataRepository
from service.model_service import ModelService, _convert_to_json_serializable
from flask_cors import cross_origin

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


# 🔥 SOLO ESTA PARTE ES LA IMPORTANTE DEL FIX
@model_bp.route('/admin/model/upload', methods=['POST', 'OPTIONS'])
@cross_origin(
    origins=[
        "https://verbose-space-yodel-jpwq47wj75pf7px-3000.app.github.dev",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    supports_credentials=True
)
@jwt_required()
def upload_model():
    """
    Endpoint para que un ADMIN cargue un nuevo modelo.
    """

    user_id = get_jwt_identity()

    # Verificar admin
    if not check_admin(int(user_id)):
        return jsonify({'error': 'Se requieren permisos de administrador'}), 403

    # Validar archivos
    if 'model_file' not in request.files:
        return jsonify({'error': 'Archivo modelo requerido'}), 400

    model_file = request.files['model_file']
    scaler_file = request.files.get('scaler_file')

    if not model_file or model_file.filename == '':
        return jsonify({'error': 'Archivo modelo inválido'}), 400

    if not allowed_file(model_file.filename):
        return jsonify({'error': 'Solo se aceptan archivos .pkl'}), 400

    # Parsear metadata
    metadata_json = {}
    if request.form.get('metadata'):
        try:
            import json
            metadata_json = json.loads(request.form.get('metadata'))
        except Exception as e:
            return jsonify({'error': f'Metadata JSON inválido: {str(e)}'}), 400

    model_id = metadata_json.get('model_id') or metadata_json.get('name', 'model').replace(' ', '_').lower()
    name = metadata_json.get('name', model_id)
    version = metadata_json.get('version', '1.0')
    description = metadata_json.get('description', '')

    if ModelMetadataRepository.exists(model_id):
        return jsonify({'error': f'El modelo {model_id} ya existe'}), 409

    try:
        import tempfile

        temp_dir = tempfile.mkdtemp()

        model_temp_path = os.path.join(temp_dir, secure_filename(model_file.filename))
        model_file.save(model_temp_path)

        scaler_temp_path = None
        if scaler_file and scaler_file.filename:
            scaler_temp_path = os.path.join(temp_dir, secure_filename(scaler_file.filename))
            scaler_file.save(scaler_temp_path)

        expected_model_hash = metadata_json.get('model_hash')
        expected_scaler_hash = metadata_json.get('scaler_hash')

        if expected_model_hash:
            ModelService.verify_file_hash(model_temp_path, expected_model_hash, 'modelo')

        if scaler_temp_path and expected_scaler_hash:
            ModelService.verify_file_hash(scaler_temp_path, expected_scaler_hash, 'scaler')

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
                return jsonify({'error': 'No se pudo extraer features'}), 400

        if not model_metadata['feature_types']:
            model_metadata['feature_types'] = ['float'] * len(model_metadata['feature_names'])

        is_pipeline = model_metadata.get('is_pipeline', False)

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

        response_data = {
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
        }

        return jsonify(_convert_to_json_serializable(response_data)), 201

    except Exception as e:
        logger.error(f"Error en upload_model: {e}")
        return jsonify({'error': str(e)}), 500
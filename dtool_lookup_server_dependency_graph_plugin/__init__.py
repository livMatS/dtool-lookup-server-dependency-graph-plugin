from flask import (
    abort,
    jsonify,
    request
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest import Blueprint

from dtool_lookup_server import AuthenticationError
from dtool_lookup_server.sql_models import DatasetSchema

try:
    from importlib.metadata import version, PackageNotFoundError
except ModuleNotFoundError:
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
   pass

from .schemas import DependencyKeysSchema

from .utils import (
    dependency_graph_by_user_and_uuid,
    config_to_dict,
)


graph_bp = Blueprint("graph", __name__, url_prefix="/graph")


@graph_bp.route("/lookup/<uuid>", methods=["GET"])
@graph_bp.response(200, DatasetSchema(many=True))
@graph_bp.paginate()
@jwt_required()
def lookup_dependency_graph_by_default_keys(pagination_parameters: PaginationParameters,
                                            uuid):
    """List the datasets within the same dependency graph as <uuid>.
    If not all datasets are accessible by the user, an incomplete, disconnected
    graph may arise."""
    username = get_jwt_identity()
    try:
        datasets = dependency_graph_by_user_and_uuid(username, uuid)
    except AuthenticationError:
        abort(401)
    pagination_parameters.item_count = len(datasets)
    return jsonify(
        datasets[pagination_parameters.first_item: pagination_parameters.last_item + 1]
    )


@graph_bp.route("/lookup/<uuid>", methods=["POST"])
@bp.arguments(DependencyKeysSchema(partial=True))
@graph_bp.response(200, DatasetSchema(many=True))
@graph_bp.paginate()
@jwt_required()
def lookup_dependency_graph_by_custom_keys(dependency_keys: DependencyKeysSchema,
                                           pagination_parameters: PaginationParameters,
                                           uuid):
    """List the datasets within the same dependency graph as <uuid>.
    If not all datasets are accessible by the user, an incomplete, disconnected
    graph may arise."""
    username = get_jwt_identity()
    # dependency_keys = request.get_json()
    try:
        datasets = dependency_graph_by_user_and_uuid(username, uuid, dependency_keys)
    except AuthenticationError:
        abort(401)
    pagination_parameters.item_count = len(datasets)
    return jsonify(
        datasets[pagination_parameters.first_item: pagination_parameters.last_item + 1]
    )


@graph_bp.route("/config", methods=["GET"])
@jwt_required()
def plugin_config():
    """Return the JSON-serialized dependency graph plugin configuration."""
    username = get_jwt_identity()
    try:
        config = config_to_dict(username)
    except AuthenticationError:
        abort(401)
    return jsonify(config)

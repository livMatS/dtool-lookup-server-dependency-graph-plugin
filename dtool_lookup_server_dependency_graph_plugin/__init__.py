from flask import (
    abort,
    Blueprint,
    jsonify,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from dtool_lookup_server import AuthenticationError,
from dtool_lookup_server.utils import (
    dependency_graph_by_user_and_uuid,
    config_to_dict,
)


graph_bp = Blueprint("graph", __name__, url_prefix="/graph")


@graph_bp.route("<uuid>", methods=["GET"])
@jwt_required
def lookup_dependency_graph(uuid):
    """List the datasets within the same dependency graph as <uuid>.
    If not all datasets are accessible by the user, an incomplete, disconnected
    graph may arise."""
    username = get_jwt_identity()
    try:
        datasets = dependency_graph_by_user_and_uuid(username, uuid)
    except AuthenticationError:
        abort(401)
    return jsonify(datasets)


@graph_bp.route("/config", methods=["GET"])
@jwt_required
def server_config():
    """Return the JSON-serialized dependency graph plugin configuration."""
    username = get_jwt_identity()
    try:
        config = config_to_dict(username)
    except AuthenticationError:
        abort(401)
    return jsonify(config)

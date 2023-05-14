try:
    from importlib.metadata import version, PackageNotFoundError
except ModuleNotFoundError:
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
   pass

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
from flask_smorest.pagination import PaginationParameters

from dtool_lookup_server import AuthenticationError
from dtool_lookup_server.sql_models import DatasetSchema


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
@graph_bp.arguments(DependencyKeysSchema(partial=True))
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


class DependencyGraphExtension(ExtensionABC):
    """Extensions for building and queryng dependency graphs."""

    # NOTE: Not very neat using class variables here, but the way the plugin
    # system works now, we need to provide the class-external route above some
    # means of accessing the database that's configured within the init_app
    # method here.
    client = None
    collection = None
    db = None

    def init_app(self, app):
        try:
            self._mongo_uri = app.config["MONGO_URI"]
            DependencyGraphExtension.client = MongoClient(self._mongo_uri,
                                      uuidRepresentation='standard')
        except KeyError:
            raise(RuntimeError("Please set the MONGO_URI environment variable"))  # NOQA

        try:
            self._mongo_db = app.config["MONGO_DB"]
            DependencyGraphExtension.db = self.client[self._mongo_db]
        except KeyError:
            raise(RuntimeError("Please set the MONGO_DB environment variable"))  # NOQA

        try:
            self._mongo_collection = app.config["MONGO_COLLECTION"]
            DependencyGraphExtension.collection = self.db[self._mongo_collection]
        except KeyError:
            raise(RuntimeError("Please set the MONGO_COLLECTION environment variable"))  # NOQA

    def register_dataset(self, dataset_info):
        """Does nothing, relies on dtool-lookup-server-direct-mongo-plugin."""
        pass

    def get_config(self):
        """Return initial Config object, available app-instance independent."""
        return Config

    def get_config_secrets_to_obfuscate(self):
        """Return config secrets never to be exposed clear text."""
        return CONFIG_SECRETS_TO_OBFUSCATE

    def get_blueprint(self):
        return graph_bp
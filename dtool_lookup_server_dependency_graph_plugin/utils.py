"""Utility functions."""

import logging
import pymongo

from dtool_lookup_server import mongo
from dtool_lookup_server.utils import (
    _preprocess_privileges,
    _dict_to_mongo_query,
)

from dtool_lookup_server_dependency_graph_pluginr.graph import (
    query_dependency_graph,
    build_undirected_adjecency_lists,
)

from dtool_lookup_server_dependency_graph_plugin.config import Config

logger = logging.getLogger(__name__)

def dependency_graph_by_user_and_uuid(username, uuid):
    """Aggregate all datasets within the same dependency graph as uuid.

    :param username: username
    :param uuid: UUID of dataset to start dependency graph search from
    :returns: List of dicts if user is valid and has access to datasets.
              Empty list if user is valid but has not got access to any
              datasets.
    :raises: AuthenticationError if user is invalid.
    """

    # enable undirected view on dependency graph
    if not Config.ENABLE_DEPENDENCY_VIEW:
        logger.warning(
            "Received dependency graph request from user '{}', but "
            "feature is disabled.".format(username))
        return []  # silently reject request

    if Config.MONGO_DEPENDENCY_VIEW in mongo.db.list_collection_names():
        if Config.FORCE_REBUILD_DEPENDENCY_VIEW:
            logger.warning("Dropping exisitng view '{}'.".format(Config.MONGO_DEPENDENCY_VIEW))
            mongo.db[Config.MONGO_DEPENDENCY_VIEW].drop()

    if Config.MONGO_DEPENDENCY_VIEW not in mongo.db.list_collection_names():
        aggregation_pipeline = build_undirected_adjecency_lists()
        logger.debug("Configured view with {}".format(aggregation_pipeline))
        try:
            mongo.db.command(
                'create',
                Config.MONGO_DEPENDENCY_VIEW, viewOn=Config.MONGO_COLLECTION,
                pipeline=aggregation_pipeline)
        except pymongo.errors.OperationFailure as exc:
            logger.exception(exc)
            logger.warning("Dependency view creation failed. Ignored.")
    else:
        logger.info("Existing view '{}' not touched.".format(Config.MONGO_DEPENDENCY_VIEW))

    # in the pipeline, we need to filter privileges two times. Initially,
    # when looking up the specified uuid , and subsequently after building
    # the dependency graph for the hypothetical case of the user not having
    # sufficient privileges to view all datasets within the same graph.
    # Building those pre- and post-queries relies on the _dict_to_mongo_query
    # utility function and hence requires the 'uuids' keyword configured as
    # an allowed query key. This is the default configuration in config.Config.
    pre_query = _preprocess_privileges(username, {'uuids': [uuid]})
    post_query = _preprocess_privileges(username, {})

    # If there are no base URIs at this point it means that the user has not
    # got privileges to search for anything.
    if (len(pre_query["base_uris"]) == 0) or len(post_query["base_uris"]) == 0:
        return []

    pre_query = _dict_to_mongo_query(pre_query)
    post_query = _dict_to_mongo_query(post_query)

    datasets = []
    mongo_aggregation = query_dependency_graph(pre_query, post_query)
    logger.debug("Constructed mongo aggregation: {}".format(mongo_aggregation))
    cx = mongo.db[Config.MONGO_COLLECTION].aggregate(mongo_aggregation)
    for ds in cx:
        datasets.append(ds)
    return datasets
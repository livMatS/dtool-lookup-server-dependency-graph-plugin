import json
import os

class Config(object):
    MONGO_DEPENDENCY_VIEW = os.environ.get('DTOOL_LOOKUP_SERVER_MONGO_DEPENDENCY_VIEW', 'dependencies')

    # If enabled, the underlying database will offer a 'view' named
    # 'dependencies' on the default collection 'datasets'. 'dependencies'
    # offers an on-the-fly-generated collection of undirected per-dataset
    # adjacency lists in order to facilitate searching dataset dependeny graphs
    # in both directions.
    # See https://docs.mongodb.com/manual/core/views/.
    ENABLE_DEPENDENCY_VIEW = os.environ.get('DTOOL_LOOKUP_SERVER_ENABLE_DEPENDENCY_VIEW',
                                            'False').lower() in ['true', '1', 'y', 'yes', 'on']

    FORCE_REBUILD_DEPENDENCY_VIEW = os.environ.get('DTOOL_LOOKUP_SERVER_FORCE_REBUILD_DEPENDENCY_VIEW',
                                                   'False').lower() in ['true', '1', 'y', 'yes', 'on']

    # Specify a key or multiple possible keys that hold unidirectional
    # dependency information in form of parents' UUIDs. The syntax must be
    # a single key or a JSON-formatted list of keys.
    # Nested fields are separated by a dot (.)
    DEPENDENCY_KEYS = [
        'readme.derived_from.uuid',
        'annotations.source_dataset_uuid'
    ]
    dep_key = os.environ.get('DTOOL_LOOKUP_SERVER_DEPENDENCY_KEYS', '')
    if len(dep_key) > 0:
        try:
            DEPENDENCY_KEYS = json.loads(dep_key)
        except json.JSONDecodeError:  # assume only one key, plain string
            DEPENDENCY_KEYS = [dep_key]

    @classmethod
    def to_dict(cls):
        """Convert server configuration into dict."""
        for k, v in cls.__dict__.items():
            # select only capitalized fields
            if k.upper() == k:
                d[k.lower()] = v
        return d

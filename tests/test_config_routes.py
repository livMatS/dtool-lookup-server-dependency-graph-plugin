"""Test the /scaffolding/config blueprint route."""

import json
import dtool_lookup_server_dependency_graph_plugin

from . import tmp_app_with_users  # NOQA
from . import snowwhite_token

def test_config_info_route(tmp_app_with_users):  # NOQA

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.get(
        "/graph/config",
        headers=headers,
    )
    assert r.status_code == 200

    expected_content = {
        'dependency_keys': ['readme.derived_from.uuid',
                            'annotations.source_dataset_uuid'],
        'dynamic_dependency_keys': True,
        'enable_dependency_view': True,
        'force_rebuild_dependency_view': False,
        'mongo_dependency_view_bookkeeping': 'dep_views',
        'mongo_dependency_view_cache_size': 10,
        'mongo_dependency_view_prefix': 'dep:',
        'version': dtool_lookup_server_dependency_graph_plugin.__version__}

    response = json.loads(r.data.decode("utf-8"))
    assert response == expected_content

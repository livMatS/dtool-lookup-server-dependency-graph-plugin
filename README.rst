Dtool Lookup Server
===================

- GitHub: https://github.com/IMTEK-Simulation/dtool-lookup-server-dependency-graph-plugin
- PyPI: https://pypi.python.org/pypi/dtool-lookup-server-dependency-graph-plugin
- Free software: MIT License


Features
--------

- Use a dataset UUID to lookup all datasets within the same dependency graph


Introduction
------------

`dtool <https://dtool.readthedocs.io>`_ is a command line tool for packaging
data and metadata into a dataset. A dtool dataset manages data and metadata
without the need for a central database.

However, if one has to manage more than a hundred datasets it can be helpful
to have the datasets' metadata stored in a central server to enable one to
quickly find datasets of interest.

The `dtool-lookup-server <https://github.com/jic-dtool/dtool-lookup-server`_ 
provides a web API for registering datasets' metadata
and provides functionality to lookup, list and search for datasets.

This plugin enables the dtool-lookup-server to directly provide all
datasets within a specific dependency graph.


Installation
------------

Install the dtool lookup server dependency graph plugin::

    $ pip install dtool-lookup-server-dependency-graph-plugin

Setup and configuration
-----------------------

Configure plugin behavior
^^^^^^^^^^^^^^^^^^^^^^^^^

With

    export DTOOL_LOOKUP_SERVER_ENABLE_DEPENDENCY_VIEW=True

the underlying database will offer a view on the default collection.
This view offers an on-the-fly-generated collection of undirected per-dataset
adjacency lists in order to facilitate searching dataset dependeny graphs
in both directions. With

    export DTOOL_LOOKUP_SERVER_FORCE_REBUILD_DEPENDENCY_VIEW=True

this view is reestablished at every query. This is required to apply changes to
related options, such as the JSON-formatted list

    export DTOOL_LOOKUP_SERVER_DEPENDENCY_KEYS='["readme.derived_from.uuid", "annotations.source_dataset_uuid"]'

which indicates at which keys to look for source dataset(s) by UUID. The example
above illustrates the default. All keys are treated equivalentnly and nested
fields are separated by the dot (.). The actual nesting hierarchy does not
matter. This means, for example, both structures evaluate equivalently in the
following::

    {'readme': {'derived_from': {'uuid':
        ['8ecd8e05-558a-48e2-b563-0c9ea273e71e',
         'faa44606-cb86-4877-b9ea-643a3777e021']}}}

    {'readme': {'derived_from':
        [{'uuid': '8ecd8e05-558a-48e2-b563-0c9ea273e71e'},
         {'uuid': 'faa44606-cb86-4877-b9ea-643a3777e021'}]}}

Setting

    export DTOOL_LOOKUP_SERVER_MONGO_DEPENDENCY_VIEW=dependencies

explicitly  will change the the name of the dependency view, as described above.

Note that the above exports containing JSON syntax are formatted for usage in
bash. Enclosing single quotes are not to be part of the actual variable value
when environment variables are configured elsewhere.


The dtool lookup server API
---------------------------

The dtool lookup server makes use of the Authrized header to pass through the
JSON web token for authrization. Below we create environment variables for the
token and the header used in the ``curl`` commands::

    $ TOKEN=$(flask user token olssont)
    $ HEADER="Authorization: Bearer $TOKEN"


Standard user usage
^^^^^^^^^^^^^^^^^^^

Looking up dependency graphs based on a dataset's UUID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dataset can be derived from one or several source datasets, usually
by machine-generated annotations attached via the Python API at dataset
creation time, or manually by recording the UUIDs of parent datasets in some
arbitrary fields within the README.yml. If configured appropriately,
querying the server directly for all datasets within the same dependency
graph by UUID is possible, i.e.

    $ UUID=8ecd8e05-558a-48e2-b563-0c9ea273e71e
    $ curl -H $HEADER http://localhost:5000/dependency/graph/$UUID

Looking up a dependency graph by UUID will reuslt in unique per-UUID hits.
As it is possible for a dataset to be registered in more than one base
URI, the query will yield one arbitrary hit in such a case.


Querying server plugin configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The request

    $ curl -H "$HEADER" http://localhost:5000/dependency/config

will return the current dependency graph plugin configuration with all keys in lowercase::

    {
      "dependency_keys": [
        "readme.derived_from.uuid",
        "annotations.source_dataset_uuid"
      ],
      "enable_dependency_view": true,
      "force_rebuild_dependency_view": false,
      "mongo_dependency_view": "dependencies",
    }

See ``dtool_lookup_server_dependency_graph_plugin.config.Config`` for more information.

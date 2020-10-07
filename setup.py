from setuptools import setup

url = "https://github.com/IMTEK-Simulation/dtool-lookup-server-dependency-graph-plugin"
version = "0.1.0"
with open('README.rst', 'r') as fh:
    readme = fh.read()

setup(
    name="dtool-lookup-server-dependency-graph-plugin",
    packages=["dtool_lookup_server_dependency_graph_plugin"],
    description="dtool lookup server plugin for querying dataset dependency graphs",
    long_description=readme,
    author="Johannes Hörmann",
    author_email="johannes.hoermann@imtek.uni-freiburg.de",
    version=version,
    url=url,
    entry_points={
        'dtool_lookup_server.blueprints': [
            'dtool_lookup_server_dependency_graph_plugin=dtool_lookup_server_dependency_graph_plugin:graph_bp',
        ],
    },
    install_requires=[
        "dtool-lookup-server",
    ],
    download_url="{}/tarball/{}".format(url, version),
    license="MIT",
)

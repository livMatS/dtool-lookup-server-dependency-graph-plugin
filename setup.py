from setuptools import setup
from setuptools_scm import get_version
version = get_version(root='.', relative_to=__file__)

def local_scheme(version):
    """Skip the local version (eg. +xyz of 0.6.1.dev4+gdf99fe2)
    to be able to upload to Test PyPI"""
    return ""

url = "https://github.com/livMatS/dserver-dependency-graph-plugin"
readme = open('README.rst').read()

setup(
    name="dserver-dependency-graph-plugin",
    packages=["dserver_dependency_graph_plugin"],
    description="dserver plugin for querying dataset dependency graphs",
    long_description=readme,
    author="Johannes Hörmann",
    author_email="johannes.hoermann@imtek.uni-freiburg.de",
    use_scm_version={"local_scheme": local_scheme},
    url=url,
    entry_points={
        'dserver.extension': [
            'DependencyGraphExtension=dserver_dependency_graph_plugin:DependencyGraphExtension',
        ],
    },
    setup_requires=['setuptools_scm'],
    install_requires=[
        "dserver>=0.18.0",
        "dtoolcore>=3.17.0",
        "dserver-direct-mongo-plugin>=0.2.0"
    ],
    download_url="{}/tarball/{}".format(url, version),
    license="MIT",
)

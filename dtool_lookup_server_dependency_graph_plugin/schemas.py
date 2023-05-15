from marshmallow import Schema
from marshmallow.fields import (
    String,
    List,
)


class DependencyKeysSchema(Schema):
    dependency_keys = List(String)
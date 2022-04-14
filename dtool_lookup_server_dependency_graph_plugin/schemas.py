from marshmallow import Schema
from marshmallow.fields import (
    String,
    List,
)


class DependencyKeysSchema(Schema):
    base_uri = String()
    users_with_register_permissions = List(String)
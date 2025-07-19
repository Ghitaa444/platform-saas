# backend/schemas.py

from marshmallow import Schema, fields, validate

# You might need to import your models if your schemas reference them for metadata
# from .models import User, Container # <-- ملاحظة: إذا كنت تستخدم هذه في مكان آخر في schemas، قم بإلغاء التعليق

# --- User Schemas ---

# Schema for validating user registration input (e.g., in auth.py's register route)
class UserRegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=6))

# Schema for validating user login input (e.g., in auth.py's login route)
class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

# Schema for serializing User objects for output (what you send back in API responses)
class UserSchema(Schema):
    id = fields.Int(dump_only=True) 
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

# --- Container Schemas ---

# Schema for validating container creation input (e.g., in container_routes.py's create_container route)
class ContainerCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    image = fields.Str(required=True, validate=validate.Length(max=200))
    ports = fields.Str(allow_none=True, metadata={'description': 'Comma-separated list of host_port:container_port (e.g., "80:8080,443:4443")'})
    environment = fields.Dict(allow_none=True, metadata={'description': 'Dictionary of environment variables (e.g., {"KEY": "VALUE"})'})

# Schema for serializing Container objects for output
class ContainerSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    image = fields.Str(required=True)
    docker_container_id = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    environment = fields.Dict(dump_only=True)
    ports = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()
user_schema = UserSchema()
container_create_schema = ContainerCreateSchema()
container_schema = ContainerSchema()
containers_schema = ContainerSchema(many=True) # For lists of containers
from marshmallow import Schema, fields, validate
from marshmallow.validate import Length, And, Regexp

class UserRegisterSchema(Schema):
    username = fields.Str(required=True, validate=Length(min=3, max=80))
    email = fields.Email(required=True, validate=Length(max=120))
    password = fields.Str(required=True, validate=Length(min=6)) 

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ForgotPasswordRequestSchema(Schema):
    email = fields.Email(required=True, validate=Length(max=120))

class ResetPasswordSchema(Schema):
    token = fields.Str(required=True, validate=Length(min=32))
    new_password = fields.Str(required=True, validate=Length(min=10)) 

class ContainerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    image = fields.Str(required=True, validate=validate.Length(min=1))
    status = fields.Str(dump_only=True) 
    docker_container_id = fields.Str(dump_only=True) 
    ports = fields.Dict(allow_none=True)
    environment = fields.Dict(allow_none=True) 
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True) # To link to the user who owns it

# Schema for creating a new container (what user sends in POST request)
class CreateContainerSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    image = fields.Str(required=True, validate=validate.Length(min=1))
    ports = fields.Dict(keys=fields.Str(), values=fields.Str(), allow_none=True) # Optional: e.g., {"80/tcp": "8080"}
    environment = fields.Dict(keys=fields.Str(), values=fields.Str(), allow_none=True) # Optional: e.g., {"MY_VAR": "my_value"}

# Schema for updating an existing container (what user sends in PUT request)
class UpdateContainerSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=128), required=False) # Optional for partial updates
    ports = fields.Dict(keys=fields.Str(), values=fields.Str(), allow_none=True, required=False)
    environment = fields.Dict(keys=fields.Str(), values=fields.Str(), allow_none=True, required=False)

# User schema instances
user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()
user_schema = UserSchema()

forgot_password_request_schema = ForgotPasswordRequestSchema()
reset_password_schema = ResetPasswordSchema()

container_schema = ContainerSchema()
containers_schema = ContainerSchema(many=True)
create_container_schema = CreateContainerSchema() 
update_container_schema = UpdateContainerSchema()
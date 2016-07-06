from flask import request, jsonify
from ..schemas import user_schema, image_schema
from . import api
from flask_login import login_required
from ..decorators import permission_required
from ..models import Permission, Image, User


@api.route("/upload", methods=['POST'])
@login_required
@permission_required(Permission.SUGGEST)
def upload():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    data, errors = image_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
    raise NotImplementedError


@api.route("/user/<int:id>")
def user(id):
    user = User.query.get_or_404(id)
    return user_schema.jsonify(user), 200

from flask import request, jsonify, g
from ..schemas import image_schema, images_schema
from . import api
from flask_login import login_required
from ..decorators import permission_required
from ..models import Permission, Image, Battle

@api.route("/gallery/", methods=['GET'])
def show():
    images = Image.query.all()
    return images_schema.jsonify(images)

@api.route("/image/<int:id>", methods=['GET'])
def show_image(id):
    image = Image.query.filter_by(id=id).first_or_404()
    return image_schema.jsonify(image)

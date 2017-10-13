from flask import request, send_from_directory, current_app
from flask_restful import Resource, reqparse, fields, marshal_with
from werkzeug.datastructures import FileStorage
from resizeimage import resizeimage
from PIL import Image

from common.auth import authenticate
from common.randomstring import generate as gen_rs

image_filename = {
    "filename": fields.Url('api.imageview')
}

class ImageUpload(Resource):
    @authenticate
    @marshal_with(image_filename)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('image', type=FileStorage, location='files', required=True, help='image file required')
        args = parser.parse_args()

        filename ='%s.jpg' % gen_rs(16)
        try:
            with open(args['image'], 'r+b') as f:
                with Image.open(f) as image:
                    img = resizeimage.resize_cover(image, [400, 400])
                    img.save(current_app.config['IMAGE_UPLOAD_DIRECTORY'] + filename, 'JPEG')
        except:
            raise TypeError("Invalid Image")

        return {"image_id": filename}, 201

class ImageView(Resource):
    @authenticate
    def get(self, image_id):
        return send_from_directory(current_app.config['IMAGE_UPLOAD_DIRECTORY'], image_id)


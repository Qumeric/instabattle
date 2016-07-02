import imghdr
from flask_wtf import Form
from wtforms import FileField, SubmitField
from wtforms import ValidationError
from wtforms.validators import Required

class UploadForm(Form):
    image = FileField("Your Image", validators=[Required()])
    submit = SubmitField("Submit")

    def validate_image(self, field):
        ALLOWED_EXTENSIONS = set(['png', 'jpeg'])
        if imghdr.what(None, h=field.data.read()) not in ALLOWED_EXTENSIONS:
            raise ValidationError("Currently supports only .png and .jpg")
        field.data.seek(0)

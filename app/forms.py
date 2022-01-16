from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, IntegerRangeField
from wtforms.validators import DataRequired

class GachaForm(FlaskForm):
    pity = IntegerField("Pity")
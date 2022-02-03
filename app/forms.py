from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, IntegerRangeField, SubmitField
from wtforms.validators import DataRequired

class GachaForm(FlaskForm):
    pity = IntegerRangeField("Current Pity:", )
    primo = IntegerRangeField("Number Of Primogens:")
    fates = IntegerRangeField("Number of Intertwined Fates:")
    guarantee = BooleanField("Last 5 star was rate up:")
    submit = SubmitField("Calculate")
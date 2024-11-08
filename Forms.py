from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired
from datetime import date, timedelta


# Creating the input form for the calculation
class PheForm(FlaskForm):
    food = SelectField('Food', validators=[DataRequired()], render_kw={"placeholder": "Select food here"}, choices=[])
    weight = FloatField("Weight", validators=[DataRequired()], render_kw={"placeholder": "Enter the weight in grams"})
    date = DateField("Chose the date", default=date.today())
    meals = SelectField('Meals', validators=[DataRequired()], render_kw={"placeholder": "Select meal here"},
                        choices=['Breakfast', 'Lunch', 'Dinner', 'Snack'])
    submit1 = SubmitField("Calculate PHE", name="submit_phe")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.food.choices = [(c.id, c.food) for c in Food.query.all()]

# Creating the input form for the Date
class DateForm(FlaskForm):
    start_date = DateField("Start Date", default=date.today(), validators=[DataRequired()])
    end_date = DateField("End Date", default=date.today() + timedelta(1), validators=[DataRequired()])
    submit = SubmitField("Show History")

# Creating the input form for the database creation
class DataForm(FlaskForm):
    food = StringField("Food", validators=[DataRequired()], render_kw={"placeholder": "Enter food name"})
    phe = FloatField("Phe", validators=[DataRequired()], render_kw={"placeholder": "Enter the Phe in 100 grams"})
    submit = SubmitField("Save")
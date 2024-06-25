from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy import String, Integer, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired
from datetime import date



# Creating the flask app and applying bootstrap
app = Flask(__name__)
app.config['SECRET_KEY'] = 'PHEcalculator123'
Bootstrap5(app)


# Creating the main database for the food data
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_database.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Creating a table for the food intake
class FoodIntake(db.Model):
    __tablename__ = "FoodIntake"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    food: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    phe: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)


# Creating a table for the food
class Food(db.Model):
    __tablename__ = "FoodDB"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    food: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    phe: Mapped[int] = mapped_column(Integer, nullable=False)


with app.app_context():
    db.create_all()


class DateForm(FlaskForm):
    date = DateField("CHOSE DATE", default=date.today())
    submit = SubmitField("Show History")


# Creating the input form for the calculation
class PheForm(FlaskForm):
    food = SelectField('Food', validators=[DataRequired()], render_kw={"placeholder": "Select food here"}, choices=[])
    weight = FloatField("Weight", validators=[DataRequired()], render_kw={"placeholder": "Enter the weight in grams"})
    date = DateField("Chose the date", default=date.today())
    submit1 = SubmitField("Calculate PHE", name="submit_phe")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.food.choices = [(c.id, c.food) for c in Food.query.all()]


# Creating the input form for the database creation
class DataForm(FlaskForm):
    food = StringField("Food", validators=[DataRequired()], render_kw={"placeholder": "Enter food name"})
    phe = FloatField("Phe", validators=[DataRequired()],render_kw={"placeholder": "Enter the Phe in 100 grams"})
    submit = SubmitField("Save")


@app.route("/", methods=["GET","POST"])
def welcome():
    return render_template("welcome.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    phe_form = PheForm()
    date_data = db.session.execute(db.select(FoodIntake).filter_by(date=date.today())).scalars().all()
    total_phe = sum(food_intake.phe for food_intake in date_data)
    if phe_form.validate_on_submit():
        result = db.get_or_404(Food, phe_form.food.data)
        food_taken = FoodIntake(
                        food=result.food,
                        phe=(result.phe * phe_form.weight.data) / 100,
                        weight=phe_form.weight.data,
                        date=phe_form.date.data
                    )
        db.session.add(food_taken)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("index.html", form=phe_form, foods=date_data, phe=total_phe)


@app.route("/input_data", methods=["GET", "POST"])
def data_input():
    result = db.session.execute(db.select(Food))
    foods = result.scalars().all()
    data_form = DataForm()
    if data_form.validate_on_submit():
        new_food = Food(
            food=data_form.food.data,
            phe=data_form.phe.data,
        )
        db.session.add(new_food)
        db.session.commit()
        return redirect(url_for('data_input'))
    return render_template('addFood.html', form=data_form, foods=foods)


@app.route("/history", methods=["GET", "POST"])
def history():
    date_form = DateForm()
    date_data = db.session.execute(db.select(FoodIntake).filter_by(date=date_form.date.data)).scalars().all()
    total_phe = sum(food_intake.phe for food_intake in date_data)
    return render_template("history.html", form=date_form, foods=date_data, phe = total_phe)




if __name__ == "__main__":
    app.run(debug=True, port=5001)

from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from Models import db, FoodIntake, Food
from Forms import PheForm, DateForm, DataForm
import fpdf


# Creating the flask app and applying bootstrap
app = Flask(__name__)
app.config['SECRET_KEY'] = 'PHEcalculator123'
Bootstrap5(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_database.db'
db.init_app(app)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
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
                        date=phe_form.date.data,
                        meals=phe_form.meals.data
                    )
        db.session.add(food_taken)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("calculator.html", form=phe_form, foods=date_data, phe=total_phe)


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
    if date_form.validate_on_submit():
        start_date = date_form.start_date.data
        end_date = date_form.end_date.data
        date_data = db.session.execute(
            db.select(FoodIntake).filter(
                FoodIntake.date.between(start_date, end_date)
            )
        ).scalars().all()

        dates = sorted(set([food.date for food in date_data]))
        date_phe_dict = {}
        for dat in date_data:
            date_var = dat.date
            phe = round(dat.phe, 2)  # Round to 2 decimal places
            if date_var in date_phe_dict:
                date_phe_dict[date_var] = round(date_phe_dict[date_var] + phe, 2)
            else:
                date_phe_dict[date_var] = phe
        return render_template("history.html", form=date_form, foods=date_data, phe=date_phe_dict, dates=dates,
                               sd=start_date, ed=end_date)
    return render_template("history.html", form=date_form)


@app.route("/pdf_convertor/<sd><ed>")
def pdf_convert(sd, ed):
    date_data = db.session.execute(
        db.select(FoodIntake).filter(
            FoodIntake.date.between(sd, ed)
        )
    ).scalars().all()

    # group the data by date
    date_data_grouped = {}
    for item in date_data:
        date = item.date
        if date not in date_data_grouped:
            date_data_grouped[date] = []
        date_data_grouped[date].append(item)
    # create a PDF object
    pdf = fpdf.FPDF()

    # set font and font size
    pdf.set_font("Arial", size=8)

    # initialize table counters
    tables_on_page = 0

    # add the first page
    pdf.add_page()

    # sort the date_data_grouped dictionary by date
    sorted_date_data_grouped = dict(sorted(date_data_grouped.items()))

    # iterate over the sorted date_data_grouped dictionary
    for date, items in sorted_date_data_grouped.items():
        # check if we need to add a new page
        if tables_on_page >= 3:
            pdf.add_page()
            tables_on_page = 0

        # set the date as a title
        pdf.set_font("Arial", size=8)  # reduced font size from 10 to 8
        pdf.cell(0, 6, f"{date}", 1, 1, "C")  # reduced cell height from 10 to 6
        pdf.ln(6)  # reduced line spacing from 10 to 6

        # create a table for each date
        pdf.set_font("Arial", size=6)  # reduced font size from 8 to 6
        pdf.cell(60, 6, "Food", 1, 0, "L")  # reduced cell width and height
        pdf.cell(20, 6, "Weight (g)", 1, 0, "L")  # reduced cell width and height
        pdf.cell(20, 6, "PHE", 1, 1, "L")  # reduced cell width and height

        for item in items:
            # render the food item, weight, and PHE values in the same row
            pdf.cell(60, 6, item.food, 1, 0, "L")  # reduced cell width and height
            pdf.cell(20, 6, str(item.weight), 1, 0, "L")  # reduced cell width and height
            pdf.cell(20, 6, str(item.phe), 1, 1, "L")  # reduced cell width and height

        # add a total PHE row
        total_phe = sum(item.phe for item in items)
        pdf.cell(60, 6, "Total PHE", 1, 0, "L")  # reduced cell width and height
        pdf.cell(20, 6, "", 1, 0, "L")  # reduced cell width and height
        pdf.cell(20, 6, str(total_phe), 1, 1, "L")  # reduced cell width and height

        # add a blank line to separate tables
        pdf.ln(3)  # reduced line spacing from 5 to 3

        # increment table counter
        tables_on_page += 1

    # save the PDF to a file
    pdf.output("Output.pdf", "F")
    flash("Your data has been converted to a PDF file. Thank you!")

    return redirect(url_for('history'))


@app.route("/delete_input/<int:input_id>")
def delete_input(input_id):
    input_to_delete = db.get_or_404(FoodIntake, input_id)
    db.session.delete(input_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, port=5001)

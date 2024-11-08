from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from sqlalchemy import String, Integer, Float

# Creating the main database for the food data
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Creating a table for the food intake
class FoodIntake(db.Model):
    __tablename__ = "FoodIntake"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    food: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    phe: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    meals: Mapped[str] = mapped_column(String, nullable=False)


# Creating a table for the food
class Food(db.Model):
    __tablename__ = "FoodDB"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    food: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    phe: Mapped[int] = mapped_column(Integer, nullable=False)


from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET"])
def get_random_cafe():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    cafe_dict = (random_cafe.__dict__)
    del cafe_dict[next(iter(cafe_dict))]
    print(cafe_dict)
    # return jsonify(cafe={
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "seats": random_cafe.seats,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "has_sockets": random_cafe.has_sockets,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "coffee_price": random_cafe.coffee_price,
    # })
    return jsonify(cafe_dict)

@app.route("/all", methods=["GET"])
def get_all_cafe():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
    all_cafes = result.scalars().all()
    cafe_list = []
    for cafe_data in all_cafes:
        cafe_dict = cafe_data.__dict__
        del cafe_dict[next(iter(cafe_dict))]
        print(cafe_dict)
        cafe_list.append(cafe_dict)
    return jsonify(cafe_list)


@app.route("/search", methods=["GET"])
def get_search_cafe():
    search_result = []
    loc = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == loc))
    all_cafes = result.scalars().all()
    for cafe_data in all_cafes:
        cafe_dict = cafe_data.__dict__
        del cafe_dict[next(iter(cafe_dict))]
        print(loc.lower())
        print(cafe_dict['location'].lower())
        if loc.lower() in cafe_dict['location'].lower():
            print(cafe_dict)
            search_result.append(cafe_dict)
    print(jsonify(search_result))
    if len(search_result) > 0:
        return jsonify(search_result)
    else:
        return jsonify({"error": {"Not Found":"No cafes found for that location"}})



# HTTP GET - Read Record

# HTTP POST - Create Record
@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    name = request.form.get("name")
    map_url = request.form.get("map_url")
    img_url = request.form.get("img_url")
    location = request.form.get("location")
    seats = request.form.get("seats")
    has_toilet = bool(request.form.get("has_toilet"))
    has_wifi = bool(request.form.get("has_wifi"))
    has_sockets = bool(request.form.get("has_sockets"))
    can_take_calls = bool(request.form.get("can_take_calls"))
    coffee_price = request.form.get("coffee_price")
    new_cafe = Cafe(name=name, map_url=map_url, img_url=img_url, location=location,seats=seats, has_toilet=has_toilet, has_wifi=has_wifi, has_sockets=has_sockets, can_take_calls=can_take_calls, coffee_price=coffee_price)
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify({"success": "Cafe added successfully"})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["GET", "POST"])
def update_price(cafe_id):
    new_price = request.args.get('new_price')
    print(new_price)
    print(cafe_id)
    try:
        cafe_to_update = db.get_or_404(Cafe, cafe_id)
    except:
        return jsonify({"error": {"Not Found": "No cafes found for that cafe ID"}})
    else:
        try:
            print(cafe_to_update.coffee_price)
            cafe_to_update.coffee_price = new_price
            db.session.commit()
        except:
            return jsonify({"error": {"Update Failed": "Unable to update the price"}})
    return jsonify({"success": "Cafe updated successfully"})


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["GET", "POST"])
def delete_cafe(cafe_id):
    api_key = request.args.get('api-key')
    if api_key != 'TopSecretAPIKey':
        return jsonify({"error": {"Forbidden": "Sorry, that API key does not have delete access"}}), 403
    else:
        try:
            cafe_to_delete = db.get_or_404(Cafe, cafe_id)
        except:
            return jsonify({"error": {"Not Found": "No cafes found for that cafe ID"}}),404
        else:
            try:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                return jsonify({"success": "Cafe deleted successfully"}), 200
            except:
                return jsonify({"error": {"Delete Failed": "Unable to delete the cafe"}}),404



if __name__ == '__main__':
    app.run(debug=True)

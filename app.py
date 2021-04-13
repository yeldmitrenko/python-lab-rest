from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, post_load
import json
import copy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:12345678@localhost/iot-test-db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Scenery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, unique=False)
    price = db.Column(db.Integer, unique=False)
    installation_time_in_days = db.Column(db.Integer, unique=False)
    film_type = db.Column(db.String(20), unique=False)

    def __init__(self, amount, price, installation_time_in_days, film_type):
        self.amount = amount
        self.price = price
        self.installation_time_in_days = installation_time_in_days
        self.film_type = film_type


class ScenerySchema(ma.Schema):
    amount = fields.Integer()
    price = fields.Integer()
    installation_time_in_days = fields.Integer()
    film_type = fields.Str()

    @post_load
    def make_scenery(self, data, **kwargs):
        return Scenery(**data)


scenery_example_schema = ScenerySchema()
scenery_examples_schema = ScenerySchema(many=True)


@app.route("/scenery", methods=["POST"])
def add_scenery():
    scenery = scenery_example_schema.load(request.json)
    db.session.add(scenery)
    db.session.commit()
    return scenery_example_schema.jsonify(request.json)


@app.route("/scenery", methods=["GET"])
def get_scenery():
    all_scenery = Scenery.query.all()
    result = scenery_examples_schema.dump(all_scenery)
    return jsonify(result)


@app.route("/scenery/<id>", methods=["GET"])
def scenery_detail(id):
    scenery = Scenery.query.get(id)
    if not scenery:
        abort(404)
    return scenery_example_schema.jsonify(scenery)


@app.route("/scenery/<id>", methods=["PUT"])
def update_scenery(id):
    scenery = Scenery.query.get(id)
    if not scenery:
        abort(404)
    old_scenery = copy.deepcopy(scenery)
    scenery.amount = request.json['amount']
    scenery.price = request.json['price']
    scenery.installation_time_in_days = request.json['installation_time_in_days']
    scenery.film_type = request.json['film_type']
    db.session.commit()
    return scenery_example_schema.jsonify(old_scenery)


@app.route("/scenery/<id>", methods=['DELETE'])
def delete_scenery(id):
    scenery = Scenery.query.get(id)
    if not scenery:
        abort(404)
    db.session.delete(scenery)
    db.session.commit()
    return scenery_example_schema.jsonify(scenery)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='127.0.0.1')

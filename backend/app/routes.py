import sqlalchemy as sa
from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash

from app import app, db
from app.models import User


@app.route("/")
@app.route("/index")
def index():
    return {"Hello": "world"}


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = db.session.scalar(sa.select(User).where(User.username == username))

    if user is None:
        return jsonify({"Erreur": "L'utilisateur n'existe pas"}), 401

    if user.checkPassword(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

    return jsonify({"Erreur": "Le mot de passe est invalide"}), 401


@app.route("/inscription", methods=["POST"])
def register():
    username = request.json["username"]
    password = request.json["password"]
    user = User(username=username, password=generate_password_hash(password))  # type: ignore

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"})


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    identity = get_jwt_identity()

    print(identity)

    return jsonify(logged_in_as=identity), 200


# curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"tonuser\",\"password\":\"tonmdp\"}" http://127.0.0.1:5000/login
# curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"tonuser\",\"password\":\"tonmdp\"}" http://127.0.0.1:5000/inscription

# curl -X GET -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2OTQzMjgzNCwianRpIjoiNjdmYjc4NGMtMTRiOS00MzgyLWFkMGMtYjY2ZTM2ZDZlZjExIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRvbnVzZXIiLCJuYmYiOjE3Njk0MzI4MzQsImNzcmYiOiI1YWVlNDc5Zi03YzVmLTQ4MDUtOGVjMy0xMTllMjNhMmY1NTEiLCJleHAiOjE3Njk0MzM3MzR9.hf45MgjAZx5cde6uVbouSrpDur4cGeK3cZoepKqyPdM" http://localhost:5000/protected

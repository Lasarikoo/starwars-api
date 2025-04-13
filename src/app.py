from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///starwars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250))

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250))

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=True)

@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'description': p.description} for p in people])

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get_or_404(people_id)
    return jsonify({'id': person.id, 'name': person.name, 'description': person.description})

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'description': p.description} for p in planets])

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify({'id': planet.id, 'name': planet.name, 'description': planet.description})

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username} for u in users])

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id is required as query param'}), 400
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    result = []
    for fav in favorites:
        if fav.planet_id:
            planet = Planet.query.get(fav.planet_id)
            result.append({'type': 'planet', 'name': planet.name})
        elif fav.people_id:
            person = People.query.get(fav.people_id)
            result.append({'type': 'people', 'name': person.name})
    return jsonify(result)

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id is required as query param'}), 400
    new_fav = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({'message': 'Planet added to favorites'}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id is required as query param'}), 400
    new_fav = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({'message': 'People added to favorites'}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.args.get('user_id', type=int)
    fav = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'message': 'Planet favorite deleted'})
    return jsonify({'message': 'Favorite not found'}), 404

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = request.args.get('user_id', type=int)
    fav = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'message': 'People favorite deleted'})
    return jsonify({'message': 'Favorite not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

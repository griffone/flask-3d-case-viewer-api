from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# DB Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://crud_user:123456@localhost/crud_game'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Platform Model
class Platform(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Item (Game) Model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    platform = db.relationship('Platform', backref='items')

# Ruta para listar todos los juegos
@app.route('/games', methods=['GET'])
def list_games():
    items = Item.query.all()
    games = [
        {
            "id": item.id,
            "title": item.title,
            "score": item.score,
            "platform": {
                "id": item.platform.id,
                "name": item.platform.name
            },
            "image_url": item.image_url
        }
        for item in items
    ]
    return jsonify(games), 200

# Ruta para listar todas las plataformas
@app.route('/platforms', methods=['GET'])
def list_platforms():
    platforms = Platform.query.all()
    platforms_data = [{"id": platform.id, "name": platform.name} for platform in platforms]
    return jsonify(platforms_data), 200

# Ruta para agregar un nuevo juego
@app.route('/games', methods=['POST'])
def add_game():
    data = request.get_json()
    title = data.get('title')
    score = data.get('score')
    platform_id = data.get('platform_id')
    image_url = data.get('image_url')

    if not title or not score or not platform_id:
        return jsonify({"error": "Missing required fields"}), 400

    item = Item(title=title, score=score, platform_id=platform_id, image_url=image_url)
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Game added successfully", "game": {
        "id": item.id,
        "title": item.title,
        "score": item.score,
        "platform_id": item.platform_id,
        "image_url": item.image_url
    }}), 201

# Ruta para agregar una nueva plataforma
@app.route('/platforms', methods=['POST'])
def add_platform():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({"error": "Platform name is required"}), 400

    platform = Platform(name=name)
    db.session.add(platform)
    db.session.commit()
    return jsonify({"message": "Platform added successfully", "platform": {
        "id": platform.id,
        "name": platform.name
    }}), 201

# Ruta para eliminar un juego
@app.route('/games/<int:id>', methods=['DELETE'])
def delete_game(id):
    item = Item.query.get(id)
    if not item:
        return jsonify({"error": "Game not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Game deleted successfully"}), 200

# Ruta para eliminar una plataforma
@app.route('/platforms/<int:id>', methods=['DELETE'])
def delete_platform(id):
    platform = Platform.query.get(id)
    if not platform:
        return jsonify({"error": "Platform not found"}), 404

    db.session.delete(platform)
    db.session.commit()
    return jsonify({"message": "Platform deleted successfully"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum as SQLEnum
from enum import Enum
import os

app = Flask(__name__)


# DB MODELS

db = SQLAlchemy()

class SimilarityClass(Enum):
    similar = 1
    dissimilar = 2

annotations = db.Table("annotations",
    db.Column("annotator_id", db.Integer, db.ForeignKey("annotator.id"), primary_key=True),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
    db.Column("value", SQLEnum(SimilarityClass))
)

class Post(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String)
    body: str = db.Column(db.String)
    annotations = db.relationship('Annotator', secondary=annotations, lazy='subquery',
        backref=db.backref('posts', lazy=True))

class Annotator(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String)


@app.route("/ping")
def ping():
    return "pong"

@app.route("/annotator", methods=["GET", "POST"])
def annotators(annotator_id=None):
    if request.method == "GET":
        return _annotators_get(annotator_id)
    else:
        return _annotators_post()

def _annotators_get(annotator_id):
    if annotator_id is not None:
        return jsonify(Annotator.query.get(annotator_id))
    return jsonify(Annotator.query.all())

def _annotators_post():
    pass

# DB CONFIG

host = os.getenv("POSTGRES_HOST")
user = os.getenv("POSTGRES_USER")
pswd = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")

app.config.update({
    "SQLALCHEMY_DATABASE_URI": f"postgresql+psycopg2://{user}:{pswd}@{host}/{db_name}",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
})

def seed():
    ann1 = Annotator(name="Alex")
    ann2 = Annotator(name="Rivas")
    ann3 = Annotator(name="Korn")

    db.create_all([ann1,ann2,ann3])

db.init_app(app)

if os.getenv("ENV") == "dev":
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed()



# API

@app.route("/annotation", methods=["GET", "POST"])
def annotation():
    if request.method == "GET":
        return _annotation_get()
    else:
        return _annotation_post()

def _annotation_get():
    pass

def _annotation_post():
    pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
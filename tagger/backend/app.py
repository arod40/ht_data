from dataclasses import dataclass
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum as SQLEnum
from enum import Enum
import os
from datetime import datetime

app = Flask(__name__)

# DB CONFIG
db = SQLAlchemy()

host = os.getenv("POSTGRES_HOST")
user = os.getenv("POSTGRES_USER")
pswd = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql+psycopg2://{user}:{pswd}@{host}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# DB MODELS


class SimilarityClass(str, Enum):
    similar = "similar"
    dissimilar = "dissimilar"


@dataclass
class Annotator(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    access_code: str = db.Column(db.String, unique=True)
    annotations = db.relationship("Annotation", back_populates="annotator")


@dataclass
class Post(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    external_reference: str = db.Column(db.String)
    title: str = db.Column(db.String)
    body: str = db.Column(db.String)


@dataclass
class Annotation(db.Model):
    left_post_id = db.Column(db.Integer, db.ForeignKey("post.id"), primary_key=True)
    right_post_id = db.Column(db.Integer, db.ForeignKey("post.id"), primary_key=True)
    annotator_id = db.Column(
        db.Integer, db.ForeignKey("annotator.id"), primary_key=True
    )
    value: SimilarityClass = db.Column(SQLEnum(SimilarityClass))
    date: datetime = db.Column(db.DateTime())
    left_post: Post = db.relationship(
        "Post",
        backref="annotations_as_left",
        foreign_keys=[left_post_id],
    )
    right_post: Post = db.relationship(
        "Post",
        backref="annotations_as_right",
        foreign_keys=[right_post_id],
    )
    annotator: Annotator = db.relationship("Annotator", back_populates="annotations")


db.init_app(app)


def seed():
    ann1 = Annotator(access_code="1")
    ann2 = Annotator(access_code="2")
    ann3 = Annotator(access_code="3")

    p1 = Post(
        body="""
😄body1body1body1body1body1body1\n
body1body1body1body1body1body1body1body1body\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
😄body1body1body1body1body1body1\n
body1body1body1body1body1body1body1body1body\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
😄body1body1body1body1body1body1\n
body1body1body1body1body1body1body1body1body\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1\n
1body1body1body1body1body1body1body1body1body1body1body1
""",
        title="title1",
        external_reference="post1",
    )
    p2 = Post(body="body2", title="title2", external_reference="post2")
    p3 = Post(body="body3", title="title3", external_reference="post3")

    annotation121 = Annotation()
    annotation121.annotator = ann1
    annotation121.left_post = p1
    annotation121.right_post = p2
    annotation121.value = SimilarityClass.similar

    annotation231 = Annotation()
    annotation231.annotator = ann1
    annotation231.left_post = p2
    annotation231.right_post = p3
    annotation231.value = SimilarityClass.dissimilar

    annotation131 = Annotation()
    annotation131.annotator = ann1
    annotation131.left_post = p1
    annotation131.right_post = p3

    annotation232 = Annotation()
    annotation232.annotator = ann2
    annotation232.left_post = p2
    annotation232.right_post = p3
    annotation232.value = SimilarityClass.dissimilar

    annotation132 = Annotation()
    annotation132.annotator = ann2
    annotation132.left_post = p1
    annotation132.right_post = p3
    annotation132.value = SimilarityClass.similar

    db.session.add_all(
        [
            ann1,
            ann2,
            ann3,
            p1,
            p2,
            annotation121,
            annotation231,
            annotation232,
            annotation132,
        ]
    )
    db.session.commit()


if os.getenv("ENV") == "dev":
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed()
else:
    with app.app_context():
        db.drop_all()
        db.create_all()

# API


@app.route("/ping")
def ping():
    return "pong"


@app.route("/annotator", methods=["GET", "POST"], defaults={"annotator_id": None})
@app.route("/annotator/<annotator_id>", methods=["GET", "PUT", "DELETE"])
def annotators(annotator_id=None):
    if request.method == "GET":
        return _annotators_get(annotator_id)
    elif request.method == "POST":
        return _annotators_post()
    elif request.method == "PUT":
        return _annotators_put(annotator_id)
    else:
        return _annotators_delete(annotator_id)


def _annotators_get(annotator_id):
    if annotator_id is not None:
        return jsonify(Annotator.query.get(annotator_id))
    return jsonify(Annotator.query.all())


def _annotators_post():
    ann_json = request.get_json()
    annotator = Annotator(access_code=ann_json["access_code"])

    db.session.add_all([annotator])
    db.session.commit()

    return jsonify(annotator), 201


def _annotators_put(annotator_id):
    ann_json = request.get_json()
    annotator = Annotator.query.get(annotator_id)
    annotator.access_code = ann_json["access_code"]

    db.session.add_all([annotator])
    db.session.commit()

    return jsonify(annotator), 200


def _annotators_delete(annotator_id):
    db.session.delete(Annotator.query.get(annotator_id))
    db.session.commit()

    return "", 204


@app.route("/post", methods=["GET", "POST"], defaults={"post_id": None})
@app.route("/post/<post_id>", methods=["GET", "PUT", "DELETE"])
def posts(post_id=None):
    if request.method == "GET":
        return _posts_get(post_id)
    elif request.method == "POST":
        return _posts_post()
    elif request.method == "PUT":
        return _posts_put(post_id)
    else:
        return _posts_delete(post_id)


def _posts_get(post_id):
    if post_id is not None:
        return jsonify(Post.query.get(post_id))
    return jsonify(Post.query.all())


def _posts_post():
    ann_json = request.get_json()
    post = Post(body=ann_json["body"], title=ann_json["title"])

    db.session.add_all([post])
    db.session.commit()

    return jsonify(post), 201


def _posts_put(post_id):
    ann_json = request.get_json()
    post = Post.query.get(post_id)
    post.body = ann_json["body"]
    post.title = ann_json["title"]

    db.session.add_all([post])
    db.session.commit()

    return jsonify(post), 200


def _posts_delete(post_id):
    db.session.delete(Post.query.get(post_id))
    db.session.commit()

    return "", 204


@app.route("/post/bulk", methods=["POST"])
def posts_bulk():
    return _posts_bulk_create()


def _posts_bulk_create():
    posts_json_list = request.get_json()
    posts = []
    for post_json in posts_json_list:
        post = Post(body=post_json["body"], title=post_json["title"])
        posts.append(post)

    db.session.add_all(posts)
    db.session.commit()

    return "All posts added sucessfully", 201


@app.route("/post/<post_id>/annotations", methods=["GET"])
def post_annotations(post_id):
    return _annotations_by_post(post_id)


def _annotations_by_post(post_id):
    post = Post.query.get(post_id)
    return jsonify(
        {"as_left": post.annotations_as_left, "as_right": post.annotations_as_right}
    )


@app.route("/annotator/<annotator_id>/annotations", methods=["GET"])
def annotator_annotations(annotator_id):
    return _annotations_by_annotator(annotator_id)


def _annotations_by_annotator(annotator_id):
    return jsonify(Annotator.query.get(annotator_id).annotations)


@app.route(
    "/annotation",
    methods=["GET", "POST"],
    defaults={"left_post_id": None, "right_post_id": None, "annotator_id": None},
)
@app.route(
    "/annotation/<left_post_id>/<right_post_id>/<annotator_id>",
    methods=["GET", "PUT", "DELETE"],
)
def annotations(left_post_id=None, right_post_id=None, annotator_id=None):
    if request.method == "GET":
        return _annotations_get(left_post_id, right_post_id, annotator_id)
    elif request.method == "POST":
        return _annotations_post()
    elif request.method == "PUT":
        return _annotations_put(left_post_id, right_post_id, annotator_id)
    else:
        return _annotations_delete(left_post_id, right_post_id, annotator_id)


def _annotations_get(left_post_id, right_post_id, annotator_id):
    if None not in [left_post_id, right_post_id, annotator_id]:
        return jsonify(
            Annotation.query.get((left_post_id, right_post_id, annotator_id))
        )
    return jsonify(Annotation.query.all())


def _annotations_post():
    ann_json = request.get_json()
    annotation = Annotation(
        left_post_id=ann_json["left_post_id"],
        right_post_id=ann_json["right_post_id"],
        annotator_id=ann_json["annotator_id"],
        value=SimilarityClass[ann_json["value"]],
        date=datetime.now(),
    )

    db.session.add_all([annotation])
    db.session.commit()

    return jsonify(annotation), 201


def _annotations_put(left_post_id, right_post_id, annotator_id):
    ann_json = request.get_json()
    annotation = Annotation.query.get((left_post_id, right_post_id, annotator_id))
    annotation.value = SimilarityClass[ann_json["value"]]
    annotation.date = datetime.now()

    db.session.add_all([annotation])
    db.session.commit()

    return jsonify(annotation), 200


def _annotations_delete(left_post_id, right_post_id, annotator_id):
    db.session.delete(Annotation.query.get((left_post_id, right_post_id, annotator_id)))
    db.session.commit()

    return "", 204


@app.route("/bulk_populate", methods=["POST"])
def bulk_populate():
    return _bulk_populate()


def _bulk_populate():
    data = request.get_json()
    annotators = []
    for annotator_json in data["annotators"]:
        annotators.append(
            Annotator(access_code=annotator_json["access_code"])
        )
    posts = []
    for post_json in data["posts"]:
        posts.append(Post(title=post_json["title"], body=post_json["body"]))

    db.session.add_all(posts + annotators)
    db.session.commit()

    annotations = []
    for annotation_json in data["annotations"]:
        annotation = Annotation(
            left_post_id=posts[annotation_json["left_post_index"]].id,
            right_post_id=posts[annotation_json["right_post_index"]].id,
            annotator_id=annotators[annotation_json["annotator_index"]].id,
            value=annotation_json.get("value", None),
            date=datetime.now(),
        )
        annotations.append(annotation)

    db.session.add_all(annotations)
    db.session.commit()

    return "All annotations added sucessfully", 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

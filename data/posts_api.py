import flask
from flask import jsonify, request, make_response
from sqlalchemy.exc import IntegrityError


from . import db_session
from .posts import Post, AnonimPost

blueprint = flask.Blueprint(
    'posts_api',
    __name__,
    template_folder='templates'
)
fields = 'id', 'author_id', 'title', 'content', 'created_date'  # все поля
required_fields = 'id', 'author_id', 'title'  # обязательные поля


@blueprint.route('/api/posts')
def get_posts():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()
    return jsonify(
        {
            'posts':
                [item.to_dict(only=fields)
                 for item in posts]
        }
    )


@blueprint.route('/api/posts/<int:post_id>', methods=['GET'])
def get_one_post(post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).get(post_id)
    if not post:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'post': post.to_dict(only=fields)
        }
    )


@blueprint.route('/api/posts', methods=['POST'])
def create_post():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in required_fields):
        return make_response(jsonify({'error': 'Bad request'}), 400)

    db_sess = db_session.create_session()

    post = Post()
    post.author_id = request.json.get('author_id')
    post.title = request.json.get('title')
    post.content = request.json.get('content')
    post.created_date = request.json.get('created_date')
    try:
        db_sess.add(post)
        db_sess.commit()
    except IntegrityError:
        return make_response(jsonify({'error': 'Error from database'}, 500))

    return make_response(jsonify({'success': 'OK'}), 200)


@blueprint.route('/api/anonim_posts', methods=['POST'])
def create_anonim_post():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif 'title' not in request.json and 'link' not in request.json:
        return make_response(jsonify({'error': 'Bad request'}), 400)

    db_sess = db_session.create_session()

    post = AnonimPost()
    post.title = request.json.get('title')
    post.content = request.json.get('content')
    post.link = request.json.get('link')

    try:
        db_sess.add(post)
        db_sess.commit()
    except IntegrityError:
        return make_response(jsonify({'error': 'Error from database'}, 500))

    return make_response(jsonify({'success': 'OK'}), 200)


@blueprint.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).get(post_id)
    if not post:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(post)
    db_sess.commit()
    return make_response(jsonify({'success': 'OK'}), 200)


@blueprint.route('/api/users', methods=['PUT'])
def edit_post():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif 'id' not in request.json:
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()

    post = db_sess.query(Post).get(request.json["id"])
    if not post:
        return make_response(jsonify({'error': 'Not found'}), 404)

    post.author_id = request.json.get('author_id')
    post.title = request.json.get('title')
    post.content = request.json.get('content')
    post.created_date = request.json.get('created_date')

    db_sess.add(post)
    db_sess.commit()
    return make_response(jsonify({'success': 'OK'}), 200)

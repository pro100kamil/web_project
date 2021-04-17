import flask
from flask import jsonify, request

from . import db_session
from .users import User

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)
fields = 'id', 'surname', 'name', 'about', 'email'  # все поля
required_fields = 'surname', 'name', 'email'  # обязательные поля


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=fields)
                 for item in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'user': user.to_dict(only=fields)
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in required_fields):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    if 'email' in request.json:
        if db_sess.query(User).filter(
                User.email == request.json['email']).first() is not None:
            return jsonify({'error': 'Email already exists'})
    user = User()
    user.email = request.json.get('email')
    user.surname = request.json.get('surname')
    user.name = request.json.get('name')
    user.about = request.json.get('about')
    user.set_password(request.json.get('password'))
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users', methods=['PUT'])
def edit_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif 'id' not in request.json:
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()

    user = db_sess.query(User).get(request.json["id"])
    if not user:
        return jsonify({'error': 'Not found'})
    if db_sess.query(User).filter(
            User.email == request.json.get('email')).first() is not None:
        return jsonify({'error': 'Email already exists'})

    user.email = request.json.get('email')
    user.surname = request.json.get('surname')
    user.name = request.json.get('name')
    user.about = request.json.get('about')

    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})

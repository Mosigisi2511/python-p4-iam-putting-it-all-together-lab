#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_user = User(
                username=data['username'],
                password=data['password'],
                image_url=data.get('image_url', ''),
                bio=data.get('bio', '')
            )
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return jsonify({
                'id': new_user.id,
                'username': new_user.username,
                'image_url': new_user.image_url,
                'bio': new_user.bio
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Username already exists."}), 422
        except Exception as e:
            return jsonify({"error": str(e)}), 400


class CheckSession(Resource):
    def get(self):
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            return jsonify({
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }), 200
        return jsonify({"error": "Unauthorized"}), 401


class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            session['user_id'] = user.id
            return jsonify({
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }), 200
        return jsonify({"error": "Invalid username or password"}), 401


class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return '', 204


class RecipeIndex(Resource):
    def get(self):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        recipes = Recipe.query.all()
        return jsonify([recipe.to_dict() for recipe in recipes]), 200

    def post(self):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.get_json()
        new_recipe = Recipe(
            title=data['title'],
            instructions=data['instructions'],
            minutes_to_complete=data['minutes_to_complete'],
            user_id=session['user_id']
        )
        db.session.add(new_recipe)
        db.session.commit()
        return jsonify(new_recipe.to_dict()), 201


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)

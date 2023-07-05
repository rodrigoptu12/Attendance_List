from flask import request, jsonify, session
from flask_restful import Resource
from backend.decorators.decorators import require_login
from models.user import User
from models import db
from flask import Blueprint

#Criar o resto do CRUD e testar
#Depois de finalizar, voltar e vê se consigo deixar o isTeacher apenas para o servidor alterar e definir
#Testar o flake8 para deixar o código com um padrão ? (Pesquisar oq é isso)

user_bp = Blueprint('user', __name__)

class UserController(Resource):
    @staticmethod
    @require_login
    @user_bp.route('/users', methods=['GET'])
    def get_all_users():
        user_session = User.query.get(session.get('user_id'))
        if not user_session.is_teacher == True:
            return jsonify({'error': 'User without permition'}), 404
        users = User.query.all()
        return jsonify([user.serialize() for user in users])
    
    @staticmethod
    @require_login
    @user_bp.route('/users/<int:user_id>', methods=['GET'])    
    def get_user(user_id):
        user = User.query.get(user_id)
        user_session_id = session.get('user_id')
        if not user.user_id == user_session_id:
            return jsonify({'error': 'User without permition'}), 404
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.serialize())

    @staticmethod
    @user_bp.route('/users', methods=['POST'])
    def create_user():
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        registration = data.get('registration')
        is_teacher = data.get('is_teacher', False)

        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if not confirm_password:
            return jsonify({'error': 'Confirm password is required'}), 400
        
        if not registration:
            return jsonify({'error': 'Registration is required'}), 400
        
        if not (User.query.filter_by(email=email).first() is None):
            return jsonify({'error': 'Email already registered'}), 400
        
        if not (User.query.filter_by(registration=registration).first() is None):
            return jsonify({'error': 'Registration already registered'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Password and confirm_password are diferrent'}), 400

        user = User(name=name, email=email, password=password, registration=registration, is_teacher=is_teacher)
        db.session.add(user)
        db.session.commit()

        return jsonify(user.serialize()), 201

    @staticmethod
    @require_login
    @user_bp.route('/users/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        new_password = data.get('new_password')
        registration = data.get('registration')

        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if not (User.query.filter_by(email=email).first() is None):
            return jsonify({'error': 'Email already registered'}), 400
        
        if not (User.query.filter_by(registration=registration).first() is None):
            return jsonify({'error': 'Registration already registered'}), 400
        
        if not user.verify_password(password):
            return jsonify({'error': 'Wrong passwod'}), 400
        
        user.name = name
        user.email = email

        if new_password:
            user.password(new_password)
          
        if registration:
            user.registration = registration
          
        db.session.commit()

        return jsonify(user.serialize())

    @staticmethod
    @require_login
    @user_bp.route('/users/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        user = User.query.get(user_id)
        user_session = session.get('user_id')
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_teacher == True and not user.user_id == user_session :
            return jsonify({'message': 'User without permition'})

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'User deleted'})
    
    @staticmethod
    @user_bp.route('/login', methods=['POST'])
    def login():
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        user = User.query.filter_by(email=email).first()

        if not user or not user.verify_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Autenticação bem-sucedida, armazene o ID do usuário na sessão
        session['user_id'] = user.userId

        return jsonify({'message': 'Login successful'})

    @staticmethod
    @require_login
    @user_bp.route('/logout', methods=['POST'])
    def logout():
        session.pop('user_id', None)
        return jsonify({'message': 'Logged out'})

    @staticmethod
    @require_login
    @user_bp.route('/me', methods=['GET'])
    def get_current_user():
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return jsonify(user.serialize())
        
        return jsonify({'error': 'Not logged in'}), 401
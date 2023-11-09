from flask_restful import Api, Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from secrets import compare_digest
from blocklist import BLOCKLIST
from resources.user_level import role_required
import traceback
from flask import make_response, render_template


atributos_registro = reqparse.RequestParser()
atributos_registro.add_argument('login', type=str, required=True, help="The field 'login' cannot be blank")
atributos_registro.add_argument('senha', type=str, required=True, help="The field 'senha' cannot be blank")
atributos_registro.add_argument('tipo_usuario', type=int, required=True, help="The field 'tipo_usuario' cannot be blank")
atributos_registro.add_argument('email', type=str)
atributos_registro.add_argument('ativado', type=bool)


atributos_login = reqparse.RequestParser()
atributos_login.add_argument('login', type=str, required=True, help="The field 'login' cannot be blank")
atributos_login.add_argument('senha', type=str, required=True, help="The field 'senha' cannot be blank")



#Classe do elemento
class UserList(Resource):
    @jwt_required()
    def get(self, user_id=None):
        if user_id:
            user = UserModel.find_user(user_id)
            if user:
                return user.json()
            return {'message': 'User not found'}, 404
        else:
            users = UserModel.obter_todos_usuarios()
            users_list = [user.json() for user in users]
            return {'users': users_list}, 200

    @jwt_required()
    @role_required(2,3)
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
                return {'message': "User with ID {} is deleted".format(user_id)}, 200
            except:
                return {'message': 'An internal error occurred trying to delete User'}, 500
        return {'message': 'User not found'}, 404


class UserRegister(Resource):
    def post(self):
        dados = atributos_registro.parse_args()
        if not dados.get('email') or dados.get("email") is None:
            return {'message': 'The field "email" cannot be left blank.'}, 400

        if not UserModel.is_valid_email(dados['email']):
            return {'message': 'O e-mail fornecido não é válido.'}, 400

        if UserModel.find_by_email(dados['email']):
            return {"message": "Email '{}' already exists".format(dados['email'])}, 400
        
        if UserModel.find_by_login(dados['login']):
            return {"message": "Login '{}' already exists".format(dados['login'])}, 400

        # Verifique se o tipo de usuário é um valor válido (1, 2 ou 3)
        if dados['tipo_usuario'] not in [1, 2, 3]:
            return {"message": "Invalid tipo_usuario. It should be 1 for user, 2 for customer, or 3 for admin"}, 400

        user = UserModel(**dados)
        user.ativado = False
        try:
            user.save_user()
            user.send_confirmation_email()
        except:
            user.delete_user()
            traceback.print_exc()
            return {'message': 'An internal server error has ocurred.'}, 500
        return {'message': 'User {} created successfully!'.format(dados['login'])}, 201


class UserLogin(Resource):
    @classmethod
    def post(cls):
        dados = atributos_login.parse_args()
        user = UserModel.find_by_login(dados['login'])
        
        if user and compare_digest(user.senha, dados['senha']):
            if user.ativado:
                token_de_acesso = create_access_token(identity=user.user_id)
                return {'access_token': token_de_acesso}, 200
            return {'message':'User not confirme.'}, 400
        return {'message': 'The username or password is incorrect.'}, 401


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti']
        BLOCKLIST.add(jwt_id)
        return {'message': "logged out successfully"},200

class UserConfirm(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_user(user_id)
        
        if not user:
            return {"message": "User id '{}' not found.".format(user_id)}, 404
        
        user.ativado = True
        user.save_user()
        #return{"message": "User id '{}' confirmed sucessfully.".format(user_id)}, 200
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('user_confirm.html', email=user.email, usuario=user.login),200 , headers)
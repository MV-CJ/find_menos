from flask import Flask, jsonify
from flask_restful import Api
from resources.hotel import Hoteis, Hotel
from resources.usuario import UserList, UserRegister, UserLogin, UserLogout, UserConfirm
from resources.site import Site, Sites
from flask_jwt_extended import JWTManager
from blocklist import BLOCKLIST


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'DontTellAnyone'
app.config['JWT_BLOCKLIST_ENABLED'] = True
api = Api(app)
jwt = JWTManager(app)


@app.before_request
def cria_banco():
    banco.create_all()


@jwt.token_in_blocklist_loader
def verifica_blocklist(self,token):
    return token['jti'] in BLOCKLIST


@jwt.revoked_token_loader
def access_token_invalidation(jwt_header, jwt_payload):
    return jsonify(msg=f"You have been logged out!"), 401

#rota hoteis
api.add_resource(Hoteis, '/hoteis')
api.add_resource(Hotel, '/hoteis/<string:hotel_id>')
#rota usuarios
api.add_resource(UserList, '/usuarios','/usuarios/<int:user_id>')
#rota cadastro
api.add_resource(UserRegister, '/cadastro')
#rota usuarios
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
#rota sites
api.add_resource(Sites, '/sites')
api.add_resource(Site, '/sites/<string:url>')

api.add_resource(UserConfirm, '/confirmacao/<int:user_id>')

if __name__ == '__main__':
    from sql_alchemy import banco
    banco.init_app(app)
    app.run(debug=True)
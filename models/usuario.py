from sql_alchemy import banco
from flask import request,url_for
from requests import post 
import re



#Construtor
class UserModel(banco.Model):
    __tablename__ = 'usuarios'
    
    user_id = banco.Column(banco.Integer, primary_key=True)
    login = banco.Column(banco.String(40), nullable=False, unique=True)
    senha = banco.Column(banco.String(40), nullable=False)
    tipo_usuario = banco.Column(banco.Integer, nullable=False)  # Novo campo para o tipo de usuário
    email = banco.Column(banco.String(80), nullable=False, unique=True)
    ativado = banco.Column(banco.Boolean, default=False)
    
    # Variáveis estáticas para configuração do Mailgun
    MAILGUN_API_KEY = 'a4f75b0d770a2ef97218186d40803281-8c9e82ec-d900b43c'
    MAILGUN_DOMAIN = 'sandbox99bce699cd1b49eca2c6e0e5e39938ab.mailgun.org'
    FROM_TITLE = 'NO-REPLAY'
    FROM_EMAIL = 'no-replay@findmenos.com'

    @staticmethod
    def set_email_config(api_key, domain, from_title, from_email):
        UserModel.MAILGUN_API_KEY = api_key
        UserModel.MAILGUN_DOMAIN = domain
        UserModel.FROM_TITLE = from_title
        UserModel.FROM_EMAIL = from_email
        
    @staticmethod
    def is_valid_email(email):
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return True
        return False

    def __init__(self, login, senha, tipo_usuario, ativado, email):
        self.login = login
        self.senha = senha
        self.tipo_usuario = tipo_usuario
        self.email = email
        self.ativado = ativado

        
    def send_confirmation_email(self):
        link = request.url_root[:-1] + url_for('userconfirm', user_id=self.user_id)
        api_key = UserModel.MAILGUN_API_KEY  # Usando a variável de classe
        domain = UserModel.MAILGUN_DOMAIN  # Usando a variável de classe
        from_title = UserModel.FROM_TITLE  # Usando a variável de classe
        from_email = UserModel.FROM_EMAIL  # Usando a variável de classe
        if not (api_key and domain and from_title and from_email):
            raise ValueError("Configuração do Mailgun não definida")
        
        return post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": f"{from_title} <{from_email}>",
                "to": self.email,
                "subject": "Confirmação de Cadastro FindMenos",
                "text": f"Confirme seu cadastro clicando no link a seguir: {link}",
                "html": f"<html><p>Confirme seu cadastro clicando no link a seguir: <a href='{link}'>CONFIRMAR EMAIL</a></p></html>"
            }
        )

    def json(self):
        return {
                'user_id': self.user_id,
                'login': self.login,
                'tipo_usuario': self.tipo_usuario,
                'email': self.email,
                'ativado': self.ativado
        }


    @classmethod
    def find_user(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        if user:
            return user
        return None


    @classmethod
    def find_by_login(cls, login):
        user = cls.query.filter_by(login=login).first()
        if user:
            return user
        return None


    @classmethod
    def find_by_email(cls, email):
        user = cls.query.filter_by(email=email).first()
        if user:
            return user
        return None


    @classmethod
    def obter_todos_usuarios(cls):
        return cls.query.all()  


    def save_user(self):
        banco.session.add(self)
        banco.session.commit()


    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()
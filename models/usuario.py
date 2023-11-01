from sql_alchemy import banco

#Construtor
class UserModel(banco.Model):
    __tablename__ = 'usuarios'
    
    user_id = banco.Column(banco.Integer, primary_key=True)
    login = banco.Column(banco.String(40))
    senha = banco.Column(banco.String(40))
    tipo_usuario = banco.Column(banco.Integer)  # Novo campo para o tipo de usuário


    def __init__(self, login, senha, tipo_usuario):
        self.login = login
        self.senha = senha
        self.tipo_usuario = tipo_usuario


    def json(self):
        return {
                'user_id': self.user_id,
                'login': self.login,
                'tipo_usuario': self.tipo_usuario
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
    def obter_todos_usuarios(cls):
        return cls.query.all()  


    def save_user(self):
        banco.session.add(self)
        banco.session.commit()


    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()
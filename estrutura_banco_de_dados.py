from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#criar api flask
app = Flask(__name__)

#criar instancia de sqlAlchemy
app.config['SECRET_KEY'] = 'FSD2323f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:HikV4efvYgbUD9hDvYpG@containers-us-west-191.railway.app:5943/railway'


db = SQLAlchemy(app)
db:SQLAlchemy


#definindo estrutura
class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor')) # nome da tabela

#autor
#tabela autor
class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem') # nome da classe no relacionamento

'''
with app.app_context():
    # executando
    db.drop_all()
    db.create_all()

    #usuarios administradores
    autor = Autor(nome='edgar', email='@gmail.com', senha='', admin=True)
    db.session.add(autor)
    db.session.commit()
'''

def inicializar_banco():
    with app.app_context():
    # executando
        db.drop_all()
        db.create_all()

        #usuarios administradores
        autor = Autor(nome='edgar', email='edgar@gmail.com', senha='123456', admin=True)
        db.session.add(autor)
        db.session.commit()

if __name__=="__main__":
    inicializar_banco()
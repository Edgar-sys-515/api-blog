from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import app, Autor, Postagem, db
import jwt
import json
from datetime import datetime,timedelta
from functools import wraps
import os

def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        #verificando se o token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem':'Token não foi incluído'}, 401)
        #se temos um token tem q se validado no banco de dados
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'mensagem': 'Token é inválido'}, 401)
        return f(autor, *args, **kwargs)
    return decorated



@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401,{'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido', 401,{'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor':usuario.id_autor, 'exp':datetime.utcnow()+timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return make_response('Login inválido', 401,{'WWW-Authenticate': 'Basic realm="Login obrigatório"'})






# rota padrao get - GET http://localhost
@app.route('/')
@token_obrigatorio
def obter_postagens(autor):
    postagens = Postagem.query.all()  # pegando do banco de dados 
    list_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        list_postagens.append(postagem_atual)
    return jsonify({'postagens': list_postagens})


# get com ID - GET http://localhost:5000/postagem/1
@app.route('/postagem/<int:indice>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_indice(autor, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    postagem_atual = {}
    try:
        postagem_atual['titulo'] = postagem.titulo
    except:
        pass
    postagem_atual['id_autor'] = postagem.id_autor

    return jsonify({'postagens': postagem_atual})



#criar nova postagem - POSt
@app.route('/postagem', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(
        titulo=nova_postagem['titulo'], id_autor=nova_postagem['id_autor'])

    db.session.add(postagem)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem criada com sucesso'})


#put alterar postagem existente
@app.route('/postagem/<int:indice>', methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor, id_postagem):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    try:
        postagem.titulo = postagem_alterada['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_alterada['id_autor']
    except:
        pass

    db.session.commit()
    return jsonify({'mensagem': 'Postagem alterada com sucessso'})

# exluir, delete
@app.route('/postagem/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def excluindo_registro(autor, id_postagem):
    postagem_a_ser_exluida = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem_a_ser_exluida:
        return jsonify({'mensagem': 'Não foi encontrada postagem com esse ID'})
    db.session.delete(postagem_a_ser_exluida)
    db.session.commit()
    return jsonify({'mensagem':'postagem excluída com sucesso.'})    


# continuando agora por autor e postagem


@app.route('/autores/' or '/autores')
@token_obrigatorio
def obter_autores(autor):
    autores = Autor.query.all()  # pegando do banco de dados 
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        lista_de_autores.append(autor_atual)
    return jsonify({'autores':lista_de_autores})

@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autor_id(autor, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first() # banco de dados
    if not autor:
        return jsonify(f'Autor de id {id_autor} não foi encontrado.')
    
    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email
    return jsonify( {'autor' : autor_atual})


@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
    print("Deu ruim")
    novo_autor = request.get_json() # pegando informação da request passado para se incluido no bd
    autor = Autor(nome=novo_autor['nome'], senha=novo_autor['senha'],email=novo_autor['email'])
    db.session.add(autor)
    db.session.commit()
    return jsonify('Usuario criado com sucesso', 200)

@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor, id_autor):
    autor_a_ser_alterador = request.get_json() # pegando a informação do request, usuário que será alterado
    autor = Autor.query.filter_by(id_autor=id_autor).first() # pegando no bd o autor pelo id passado
    if not autor:
        return jsonify({'mensagem': 'Esse autor não foi encontrado.'})
    try:
        autor.nome = autor_a_ser_alterador['nome']
    except:
        pass
    try:
        autor.senha = autor_a_ser_alterador['senha']
    except:
        pass
    try:
        autor.email = autor_a_ser_alterador['email']
    except:
        pass
    db.session.commit()
    return jsonify({'mensagem': 'Usuário alterado com sucesso'})

    

@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor, id_autor):
    autor_a_ser_excluido = Autor.query.filter_by(id_autor=id_autor).first() #pegando requisição
    if not autor_a_ser_excluido:
        return jsonify({'mensagem': 'esse autor não foi encontrado'})
    db.session.delete(autor_a_ser_excluido)
    db.session.commit()
    return jsonify({'mensagem': 'autor excluído com sucesso...'})

#comentario
if __name__ =='__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))

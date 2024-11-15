from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def conectar_banco():
    conn = sqlite3.connect('bd_livros_e_autores.db')
    return conn

# ROTAS

@app.route("/api/usuarios", methods=["POST"])
def criar_usuario():
    data = request.get_json()
    print(data)
    conn = conectar_banco()
    cursor = conn.cursor()
    nome = data['nome']
    email = data['email']
    # verificar se usuario já existe
    verificar_existencia_nome = cursor.execute("SELECT nome FROM usuarios WHERE nome = ?", (nome,)).fetchone()
    verificar_existencia_email = cursor.execute("SELECT nome FROM usuarios WHERE email = ?", (email,)).fetchone() 
    if verificar_existencia_nome is not None:
        return jsonify({"mensagem": "Nome de usuário já existente"}), 201
    elif verificar_existencia_email is not None:
        return jsonify({"mensagem": "Email de usuário já existente"}), 201
    else:    
        cursor.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)', 
                    (data['nome'], data['email'], data['senha']))
        conn.commit()
        conn.close()
        
        return jsonify({"mensagem": "Usuário criado com sucesso!"}), 201


@app.route("/api/livros", methods=["GET"])
def listar_livros():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""SELECT livros.id, livros.titulo, livros.genero, autores.nome, autores.nacionalidade 
                      FROM livros 
                      JOIN autores ON livros.autor_id = autores.id""")
    livros = cursor.fetchall()
    conn.close()
    
    resultado = [{
        "id": l[0],
        "titulo": l[1],
        "genero": l[2],
        "autor": l[3],
        "nacionalidade": l[4]
    } for l in livros]
    
    return jsonify(resultado), 200

@app.route('/api/verificar_usuario', methods=['POST'])
def verificar_usuario():
    data = request.get_json()
    nome = data.get("nome")
    senha = data.get("senha")

    if not nome or not senha:
        return jsonify({"error": "Nome e senha são necessários"}), 400

    conn = sqlite3.connect('bd_livros_e_autores.db')
    cursor = conn.cursor()
    verificar_usuario = cursor.execute("SELECT nome, senha FROM usuarios WHERE nome = ?", (nome,)).fetchone()
    conn.close()

    if verificar_usuario:
        verificar_nome, verificar_senha = verificar_usuario
        if nome == verificar_nome and senha == verificar_senha:
            return jsonify({"valido": True}), 200
        else:
            return jsonify({"valido": False, "error": "Senha incorreta"}), 401
    else:
        return jsonify({"valido": False, "error": "Usuário não encontrado"}), 404


if __name__ == "__main__":

    app.run(debug=True)
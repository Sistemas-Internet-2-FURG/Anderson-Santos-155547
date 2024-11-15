from flask import Flask, render_template, request, session, redirect, url_for
import requests

app = Flask(__name__)
app.secret_key = 'chave muito secreta'

API_URL = "http://127.0.0.1:5000/api"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/logar", methods=['POST', 'GET'])
def logar():
    if request.method == 'POST':
        nome = request.form.get("login_nome")
        senha = request.form.get("login_senha")

        if len(nome) > 0 and len(senha) > 0:
            resposta = requests.post(f"{API_URL}/verificar_usuario", json={"nome": nome, "senha": senha})
            if resposta.status_code == 200:
                user_data = resposta.json()
                if user_data.get("valido"):
                    session['user'] = nome
                    return redirect(url_for("index"))
                else:
                    print("senha não coincide com usuário")
            else:
                print("Erro na conexão com a API.")
                    
        return render_template("login.html", error="Credenciais inválidas. Tente novamente.")

    return render_template("login.html")

@app.route("/deslogar")
def deslogar():
    session.pop("user", None)
    return redirect(url_for('logar'))

@app.route("/usuario")
def usuario():
    if 'user' in session:
        user = session['user']
        response = requests.get(f"{API_URL}/livros")
        if response.status_code == 200:
            livros = response.json()
        else:
            livros = []
        return render_template("usuario.html", user=user, livros=livros)
    else:
        return redirect(url_for('logar'))

@app.route("/criar_usuario", methods=['GET', 'POST'])
def criar_usuario():
    if request.method == 'POST':
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        # Envia os dados para a API
        resposta = requests.post(f"{API_URL}/usuarios", json={
            "nome": nome,
            "email": email,
            "senha": senha
        })

        if resposta.status_code == 201:
            return redirect(url_for("logar"))
        else:
            return render_template("registro.html", error="Erro ao criar usuário.")

    return render_template("registro.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)

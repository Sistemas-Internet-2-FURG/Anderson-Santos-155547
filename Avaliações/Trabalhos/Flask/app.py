from flask import Flask,request,render_template, session, redirect, url_for
from datetime import timedelta
import sqlite3
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
def check(email):
	if(re.fullmatch(regex, str(email))):
		return True 
 
	else:
		return False
	
app = Flask(__name__)
app.secret_key = 'nao sei'
app.permanent_session_lifetime = timedelta(days=30)

def le_arquivo():
	arq = open('dados.csv','r')
	dados = arq.readlines()
	saida = {}
	for linha in dados:
		linha = linha[:-1].split(';')
		saida[linha[0]] = linha[1]
	return saida

def salva_dados(matricula,nome):
	arq = open('dados.csv','a')
	arq.write(f"{matricula};{nome}\n")	
	arq.close()

@app.route("/")
def index():
	if 'user' in session:
		user = session['user']
	else:
		user = None
	return render_template('index.html', user=user)

@app.route("/verificardatabase")
def verificarDatabase():
	Conexao = sqlite3.connect("Banco_de_Dados.db")
	Cursor = Conexao.cursor()
	lista = []
	Conexao.commit()
	Cursor.execute('SELECT * FROM Usuarios')
	lista.append("Usuários")
	for i in Cursor:
		lista.append(i)
	lista.append("\n")
	Cursor.execute('SELECT * FROM Livros')
	lista.append("Livros")
	for i in Cursor:
		lista.append(i)
	lista.append("\n")
	Cursor.execute('SELECT * FROM Estantes')
	lista.append("Estantes")
	for i in Cursor:
		lista.append(i)
	Conexao.close()
	return render_template('checar_database.html', lista=lista)

@app.route("/apagar/", methods=['POST','GET'])

def apagar():
	matricula_del = request.form.get('matricula_del')

	if request.method == 'POST' and matricula_del and len(matricula_del) > 0:
		matricula_del = int(matricula_del)
		arq = open('dados.csv','r')
		saida = ""
		for linha in arq:
			linha = linha.split(';')
			if int(linha[0]) != matricula_del:
				linha = linha[0]+";"+linha[1]
				saida+=linha
		arq.close()
		arq = open('dados.csv','w')
		arq.write(saida)
		arq.close
		return render_template('apagada.html',matricula_del=matricula_del)
	
	return render_template('apagar-matricula.html',matricula_del=matricula_del)
	
@app.route("/cadastro_livro", methods=['POST', 'GET'])
def cadastrar_livro():
	titulo = autor = None
	titulo = request.form.get("novo_titulo")
	autor = request.form.get("novo_autor")
	capa = request.form.get("nova_capa")
	if request.method == 'POST':
		if not titulo or not autor:
			mensagem_cadastro = "Todos os campos são obrigatórios!"
			return render_template('cadastro_livro.html', possui_na_biblioteca=mensagem_cadastro)
		Conexao = sqlite3.connect("Banco_de_Dados.db")
		Cursor = Conexao.cursor()

		verificar_titulo = Cursor.execute("SELECT Title FROM Livros WHERE Title = ?", (titulo,)).fetchone()

		if verificar_titulo is not None:
			mensagem_cadastro = "Título do livro já existe!"
			return render_template('cadastro_livro.html', possui_na_biblioteca=mensagem_cadastro)
		else:
			# Insere o novo livro no banco de dados

			Cursor.execute('INSERT INTO Livros (Title, Author, Cover) VALUES (?, ?, ?)', (titulo, autor, capa))

			Conexao.commit()
			mensagem_cadastro = "Novo livro adicionado com sucesso!"
		Conexao.close()
	else:
		mensagem_cadastro =''
	return render_template('cadastro_livro.html', possui_na_biblioteca=mensagem_cadastro)


@app.route("/cadastro_usuario", methods=['POST', 'GET'])
def cadastrar_usuario():
	print("request.form",request.form)
	nome = email = senha = None
	nome = request.form.get("novo_usuario")
	email = request.form.get("novo_email")
	senha = request.form.get("nova_senha")
	if request.method == 'POST':
		# Verifica se os campos estão preenchidos
		if not nome or not email or not senha:
			mensagem_cadastro = "Todos os campos são obrigatórios!"
			return render_template('cadastro_usuario.html', possui_na_biblioteca=mensagem_cadastro)

		# Verifica se o email é válido
		if not check(email):
			mensagem_cadastro = "E-mail inválido!"
			return render_template('cadastro_usuario.html', possui_na_biblioteca=mensagem_cadastro)

		Conexao = sqlite3.connect("Banco_de_Dados.db")
		Cursor = Conexao.cursor()
		
		Cursor.execute("""CREATE TABLE IF NOT EXISTS Usuarios (
							ID INTEGER PRIMARY KEY AUTOINCREMENT, 
							Name TEXT NOT NULL, 
							Password TEXT NOT NULL,
							Email TEXT NOT NULL UNIQUE,
				 			Usuario_Estante INTEGER UNIQUE
						)""")

		# Verifica se o nome de usuário ou o email já existem no banco de dados
		verificar_nome = Cursor.execute("SELECT Name FROM Usuarios WHERE Name = ?", (nome,)).fetchone()
		verificar_email = Cursor.execute("SELECT Email FROM Usuarios WHERE Email = ?", (email,)).fetchone()

		if verificar_nome is not None:
			mensagem_cadastro = "Nome de Usuário já existe!"
			return render_template('cadastro_usuario.html', possui_na_biblioteca=mensagem_cadastro)

		elif verificar_email is not None:
			mensagem_cadastro = "Email de usuário já está em uso!"
			return render_template('cadastro_usuario.html', possui_na_biblioteca=mensagem_cadastro)

		else:
			# Insere o novo usuário no banco de dados
			Cursor.execute('INSERT INTO Usuarios (Name, Password, Email) VALUES (?, ?, ?)', (nome, senha, email))
			Conexao.commit()
			mensagem_cadastro = "Novo usuário adicionado com sucesso!"
			return redirect(url_for('logar'))
		Conexao.close()
	else:
		mensagem_cadastro =''
	return render_template('cadastro_usuario.html', possui_na_biblioteca=mensagem_cadastro)

@app.route('/deletar_conta', methods=['GET', 'POST'])
def deletar_conta():
	if request.method == 'POST':
		if 'confirmar' in request.form:
			user_id = session.get('user')
			if user_id:
				Conexao = sqlite3.connect("Banco_de_Dados.db")
				Conexao.row_factory = sqlite3.Row
				Conexao.execute('DELETE FROM Usuarios WHERE Name = ?', (user_id,))
				Conexao.commit()
				Conexao.close()
				session.clear()  
				return redirect(url_for('index'))
		elif 'cancelar' in request.form:
			return redirect(url_for('usuario'))

	return render_template('confirmar_delecao.html')

@app.route('/deletar_livro/<int:id>', methods=['GET', 'POST'])
def deletar_livro(id):
    if request.method == 'POST':
        if 'confirmar' in request.form:
            user_id = session.get('user')
            if user_id:
                Conexao = sqlite3.connect("Banco_de_Dados.db")
                Conexao.row_factory = sqlite3.Row
                
                # Remover o livro da tabela Livros
                Conexao.execute('DELETE FROM Livros WHERE ID = ?', (id,))
            
                Conexao.commit()
                Conexao.close()
                return redirect(url_for('index'))
        elif 'cancelar' in request.form:
            return redirect(url_for('Exibir_Todos_Livros'))
    
    return render_template('confirmar_delecao_livro.html', id=id)

@app.route("/login", methods=['POST', 'GET'])
def logar():
	# email = request.form.get("login_email")
	nome = request.form.get("login_usuario")
	senha = request.form.get("login_senha")	

	if 'user' not in session:
		if request.method == 'POST' and len(nome) > 0 and len(senha) > 0:
			Conexao = sqlite3.connect("Banco_de_Dados.db")
			Cursor = Conexao.cursor()
			Cursor.execute("""CREATE TABLE IF NOT EXISTS Usuarios (
								ID INTEGER PRIMARY KEY AUTOINCREMENT, 
								Name TEXT NOT NULL, 
								Password TEXT NOT NULL,
								Email TEXT NOT NULL UNIQUE
							)""")
			verificar_usuario = Cursor.execute("SELECT Name, Password FROM Usuarios WHERE Name = ?", (nome,)).fetchone()
			Conexao.close()

			if verificar_usuario:
				verificar_nome, verificar_senha = verificar_usuario
				if nome == verificar_nome and senha == verificar_senha:
					print("verificar nome e senha", verificar_nome, verificar_senha, "; dados verificados!")
					session.permanent = True
					session['user'] = nome
					Conexao.close()
					return redirect(url_for('usuario'))
				else:
					print("senha não coincide com usuario")
		else:
			print("Usuário não encontrado!")
	else:
		return redirect(url_for('usuario'))

	return render_template('login.html')

@app.route("/logout")
def deslogar():
	session.pop("user", None)
	return redirect(url_for('logar'))

@app.route("/sobre")
def sobre():
	return render_template('sobre.html')

@app.route("/usuario")
def usuario():
	if 'user' in session:
		user = session['user']
		Conexao = sqlite3.connect("Banco_de_Dados.db")
		Cursor = Conexao.cursor()
		Cursor.execute("""CREATE TABLE IF NOT EXISTS Usuarios (
					ID INTEGER PRIMARY KEY AUTOINCREMENT, 
					Name TEXT NOT NULL, 
					Password TEXT NOT NULL,
					Email TEXT NOT NULL UNIQUE
				)""")
		verificar_usuario = Cursor.execute("SELECT Name, Password FROM Usuarios WHERE Name = ?", (session['user'],)).fetchone()

		Estante = Cursor.execute("SELECT ID_Livro FROM Estantes WHERE ID_Usuario = ? AND Possui IS NOT NULL", (session['user'],)).fetchall()
		livros_dict = {}
		# print("ESTANTE!",Estante)

		for entrada in Estante:
			titulo_livro = entrada[0]
			# print(f"Titulo na estante: {titulo_livro}")  

			id_livro = Cursor.execute("SELECT ID FROM Livros WHERE Title = ?", (titulo_livro,)).fetchone()
			# print(f"ID recuperado: {id_livro}")  

			if id_livro:
				livros_dict[titulo_livro] = id_livro[0]

		# print("Dicionário final:", livros_dict) 
		Conexao.close()
		return render_template('usuario.html', user=user, verificar_usuario=verificar_usuario, livros_dict=livros_dict)
	else:
		return redirect(url_for('logar'))
	
@app.route('/Livro/<int:id>', methods=['GET', 'POST'])
def Exibir_Livro(id):
	Conexao = sqlite3.connect('Banco_de_Dados.db')
	Conexao.row_factory = sqlite3.Row  
	entry = Conexao.execute('SELECT * FROM Livros WHERE ID = ?', (id,)).fetchone()
	Conexao.close()

	if entry is None:
		return 'Entrada Não encontrada!', 404
	
	# user = session['user']
	user = session.get('user')
	mensagem = ""
	possui_na_biblioteca = None
	if 'user' in session:
		Conexao = sqlite3.connect('Banco_de_Dados.db')
		possui_na_biblioteca = Conexao.execute(
			'SELECT Estantes.Possui FROM Estantes INNER JOIN Livros ON Estantes.ID_Livro = Livros.Title WHERE Livros.ID = ? AND Estantes.ID_Usuario = ?;', 
			(id,user)).fetchone()
		Conexao.close()

		if possui_na_biblioteca[0] != None:
			mensagem = "Você tem esse livro na sua estante."
		elif possui_na_biblioteca[0] == None:
			mensagem = "Você não possui este livro, gostaria de adicionar a sua estante?"

	else:
		return render_template('Livro.html', entry=entry, mensagem=mensagem, id=id)

		
	if request.method == 'POST':
		if possui_na_biblioteca[0] == None:
			Conexao = sqlite3.connect('Banco_de_Dados.db')
				# Adiciona o livro à estante do usuário
			Conexao.execute(
						'UPDATE Estantes '
						'SET Possui = ? '
						'WHERE ID_Usuario = ? AND ID_Livro = ?;',
						(1, user, entry['Title'])
					)
			Conexao.commit()
			Conexao.close()
			mensagem = "Livro adicionado à sua estante!"
			return render_template('Livro.html', entry=entry, user=user, mensagem=mensagem, id=id)
		else:
			Conexao = sqlite3.connect('Banco_de_Dados.db')
				# Remove livro da estante do usuário
			Conexao.execute(
						'UPDATE Estantes '
						'SET Possui = ? '
						'WHERE ID_Usuario = ? AND ID_Livro = ?;',
						(None, user, entry['Title'])
					)
			Conexao.commit()
			Conexao.close()
			mensagem = "Livro removido da sua estante!"
			return render_template('Livro.html', entry=entry, user=user, mensagem=mensagem, id=id)

	# renderiza a página caso não haja usuario logado
	else:
		return render_template('Livro.html', entry=entry, user=user, mensagem=mensagem, id=id, possui_na_biblioteca=possui_na_biblioteca[0])

@app.route('/Livros')
def Exibir_Todos_Livros():
	Conexao = sqlite3.connect('Banco_de_Dados.db')
	Conexao.row_factory = sqlite3.Row
	entries = Conexao.execute('SELECT * FROM Livros').fetchall()
	Conexao.close()
	
	return render_template('Livros.html', entries=entries)

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def erro_interno_servidor(e):
    return render_template('500.html'), 500

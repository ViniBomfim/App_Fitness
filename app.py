from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'admin'

# Função para obter uma nova conexão com o banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='admin',
        database='fitness',
        auth_plugin='mysql_native_password'
    )

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conexao = get_db_connection()
        cursor = conexao.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Esse nome de usuário já está em uso.', 'error')
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conexao.commit()
            cursor.close()
            conexao.close()
            return redirect(url_for('login'))

        cursor.close()
        conexao.close()

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conexao = get_db_connection()
        cursor = conexao.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user[2] == password:  # Comparando diretamente a senha
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Login bem-sucedido!', 'success')
            cursor.close()
            conexao.close()
            return redirect(url_for('registrar_atividade'))
        else:
            flash('Usuário não encontrado ou senha incorreta.', 'error')

        cursor.close()
        conexao.close()

    return render_template('login.html')



@app.route('/registrar_atividade', methods=['GET', 'POST'])
def registrar_atividade():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar essa página.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        tipo = request.form['tipo']
        horario = request.form['horario']
        data = request.form['data']
        
        try:
            horario = datetime.strptime(horario, '%H:%M').time()
            data = datetime.strptime(data, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de data ou hora inválido.', 'error')
            return redirect(url_for('registrar_atividade'))

        if data < data.today():
            flash('A data não pode ser anterior à data atual.', 'error')
            return redirect(url_for('registrar_atividade'))

        conexao = get_db_connection()
        cursor = conexao.cursor()

        if tipo == 'Musculação':
            exercicios = request.form.getlist('exercicios[]')
            repeticoes = request.form.getlist('repeticoes[]')
            for exercicio, repeticao in zip(exercicios, repeticoes):
                cursor.execute(
                    "INSERT INTO atividades_fisicas (tipo, exercicio, repeticoes, horario, data) VALUES (%s, %s, %s, %s, %s)",
                    (tipo, exercicio, repeticao, horario, data)
                )
        else:
            repeticoes = request.form['repeticoes']
            cursor.execute(
                "INSERT INTO atividades_fisicas (tipo, repeticoes, horario, data) VALUES (%s, %s, %s, %s)",
                (tipo, repeticoes, horario, data)
            )

        conexao.commit()
        cursor.close()
        conexao.close()

        flash('Atividade física registrada com sucesso!', 'success')
        return redirect(url_for('listar_atividades'))

    return render_template('atividade_fisica.html')




@app.route('/listar_atividades')
def listar_atividades():
    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM atividades_fisicas")
    atividades = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template('lista_atividades.html', atividades=atividades)



@app.route('/calculadora_imc', methods=['GET', 'POST'])
def calculadora_imc():
    if request.method == 'POST':
        peso = float(request.form['peso'])
        altura = float(request.form['altura'])

        imc = calcular_imc(peso, altura)

        return render_template('resultado_imc.html', imc=imc, altura=altura)

    return render_template('calculadora_imc.html')

def calcular_imc(peso, altura):
    imc = peso / (altura ** 2)
    return round(imc, 2)



@app.route('/planejamento_treinos', methods=['GET', 'POST'])
def planejamento_treinos():
    if request.method == 'POST':
        semana = request.form['semana']
        exercicio = request.form['exercicio']
        repeticoes = request.form['repeticoes']
        descanso = request.form['descanso']

    return render_template('planejamento_treinos.html')



@app.route('/excluir')
def listar_clientes():
    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM users")
    clientes = [User(id, username, password) for (id, username, password) in cursor.fetchall()]

    cursor.close()
    conexao.close()

    return render_template('lista_clientes.html', clientes=clientes)



@app.route('/excluir_cliente/<int:id>', methods=['GET'])
def excluir_cliente(id):
    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conexao.commit()

    cursor.close()
    conexao.close()

    return redirect(url_for('listar_clientes'))

@app.route('/excluir_atividade/<int:id>', methods=['GET'])
def excluir_atividade(id):
    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM atividades_fisicas WHERE id = %s", (id,))
    conexao.commit()

    cursor.close()
    conexao.close()

    flash('Atividade física excluída com sucesso!', 'success')
    return redirect(url_for('listar_atividades'))

@app.route('/atividades')
def excluir_atividades():
    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM atividades_fisicas")
    atividades = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template('excluir_atividades.html', atividades=atividades)

if __name__ == '__main__':
    app.run(debug=True)

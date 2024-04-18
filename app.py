from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'


conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='123456',
    database='fitness',
    auth_plugin='mysql_native_password'
)

cursor = conexao.cursor()

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

        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Esse nome de usuário já está em uso.', 'error')
        else:
            
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conexao.commit()

            return redirect(url_for('login'))  
            #return redirect(url_for('index'))

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.args.get('username', '')  

    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            
            if user[2] == password:  
                flash('Login bem-sucedido!', 'success')
                return redirect(url_for('registrar_atividade'))
            else:
                flash('Senha incorreta.', 'error')
        else:
            flash('Usuário não encontrado.', 'error')

    return render_template('login.html') 



@app.route('/registrar_atividade', methods=['GET', 'POST'])
def registrar_atividade():
    if request.method == 'POST':
        
        if 'tipo' in request.form:
            tipo = request.form['tipo']
        else:
            
            flash('Tipo de atividade não especificado.', 'error')
            return redirect(url_for('registrar_atividade'))

        
        tipo = request.form['tipo']
        repeticoes = request.form['repeticoes']
        horario = request.form['horario']
        data = request.form['data']
        
        
        horario = datetime.strptime(horario, '%H:%M').time()
        data = datetime.strptime(data, '%Y-%m-%d').date()
        
        
        cursor.execute("INSERT INTO atividades_fisicas (tipo, repeticoes, horario, data) VALUES (%s, %s, %s, %s)",
                       (tipo, repeticoes, horario, data))
        conexao.commit()
        
        
        cursor.execute("SELECT * FROM atividades_fisicas")
        atividades = cursor.fetchall()

        
        flash('Atividade física registrada com sucesso!', 'success')
        
        
        return redirect(url_for('listar_atividades', atividades=atividades))

    
    return render_template('atividade_fisica.html')



@app.route('/listar_atividades')
def listar_atividades():
    
    cursor.execute("SELECT * FROM atividades_fisicas")
    atividades = cursor.fetchall()
    
    
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
    
    cursor.execute("SELECT * FROM users")
    clientes = [User(id, username, password) for (id, username, password) in cursor.fetchall()]
    return render_template('lista_clientes.html', clientes=clientes)


@app.route('/excluir_cliente/<int:id>', methods=['GET'])
def excluir_cliente(id):
    
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conexao.commit()

    return redirect(url_for('listar_clientes'))


@app.route('/excluir_atividade/<int:id>', methods=['GET'])
def excluir_atividade(id):
    
    cursor.execute("DELETE FROM atividades_fisicas WHERE id = %s", (id,))
    conexao.commit()

    flash('Atividade física excluída com sucesso!', 'success')
    return redirect(url_for('listar_atividades'))


@app.route('/atividades')
def excluir_atividades():
    
    cursor.execute("SELECT * FROM atividades_fisicas")
    atividades = cursor.fetchall()
    return render_template('excluir_atividades.html', atividades=atividades)


if __name__ == '__main__':
    app.run(debug=True)


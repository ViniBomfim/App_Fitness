from flask import Flask, render_template, request, jsonify
import mysql.connector
from flask import redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'


conexao = {
    'host': 'localhost',
    'user': 'root',
    'password': 'vinicius123!',
    'database': 'fitness',
    'auth_plugin': 'mysql_native_password'
}

# Função para conectar ao banco de dados
def connect_to_database():
    return mysql.connector.connect(**conexao)

# Rota para a página inicial
@app.route('/')
def index():
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM metas")
    metas = cursor.fetchall()

    conn.close()

    return render_template('index.html', metas=metas)

# Rota para adicionar uma nova meta
# Rota para adicionar uma nova meta
@app.route('/metas', methods=['POST'])
def add_goal():
    data = request.json
    if 'descricao' not in data or 'valor_meta' not in data or 'data_limite' not in data:
        return jsonify({'error': 'Faltam informações'}), 400

    conn = connect_to_database()
    cursor = conn.cursor()

    query = "INSERT INTO metas (descricao, valor_meta, data_limite) VALUES (%s, %s, %s)"
    cursor.execute(query, (data['descricao'], data['valor_meta'], data['data_limite']))
    
    conn.commit()

    # Recuperar a nova meta inserida
    cursor.execute("SELECT * FROM metas ORDER BY id DESC LIMIT 1")
    nova_meta = cursor.fetchone()
    
    conn.close()

    # Formatar os dados da nova meta
    nova_meta_dict = {
        'id': nova_meta[0],
        'descricao': nova_meta[1],
        'valor_meta': nova_meta[2],
        'data_limite': nova_meta[3]
    }

    return jsonify(nova_meta_dict), 200


# Rota para listar todas as metas
@app.route('/metas', methods=['GET'])
def get_goals():
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM metas")
    metas = cursor.fetchall()

    conn.close()

    return render_template('listar_metas.html',metas=metas), 200

# Rota para atualizar uma meta
@app.route('/metas/<int:id>', methods=['PUT'])
def update_goal(id):
    data = request.json
    if 'descricao' not in data or 'valor_meta' not in data or 'data_limite' not in data:
        return jsonify({'error': 'Faltam informações'}), 400

    conn = connect_to_database()
    cursor = conn.cursor()

    query = "UPDATE metas SET descricao=%s, valor_meta=%s, data_limite=%s WHERE id=%s"
    cursor.execute(query, (data['descricao'], data['valor_meta'], data['data_limite'], id))
    
    conn.commit()
    conn.close()

    return jsonify({'message': 'Meta atualizada com sucesso'}), 200

# Rota para excluir uma meta
@app.route('/metas/<int:id>', methods=['DELETE'])
def delete_goal(id):
    conn = connect_to_database()
    cursor = conn.cursor()

    query = "DELETE FROM metas WHERE id=%s"
    cursor.execute(query, (id,))
    
    conn.commit()
    conn.close()

    return jsonify({'message': 'Meta excluída com sucesso'}), 200

if __name__ == '__main__':
    app.run(debug=True)

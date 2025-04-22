from flask import Flask, request, jsonify
import firebase_admin
from flask_cors import CORS
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os, json

load_dotenv()
API = json.loads(os.getenv('CONFIG_FIREBASE'))

cred = credentials.Certificate(API)
firebase_admin.initialize_app(cred)

# conectando com o firestore da firebase
db = firestore.client()

app = Flask(__name__)
CORS(app)


# ---------------------------
# Rota Teste
# ---------------------------
@app.route('/')
def index():
    return "API ACADEMIA ONLINE"

# ---------------------------
# Rota para listar os alunos OK
# ---------------------------
@app.route('/academia', methods=['GET'])
def listar_alunos():
    alunos = []
    lista = db.collection('alunos').stream()

    for item in lista:
        aluno_data = item.to_dict()
        aluno_data['id'] = item.id  # Adiciona o ID do documento
        alunos.append(aluno_data)

    if alunos:
        return jsonify(alunos), 200
    else:
        return jsonify({'mensagem': 'ERRO! Nenhum aluno encontrado.'}), 404

# ---------------------------
# Rota para cadastrar aluno
# ---------------------------
@app.route('/academia/cadastro', methods=['POST'])
def cadastrar_aluno():
    dados = request.json
    cpf = dados.get('cpf')
    nome = dados.get('nome')
    status = dados.get('status')

    if not cpf:
        return jsonify({'mensagem': 'CPF não enviado.'}), 400
    if not nome:
        return jsonify({'mensagem': 'Nome não enviado.'}), 400
    if status is None:
        return jsonify({'mensagem': 'Status não enviado.'}), 400

    try:
        # Verifica se já existe um aluno com o CPF fornecido
        alunos_ref = db.collection('alunos')
        query = alunos_ref.where('cpf', '==', cpf).limit(1)
        resultados = query.get()

        if resultados:
            return jsonify({'mensagem': f'CPF "{cpf}" já cadastrado.'}), 409  # Código 409 Conflict
        else:
            # Se o CPF não existe, cadastramos o novo aluno
            novo_aluno = {
                'cpf': cpf,
                'nome': nome,
                'status': status
            }
            # Usando o CPF como ID do documento
            db.collection('alunos').document(cpf).set(novo_aluno)
            return jsonify({'mensagem': 'Aluno cadastrado com sucesso.', 'aluno': novo_aluno, 'id': cpf}), 201

    except Exception as e:
        return jsonify({'mensagem': f'Erro ao acessar o banco de dados: {str(e)}'}), 500

# ---------------------------
# Rota para consultar aluno (para edição)
# ---------------------------
@app.route('/academia_edicao/<cpf>', methods=['GET'])
def consultar_aluno(cpf):
    try:
        aluno_ref = db.collection('alunos').document(cpf)
        doc = aluno_ref.get()
        if doc.exists:
            aluno_data = doc.to_dict()
            return jsonify({'id': doc.id, 'cpf': aluno_data.get('cpf'), 'nome': aluno_data.get('nome'), 'status': aluno_data.get('status')}), 200
        else:
            return jsonify({'mensagem': 'Aluno não encontrado.'}), 404
    except Exception as e:
        return jsonify({'mensagem': f'Erro ao consultar o banco de dados: {str(e)}'}), 500

# ---------------------------
# Rota para editar aluno
# ---------------------------
@app.route('/academia/editar/<cpf>', methods=['PUT'])
def editar_aluno(cpf):
    dados = request.json
    nome = dados.get('nome')
    status = dados.get('status')

    if not nome:
        return jsonify({'mensagem': 'Nome não enviado para edição.'}), 400
    if status is None:
        return jsonify({'mensagem': 'Status não enviado para edição.'}), 400

    try:
        aluno_ref = db.collection('alunos').document(cpf)
        doc = aluno_ref.get()
        if doc.exists:
            aluno_ref.update({
                'nome': nome,
                'status': status
            })
            return jsonify({'mensagem': f'Aluno com CPF "{cpf}" atualizado com sucesso.'}), 200
        else:
            return jsonify({'mensagem': f'Aluno com CPF "{cpf}" não encontrado.'}), 404
    except Exception as e:
        return jsonify({'mensagem': f'Erro ao editar aluno: {str(e)}'}), 500

# ---------------------------
# Rota para excluir aluno
# ---------------------------
@app.route('/academia/<cpf>', methods=['DELETE'])
def excluir_aluno(cpf):
    try:
        aluno_ref = db.collection('alunos').document(cpf)
        doc = aluno_ref.get()
        if doc.exists:
            aluno_ref.delete()
            return jsonify({'mensagem': f'Aluno com CPF "{cpf}" excluído com sucesso.'}), 200
        else:
            return jsonify({'mensagem': f'Aluno com CPF "{cpf}" não encontrado.'}), 404
    except Exception as e:
        return jsonify({'mensagem': f'Erro ao excluir aluno: {str(e)}'}), 500


if __name__ == '__main__':
    app.run()
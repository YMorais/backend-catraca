from flask import Flask, request, jsonify
import firebase_admin
from flask_cors import CORS
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os, json, random

load_dotenv()
API = json.loads(os.getenv('CONFIG_FIREBASE'))

cred = credentials.Certificate(API)
firebase_admin.initialize_app(cred)

#conectando com o firestore da firebase
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
        alunos.append(item.to_dict())

    if alunos:
        return jsonify(alunos), 200
    else:
        return jsonify({'mensagem': 'ERRO! Nenhum aluno encontrado.'}), 404

# ---------------------------
# Rota para cadastrar aluno
# ---------------------------
@app.route('/academia_cadastro', methods=['POST'])
def cadastrar_aluno():
    dados = request.json
    cpf = dados.get('cpf')
    nome = dados.get('nome')
    status = dados.get('status')

    if not cpf:
        return jsonify({'mensagem': 'CPF não enviado.'}), 400
    if not nome:
        return jsonify({'mensagem': 'Nome não enviado.'}), 400
    if status is None: # Permite status booleano (True/False)
        return jsonify({'mensagem': 'Status não enviado.'}), 400

    try:
        # Verifica se já existe um aluno com o CPF fornecido
        alunos_ref = db.collection('alunos')
        query = alunos_ref.where('cpf', '==', cpf).limit(1)
        resultados = query.get()

        if resultados:
            return jsonify({'mensagem': f'CPF "{cpf}" já cadastrado.'}), 409 # Código 409 Conflict
        else:
            # Se o CPF não existe, cadastramos o novo aluno
            novo_aluno = {
                'cpf': cpf,
                'nome': nome,
                'status': status
            }
            # Aqui você precisa definir um ID para o documento.
            # Você pode usar o próprio CPF como ID (se fizer sentido para sua lógica),
            # ou deixar o Firestore gerar um ID automático.

            # Opção 1: Usar o CPF como ID do documento
            db.collection('alunos').document(cpf).set(novo_aluno)

            # Opção 2: Deixar o Firestore gerar um ID automático
            # db.collection('alunos').add(novo_aluno)

            return jsonify({'mensagem': 'Aluno cadastrado com sucesso.', 'aluno': novo_aluno}), 201
        
    except Exception as e:
        return jsonify({'mensagem': f'Erro ao acessar o banco de dados: {str(e)}'}), 500

# ---------------------------
# Rota para consultar aluno
# ---------------------------
@app.route('/academia_consulta/<cpf>', methods=['GET'])
def consultar_aluno(cpf):
    try:
        # Consulta a coleção 'alunos' onde o campo 'cpf' é igual ao CPF fornecido
        alunos_ref = db.collection('alunos')
        query = alunos_ref.where('cpf', '==', cpf).limit(1) # Limita a 1 resultado, pois o CPF deve ser único

        resultados = query.get()

        if resultados:
            # Se encontrarmos um documento, pegamos o primeiro (e único) resultado
            aluno_doc = resultados[0]
            aluno_data = aluno_doc.to_dict()
            return jsonify({'cpf': cpf, 'nome': aluno_data.get('nome'), 'status': aluno_data.get('status')}), 200
        else:
            return jsonify({'mensagem': 'Aluno não encontrado.'}), 404
    except Exception as e:
        return jsonify({'mensagem': f'Erro ao consultar o banco de dados: {str(e)}'}), 500




# ---------------------------
# Rota para editar aluno
# ---------------------------
@app.route('/academia_edicao/<cpf>', methods=['PUT'])
def editar_aluno(cpf):
    if cpf not in editar_aluno:
        return jsonify({'mensagem': 'Aluno não encontrado.'}), 404

    dados = request.json
    aluno = editar_aluno[cpf]

    # Atualiza os dados apenas se forem fornecidos
    aluno['nome'] = dados.get('nome', aluno['nome'])
    aluno['status'] = dados.get('status', aluno['status'])

    return jsonify({'mensagem': 'Dados atualizados com sucesso.'}), 200



# ---------------------------
# Rota para excluir aluno
# ---------------------------
@app.route('/academia_exclusao/<cpf>', methods=['DELETE'])
def excluir_aluno(cpf):
    if cpf in excluir_aluno:
        del excluir_aluno[cpf]
        return jsonify({'mensagem': 'Aluno excluído com sucesso.'}), 200
    else:
        return jsonify({'mensagem': 'Aluno não encontrado.'}), 404


if __name__ == '__main__':
    app.run()



import json
import os
import sys

# Adicionar diretório pai ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    from api.app import app
    from pdf_processor_v2 import PDFProcessor
except ImportError as e:
    print(f"Import error: {e}")

def handler(event, context):
    """Handler para Netlify Functions"""
    try:
        # Inicializar processador
        pdf_processor = PDFProcessor()
        
        # Tentar carregar dados pré-compilados
        data_path = os.path.join(project_root, 'data', 'alunos_compilado.json')
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pdf_processor.load_data(data)
        else:
            # Processar PDFs diretamente
            pdf_processor.process_all_pdfs(project_root)
        
        # Extrair path da requisição
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        if path.startswith('/.netlify/functions/app'):
            path = path.replace('/.netlify/functions/app', '')
        
        # Roteamento simples
        if path == '/api/turmas':
            codigos = set()
            for serie_dict in pdf_processor.students_data.values():
                for aluno in serie_dict.values():
                    arq = aluno.get('arquivo_origem')
                    if arq and arq.lower().endswith('.pdf'):
                        codigos.add(arq[:-4])
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({"status": "success", "data": sorted(codigos)})
            }
        
        elif path.startswith('/api/turma/'):
            codigo = path.split('/')[-1]
            alunos = pdf_processor.get_students_by_file(codigo)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({"status": "success", "data": alunos})
            }
        
        elif path == '/api/series':
            series = list(pdf_processor.students_data.keys())
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({"status": "success", "data": sorted(series)})
            }
        
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({"status": "error", "message": "Endpoint não encontrado"})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"status": "error", "message": str(e)})
        }

import json
import os
import sys

# Adicionar diretório pai ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    from pdf_processor_v2 import PDFProcessor
except ImportError as e:
    print(f"Import error: {e}")

def handler(event, context):
    """Handler para Netlify Functions"""
    # Log de debug
    print(f"Event: {json.dumps(event, indent=2)}")
    print(f"Context: {context}")
    
    try:
        # Extrair path da requisição
        path = event.get('path', '/')
        query_params = event.get('queryStringParameters') or {}
        
        print(f"Original path: {path}")
        print(f"Query params: {query_params}")
        
        # Se veio do redirect, pegar o path do parâmetro
        if 'path' in query_params:
            path = '/' + query_params['path']
            print(f"Adjusted path: {path}")
        
        # Inicializar processador
        pdf_processor = PDFProcessor()
        
        # Tentar carregar dados pré-compilados
        data_path = os.path.join(project_root, 'data', 'alunos_compilado.json')
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pdf_processor.load_data(data)
        else:
            # Processar PDFs diretamente (não recomendado no Netlify)
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({"status": "error", "message": "Dados não compilados encontrados"})
            }
        
        # Headers CORS
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        
        # Roteamento simples
        if path == '/api/turmas' or path == '/turmas':
            codigos = set()
            for serie_dict in pdf_processor.students_data.values():
                for aluno in serie_dict.values():
                    arq = aluno.get('arquivo_origem')
                    if arq and arq.lower().endswith('.pdf'):
                        codigos.add(arq[:-4])
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({"status": "success", "data": sorted(codigos)})
            }
        
        elif path.startswith('/api/turma/') or path.startswith('/turma/'):
            codigo = path.split('/')[-1]
            alunos = pdf_processor.get_students_by_file(codigo)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({"status": "success", "data": alunos})
            }
        
        elif path == '/api/series' or path == '/series':
            series = list(pdf_processor.students_data.keys())
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({"status": "success", "data": sorted(series)})
            }
        
        elif path.startswith('/api/alunos/') or path.startswith('/alunos/'):
            serie = path.split('/')[-1]
            alunos = pdf_processor.get_students_by_serie(serie)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({"status": "success", "data": sorted(alunos)})
            }
        
        elif path.startswith('/api/aluno/'):
            parts = path.split('/')
            if len(parts) >= 4:
                serie = parts[-2]
                nome = parts[-1]
                dados = pdf_processor.get_student_data(serie, nome)
                if dados:
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps({"status": "success", "data": {"aluno": dados, "alertas": [], "risco_reprovacao": False, "risco_evasao": False}})
                    }
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({"status": "error", "message": "Aluno não encontrado"})
            }
        
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({"status": "error", "message": f"Endpoint não encontrado: {path}"})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"status": "error", "message": str(e)})
        }

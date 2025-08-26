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
    print("[handler] Event path:", event.get('path'))
    try:
        raw_path = event.get('path', '/')
        prefix = '/.netlify/functions/app'
        if raw_path.startswith(prefix):
            path = raw_path[len(prefix):] or '/'
        else:
            path = raw_path
        print('[handler] Normalized path:', path)

        # Instanciar processor e carregar dados
        pdf_processor = PDFProcessor()
        data_path = os.path.join(project_root, 'data', 'alunos_compilado.json')
        if not os.path.exists(data_path):
            return _resp(500, {"status":"error","message":"JSON compilado ausente"})
        with open(data_path, 'r', encoding='utf-8') as f:
            pdf_processor.load_data(json.load(f))

        # Roteamento
        if path in ('/api/turmas','/turmas'):
            codigos = set()
            for serie in pdf_processor.students_data.values():
                for aluno in serie.values():
                    arq = aluno.get('arquivo_origem','')
                    if arq.lower().endswith('.pdf'):
                        base = os.path.splitext(arq)[0].strip().replace('\r','').replace('\n','')
                        codigos.add(base)
            codigos = sorted(codigos)
            return _resp(200, {"status":"success","data":codigos})
        if path.startswith('/api/turma/') or path.startswith('/turma/'):
            codigo = path.split('/')[-1]
            alunos = pdf_processor.get_students_by_file(codigo)
            return _resp(200, {"status":"success","data":alunos})
        if path in ('/api/series','/series'):
            return _resp(200, {"status":"success","data":sorted(pdf_processor.students_data.keys())})
        if path.startswith('/api/alunos/') or path.startswith('/alunos/'):
            serie = path.split('/')[-1]
            alunos = pdf_processor.get_students_by_serie(serie)
            return _resp(200, {"status":"success","data":sorted(alunos)})
        if path.startswith('/api/aluno/'):
            parts = path.split('/')
            if len(parts) >= 4:
                serie = parts[-2]
                nome = parts[-1]
                dados = pdf_processor.get_student_data(serie, nome)
                if dados:
                    return _resp(200, {"status":"success","data":{"aluno":dados}})
            return _resp(404, {"status":"error","message":"Aluno não encontrado"})
        return _resp(404, {"status":"error","message":f"Endpoint não encontrado: {path}"})
    except Exception as e:
        return _resp(500, {"status":"error","message":str(e)})

def _resp(status, payload):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(payload, ensure_ascii=False)
    }

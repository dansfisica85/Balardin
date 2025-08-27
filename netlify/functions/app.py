import json
import os

def handler(event, context):
    """Função Netlify simplificada e robusta"""
    
    # Headers CORS padrão
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    try:
        # Log do evento
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        print(f"[Netlify] {method} {path}")
        
        # Tratar OPTIONS (CORS preflight)
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Normalizar path (remover prefixo da função)
        if path.startswith('/.netlify/functions/app'):
            path = path[len('/.netlify/functions/app'):] or '/'
        
        print(f"[Netlify] Normalized path: {path}")
        
        # Carregar dados compilados
        try:
            # Tentar vários caminhos possíveis para o JSON
            possible_paths = [
                'data/alunos_compilado.json',
                './data/alunos_compilado.json',
                '/opt/build/repo/data/alunos_compilado.json',
                os.path.join(os.getcwd(), 'data', 'alunos_compilado.json')
            ]
            
            data = None
            for json_path in possible_paths:
                if os.path.exists(json_path):
                    print(f"[Netlify] Found JSON at: {json_path}")
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    break
            
            if data is None:
                # Listar arquivos disponíveis para debug
                files = []
                try:
                    for root, dirs, file_list in os.walk('.'):
                        if 'alunos_compilado.json' in file_list:
                            files.append(os.path.join(root, 'alunos_compilado.json'))
                except:
                    pass
                
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({
                        'status': 'error',
                        'message': 'JSON compilado não encontrado',
                        'searched_paths': possible_paths,
                        'found_files': files,
                        'cwd': os.getcwd()
                    })
                }
                
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'status': 'error',
                    'message': f'Erro ao carregar JSON: {str(e)}'
                })
            }
        
        # Roteamento simplificado
        if path in ('/api/ping', '/ping', '/'):
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'ok',
                    'message': 'Netlify function is working',
                    'data_loaded': bool(data),
                    'series_count': len(data) if data else 0
                })
            }
        
        elif path in ('/api/turmas', '/turmas'):
            # Extrair códigos das turmas dos dados
            codigos = set()
            for serie_data in data.values():
                for aluno in serie_data.values():
                    arquivo = aluno.get('arquivo_origem', '')
                    if arquivo.endswith('.pdf'):
                        codigo = arquivo[:-4].strip()
                        codigos.add(codigo)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'data': sorted(list(codigos))
                })
            }
        
        elif path.startswith('/api/turma/') or path.startswith('/turma/'):
            # Obter dados de uma turma específica
            codigo = path.split('/')[-1]
            alunos_turma = []
            
            for serie_data in data.values():
                for aluno in serie_data.values():
                    arquivo = aluno.get('arquivo_origem', '')
                    if arquivo.endswith('.pdf') and arquivo[:-4].strip() == codigo:
                        alunos_turma.append({
                            'nome': aluno.get('nome', ''),
                            'ra': aluno.get('ra', ''),
                            'serie': aluno.get('serie', ''),
                            'turma': aluno.get('turma', ''),
                            'frequencia_media': aluno.get('frequencia_media', 0),
                            'total_faltas': aluno.get('total_faltas', 0)
                        })
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'data': alunos_turma
                })
            }
        
        elif path in ('/api/series', '/series'):
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'data': sorted(list(data.keys()))
                })
            }
        
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({
                    'status': 'error',
                    'message': f'Endpoint não encontrado: {path}'
                })
            }
            
    except Exception as e:
        print(f"[Netlify] Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'status': 'error',
                'message': f'Erro interno: {str(e)}'
            })
        }

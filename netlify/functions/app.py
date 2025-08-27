import json

def handler(event, context):
    """Função Netlify simplificada"""
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    try:
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        # Normalizar path
        if path.startswith('/.netlify/functions/app'):
            path = path[len('/.netlify/functions/app'):] or '/'
        
        # Tratar OPTIONS
        if method == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}
        
        # Mock data para teste
        mock_turmas = ["1A", "1B", "1C", "1D", "1E", "2A", "2B", "2C", "2D", "2E", "2F", "3A", "3B", "3C", "3D", "3E", "3F", "3G", "6A", "6B", "7A", "7B", "7C", "8A", "8B", "8C", "9A", "9B"]
        
        # Roteamento
        if path in ('/api/ping', '/ping', '/'):
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'status': 'ok', 'message': 'Function working', 'path': path})
            }
        
        elif path in ('/api/turmas', '/turmas'):
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'status': 'success', 'data': mock_turmas})
            }
        
        elif path.startswith('/api/turma/') or path.startswith('/turma/'):
            codigo = path.split('/')[-1]
            mock_alunos = [
                {"nome": f"Aluno Teste {i}", "ra": f"00000000{i:03d}-X", "serie": "1º ano", "frequencia_media": 90 + i}
                for i in range(1, 6)
            ]
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'status': 'success', 'data': mock_alunos, 'turma': codigo})
            }
        
        elif path in ('/api/series', '/series'):
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'status': 'success', 'data': ["1º ano", "2º ano", "3º ano", "6º ano", "7º ano", "8º ano", "9º ano"]})
            }
        
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'status': 'error', 'message': f'Endpoint não encontrado: {path}'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'status': 'error', 'message': str(e)})
        }

#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from netlify.functions.app import handler

# Teste local da função
if __name__ == "__main__":
    # Teste /api/turmas
    event = {
        'path': '/api/turmas',
        'httpMethod': 'GET',
        'queryStringParameters': None
    }
    
    response = handler(event, {})
    print("Teste /api/turmas:")
    print(f"Status: {response['statusCode']}")
    print(f"Body: {response['body']}")
    print()
    
    # Teste /api/turma/1A
    event = {
        'path': '/api/turma/1A',
        'httpMethod': 'GET',
        'queryStringParameters': None
    }
    
    response = handler(event, {})
    print("Teste /api/turma/1A:")
    print(f"Status: {response['statusCode']}")
    if response['statusCode'] == 200:
        import json
        data = json.loads(response['body'])
        if data['status'] == 'success':
            print(f"Alunos encontrados: {len(data['data'])}")
            if data['data']:
                primeiro = data['data'][0]
                print(f"Primeiro aluno: {primeiro['nome']} - {len(primeiro['disciplinas'])} disciplinas")
        else:
            print(f"Erro: {data['message']}")
    else:
        print(f"Body: {response['body']}")

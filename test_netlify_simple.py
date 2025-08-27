#!/usr/bin/env python3
"""Teste local da função Netlify simplificada"""

import sys
import os
sys.path.insert(0, 'netlify/functions')

from app import handler

def test_endpoint(path):
    """Testa um endpoint específico"""
    event = {
        'path': path,
        'httpMethod': 'GET'
    }
    
    context = {}
    
    print(f"\n=== Testando {path} ===")
    result = handler(event, context)
    
    print(f"Status: {result['statusCode']}")
    print(f"Headers: {result['headers']}")
    
    if result['body']:
        import json
        try:
            body_data = json.loads(result['body'])
            print(f"Body: {json.dumps(body_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Body (raw): {result['body'][:200]}...")
    
    return result

if __name__ == "__main__":
    print("Testando função Netlify localmente...")
    
    # Testar endpoints
    test_endpoint('/api/ping')
    test_endpoint('/api/turmas')
    
    # Testar uma turma específica se disponível
    turmas_result = test_endpoint('/api/turmas')
    if turmas_result['statusCode'] == 200:
        import json
        turmas_data = json.loads(turmas_result['body'])
        if turmas_data.get('data'):
            primeira_turma = turmas_data['data'][0]
            test_endpoint(f'/api/turma/{primeira_turma}')

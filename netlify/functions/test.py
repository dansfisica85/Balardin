def handler(event, context):
    """Função de teste minimalista"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': '{"status":"ok","message":"Netlify function is alive"}'
    }

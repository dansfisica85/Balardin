"""
Sistema de Análise de Desempenho Acadêmico
Aplicação Flask para análise de dados educacionais de PDFs
"""

from flask import Flask, render_template, jsonify, request
from pdf_processor_v2 import PDFProcessor
import os
import json

app = Flask(__name__)

# Inicializar o processador de PDFs
pdf_processor = PDFProcessor()

# Carregar dados dos PDFs na inicialização
def load_pdf_data():
    """Carrega e processa todos os PDFs na inicialização da aplicação"""
    pdf_directory = os.path.dirname(os.path.abspath(__file__))
    pdf_processor.process_all_pdfs(pdf_directory)

# Chamar a função de carregamento
with app.app_context():
    load_pdf_data()

@app.route('/')
def index():
    """Página principal do sistema"""
    return render_template('index.html')

@app.route('/api/series')
def get_series():
    """Retorna todas as séries/anos disponíveis"""
    try:
        series = pdf_processor.get_all_series()
        return jsonify({"status": "success", "data": sorted(series)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/alunos/<serie>')
def get_alunos_by_serie(serie):
    """Retorna todos os alunos de uma série específica"""
    try:
        alunos = pdf_processor.get_students_by_serie(serie)
        return jsonify({"status": "success", "data": sorted(alunos)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/aluno/<serie>/<nome_aluno>')
def get_dados_aluno(serie, nome_aluno):
    """Retorna os dados completos de um aluno específico"""
    try:
        dados = pdf_processor.get_student_data(serie, nome_aluno)
        if not dados:
            return jsonify({"status": "error", "message": "Aluno não encontrado"})
        
        # Calcular alertas
        alertas = []
        disciplinas_com_problema = []
        frequencia_baixa = False
        
        for disciplina in dados.get('disciplinas', []):
            # Verificar notas baixas
            if disciplina.get('media_semestral', 0) < 5:
                disciplinas_com_problema.append(disciplina['nome'])
                alertas.append({
                    "tipo": "reprovacao",
                    "disciplina": disciplina['nome'],
                    "media": disciplina['media_semestral'],
                    "message": f"Risco de reprovação em {disciplina['nome']} - Média: {disciplina['media_semestral']}"
                })
        
        # Verificar frequência
        if dados.get('frequencia_media', 100) < 75:
            frequencia_baixa = True
            alertas.append({
                "tipo": "evasao",
                "frequencia": dados['frequencia_media'],
                "message": f"RISCO DE EVASÃO - Frequência: {dados['frequencia_media']}%"
            })
        
        resultado = {
            "aluno": dados,
            "alertas": alertas,
            "risco_reprovacao": len(disciplinas_com_problema) > 0,
            "risco_evasao": frequencia_baixa,
            "disciplinas_problema": disciplinas_com_problema
        }
        
        return jsonify({"status": "success", "data": resultado})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/relatorio/notas-baixas')
def relatorio_notas_baixas():
    """Relatório de estudantes com notas abaixo de 5 agrupados por série"""
    try:
        relatorio = pdf_processor.get_low_grades_report()
        return jsonify({"status": "success", "data": relatorio})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/relatorio/frequencia-baixa')
def relatorio_frequencia_baixa():
    """Relatório de estudantes com frequência abaixo de 75% agrupados por série"""
    try:
        relatorio = pdf_processor.get_low_attendance_report()
        return jsonify({"status": "success", "data": relatorio})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/reprocessar')
def reprocessar_pdfs():
    """Reprocessa todos os PDFs (útil para atualizações)"""
    try:
        pdf_directory = os.path.dirname(os.path.abspath(__file__))
        pdf_processor.process_all_pdfs(pdf_directory)
        return jsonify({"status": "success", "message": "PDFs reprocessados com sucesso"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

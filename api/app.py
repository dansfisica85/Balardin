from flask import Flask, render_template, jsonify
import os, json
from pdf_processor_v2 import PDFProcessor

app = Flask(__name__, static_folder="../static", template_folder="../templates")

pdf_processor = PDFProcessor()
# Tentar carregar JSON pré-compilado para evitar processamento pesado em ambiente serverless
base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, '..', 'data', 'alunos_compilado.json')
if os.path.exists(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            pdf_processor.load_data(data)
            print('Dados pré-carregados do JSON.')
    except Exception as e:
        print('Falha ao carregar JSON pré-compilado:', e)
else:
    # fallback (cuidado: pode ser lento em Vercel)
    pdf_processor.process_all_pdfs(os.path.join(base_dir, '..'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/series')
def get_series():
    try:
        series = pdf_processor.get_all_series()
        return jsonify({"status": "success", "data": sorted(series)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/alunos/<serie>')
def get_alunos_by_serie(serie):
    try:
        alunos = pdf_processor.get_students_by_serie(serie)
        return jsonify({"status": "success", "data": sorted(alunos)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/aluno/<serie>/<nome_aluno>')
def get_dados_aluno(serie, nome_aluno):
    try:
        dados = pdf_processor.get_student_data(serie, nome_aluno)
        if not dados:
            return jsonify({"status": "error", "message": "Aluno não encontrado"})
        alertas = []
        disciplinas_com_problema = []
        frequencia_baixa = False
        for disciplina in dados.get('disciplinas', []):
            if disciplina.get('media_semestral', 0) < 5:
                disciplinas_com_problema.append(disciplina['nome'])
                alertas.append({
                    "tipo": "reprovacao",
                    "disciplina": disciplina['nome'],
                    "media": disciplina['media_semestral'],
                    "message": f"Risco de reprovação em {disciplina['nome']} - Média: {disciplina['media_semestral']}"
                })
        if dados.get('frequencia_media', 100) < 75:
            frequencia_baixa = True
            alertas.append({
                "tipo": "evasao",
                "frequencia": dados['frequencia_media'],
                "message": f"RISCO DE EVASÃO - Frequência: {dados['frequencia_media']}%"
            })
        return jsonify({"status": "success", "data": {
            "aluno": dados,
            "alertas": alertas,
            "risco_reprovacao": len(disciplinas_com_problema) > 0,
            "risco_evasao": frequencia_baixa,
            "disciplinas_problema": disciplinas_com_problema
        }})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/turmas')
def listar_turmas():
    """Lista códigos de turmas/arquivos disponíveis (derivado dos PDFs processados)."""
    try:
        # Extrair códigos únicos de arquivo_origem sem extensão
        codigos = set()
        for serie_dict in pdf_processor.students_data.values():
            for aluno in serie_dict.values():
                arq = aluno.get('arquivo_origem')
                if arq and arq.lower().endswith('.pdf'):
                    codigos.add(arq[:-4])
        return jsonify({"status": "success", "data": sorted(codigos)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/turma/<codigo>')
def dados_turma(codigo):
    """Retorna alunos completos de uma turma (arquivo)."""
    try:
        alunos = pdf_processor.get_students_by_file(codigo)
        return jsonify({"status": "success", "data": alunos})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/relatorio/notas-baixas')
def relatorio_notas_baixas():
    try:
        relatorio = pdf_processor.get_low_grades_report()
        return jsonify({"status": "success", "data": relatorio})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/relatorio/frequencia-baixa')
def relatorio_frequencia_baixa():
    try:
        relatorio = pdf_processor.get_low_attendance_report()
        return jsonify({"status": "success", "data": relatorio})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/relatorio/combinais')
def relatorio_combinado():
    try:
        relatorio = pdf_processor.get_combined_issues_report()
        return jsonify({"status": "success", "data": relatorio})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/resumo/series')
def resumo_series():
    try:
        resumo = pdf_processor.get_series_summary()
        return jsonify({"status": "success", "data": resumo})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/resumo/series/simples')
def resumo_series_simples():
    try:
        full = pdf_processor.get_series_summary()
        simples = {s: { 'alunos': d['alunos'], 'frequencia_media_serie': d['frequencia_media_serie'] } for s,d in full.items()}
        return jsonify({"status": "success", "data": simples})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/resumo/disciplinas')
def resumo_disciplinas_global():
    try:
        resumo = pdf_processor.get_discipline_summary()
        return jsonify({"status": "success", "data": resumo})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/resumo/disciplinas/<serie>')
def resumo_disciplinas_por_serie(serie):
    try:
        resumo = pdf_processor.get_discipline_summary(serie)
        return jsonify({"status": "success", "data": resumo})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Sem app.run para Vercel

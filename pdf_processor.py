"""
Processador de PDFs para extração de dados acadêmicos reais
Extraia dados específicos dos boletins escolares do Estado de SP
"""

import PyPDF2
import pdfplumber
import os
import re
from collections import defaultdict
import json

class PDFProcessor:
    def __init__(self):
        self.students_data = defaultdict(dict)
        self.series_data = defaultdict(list)
        
    def extract_text_from_pdf(self, pdf_path):
        """Extrai texto de um arquivo PDF usando múltiplas bibliotecas"""
        try:
            # Primeiro tenta com pdfplumber (melhor para tabelas)
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        
                if text.strip():
                    return text
                    
        except Exception as e:
            print(f"Erro com pdfplumber em {pdf_path}: {str(e)}")
        
        # Fallback para PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Erro ao processar {pdf_path}: {str(e)}")
            return ""
    
    def parse_student_data(self, text, filename):
        """Extrai dados específicos do aluno do texto do PDF"""
        
        # Dividir o texto em seções por aluno (cada página é um aluno)
        pages = text.split("GOVERNO DO ESTADO DE SÃO PAULO")
        students_found = []
        
        for page in pages:
            if "Nome do Aluno:" in page and "Boletim Escolar" in page:
                student_data = self.parse_single_student(page, filename)
                if student_data:
                    students_found.append(student_data)
        
        return students_found
    
    def parse_single_student(self, page_text, filename):
        """Extrai dados de um único aluno"""
        
        student_data = {
            "nome": "",
            "ra": "",
            "serie": "",
            "turma": "",
            "disciplinas": [],
            "frequencia_media": 0,
            "arquivo_origem": filename,
            "dados_brutos": []
        }
        
        # Extrair nome do aluno
        nome_match = re.search(r'Nome do Aluno:([^R]+?)RA:', page_text)
        if nome_match:
            student_data["nome"] = nome_match.group(1).strip()
        
        # Extrair RA
        ra_match = re.search(r'RA:([^\s/]+)', page_text)
        if ra_match:
            student_data["ra"] = ra_match.group(1).strip()
        
        # Extrair série/turma
        turma_match = re.search(r'Turma:([^\n]+)', page_text)
        if turma_match:
            turma_info = turma_match.group(1).strip()
            student_data["turma"] = turma_info
            
            # Extrair série
            if "1ª SERIE" in turma_info or "1° SERIE" in turma_info:
                student_data["serie"] = "1º ano"
            elif "2ª SERIE" in turma_info or "2° SERIE" in turma_info:
                student_data["serie"] = "2º ano"
            elif "3ª SERIE" in turma_info or "3° SERIE" in turma_info:
                student_data["serie"] = "3º ano"
            else:
                # Tentar extrair do nome do arquivo
                serie_match = re.search(r'(\d+)[A-Z]', filename)
                if serie_match:
                    student_data["serie"] = f"{serie_match.group(1)}º ano"
        
        # Extrair disciplinas e notas
        disciplinas = self.extract_disciplines_data(page_text)
        student_data["disciplinas"] = disciplinas
        
        # Calcular frequência média
        frequencias = []
        for disc in disciplinas:
            if disc.get('freq_1bim', 0) > 0:
                frequencias.append(disc['freq_1bim'])
            if disc.get('freq_2bim', 0) > 0:
                frequencias.append(disc['freq_2bim'])
        
        if frequencias:
            student_data["frequencia_media"] = round(sum(frequencias) / len(frequencias), 1)
        else:
            student_data["frequencia_media"] = 100  # Default
        
        return student_data if student_data["nome"] else None
    
    def extract_disciplines_data(self, page_text):
        """Extrai dados das disciplinas do texto da página"""
        disciplinas = []
        
        # Padrão para capturar linhas de disciplinas
        # Formato: DISCIPLINA NOTA1%FREQ1ACNOTA2%FREQ2AC...
        lines = page_text.split('\n')
        
        for line in lines:
            # Buscar por linhas que contenham disciplinas com dados
            if any(disc in line.upper() for disc in [
                'BIOLOGIA', 'EDUCACAO FISICA', 'FISICA', 'GEOGRAFIA', 'HISTORIA',
                'LINGUA PORTUGUESA', 'LINGUA INGLESA', 'MATEMATICA', 'QUIMICA',
                'SOCIOLOGIA', 'EDUCAÇÃO FINANCEIRA', 'LIDERANÇA', 'ORATÓRIA',
                'REDAÇÃO E LEITURA'
            ]):
                disciplina_data = self.parse_discipline_line(line)
                if disciplina_data:
                    disciplinas.append(disciplina_data)
        
        return disciplinas
    
    def parse_discipline_line(self, line):
        """Extrai dados de uma linha de disciplina"""
        
        # Remover espaços extras e normalizar
        line = re.sub(r'\s+', ' ', line.strip())
        
        # Extrair nome da disciplina (primeira palavra(s) até encontrar números)
        nome_match = re.match(r'^([A-ZÇÃÁÉÊÔÕÜàáçéêôõü\s]+)', line)
        if not nome_match:
            return None
            
        nome_disciplina = nome_match.group(1).strip()
        
        # Normalizar nomes de disciplinas
        nome_disciplina = self.normalize_discipline_name(nome_disciplina)
        
        # Extrair dados numéricos da linha
        # Padrão: DISCIPLINA NOTA1%FREQ1ACNOTA2%FREQ2AC...
        dados_numericos = re.findall(r'(\d+)(\d+%)?(-)?(\d+%)?(\d*)', line)
        
        # Tentar extrair nota e frequência do 1º e 2º bimestre
        disciplina_data = {
            "nome": nome_disciplina,
            "nota_1bim": 0,
            "freq_1bim": 0,
            "ac_1bim": 0,
            "nota_2bim": 0,
            "freq_2bim": 0,
            "ac_2bim": 0,
            "media_semestral": 0
        }
        
        # Padrão mais específico para dados do boletim
        # Buscar padrões como: 7385%-6291%
        padrao_dados = re.findall(r'(\d+)(\d+%)-?(\d*)(\d+%)?', line)
        
        if padrao_dados:
            # Primeiro bimestre
            if len(padrao_dados) >= 1:
                try:
                    nota1 = int(padrao_dados[0][0])
                    freq1 = int(padrao_dados[0][1].replace('%', ''))
                    
                    # Converter nota (parece estar em formato condensado)
                    if nota1 >= 100:
                        # Dividir dígitos (ex: 7385 = nota 7, freq 85%)
                        nota_str = str(nota1)
                        if len(nota_str) >= 3:
                            disciplina_data["nota_1bim"] = int(nota_str[0])
                            disciplina_data["freq_1bim"] = int(nota_str[1:])
                    else:
                        disciplina_data["nota_1bim"] = nota1
                        disciplina_data["freq_1bim"] = freq1
                        
                except (ValueError, IndexError):
                    pass
            
            # Segundo bimestre
            if len(padrao_dados) >= 2:
                try:
                    nota2 = int(padrao_dados[1][0])
                    freq2 = int(padrao_dados[1][1].replace('%', ''))
                    
                    if nota2 >= 100:
                        nota_str = str(nota2)
                        if len(nota_str) >= 3:
                            disciplina_data["nota_2bim"] = int(nota_str[0])
                            disciplina_data["freq_2bim"] = int(nota_str[1:])
                    else:
                        disciplina_data["nota_2bim"] = nota2
                        disciplina_data["freq_2bim"] = freq2
                        
                except (ValueError, IndexError):
                    pass
        
        # Calcular média semestral
        if disciplina_data["nota_1bim"] > 0 and disciplina_data["nota_2bim"] > 0:
            disciplina_data["media_semestral"] = round(
                (disciplina_data["nota_1bim"] + disciplina_data["nota_2bim"]) / 2, 1
            )
        elif disciplina_data["nota_1bim"] > 0:
            disciplina_data["media_semestral"] = disciplina_data["nota_1bim"]
        elif disciplina_data["nota_2bim"] > 0:
            disciplina_data["media_semestral"] = disciplina_data["nota_2bim"]
        
        return disciplina_data if disciplina_data["nome"] else None
    
    def normalize_discipline_name(self, nome):
        """Normaliza nomes de disciplinas"""
        nome = nome.upper().strip()
        
        normalizacoes = {
            'LINGUA PORTUGUESA': 'Língua Portuguesa',
            'LINGUA INGLESA': 'Língua Inglesa',
            'MATEMATICA': 'Matemática',
            'EDUCACAO FISICA': 'Educação Física',
            'EDUCAÇÃO FINANCEIRA': 'Educação Financeira',
            'GEOGRAFIA': 'Geografia',
            'HISTORIA': 'História',
            'BIOLOGIA': 'Biologia',
            'FISICA': 'Física',
            'QUIMICA': 'Química',
            'SOCIOLOGIA': 'Sociologia',
            'LIDERANÇA': 'Liderança',
            'ORATÓRIA': 'Oratória',
            'REDAÇÃO E LEITURA': 'Redação e Leitura'
        }
        
        return normalizacoes.get(nome, nome.title())
    
    def process_all_pdfs(self, directory):
        """Processa todos os PDFs no diretório"""
        print("Iniciando processamento dos PDFs...")
        
        # Limpar dados anteriores
        self.students_data.clear()
        self.series_data.clear()
        
        pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
        total_students = 0
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(directory, pdf_file)
            print(f"Processando: {pdf_file}")
            
            text = self.extract_text_from_pdf(pdf_path)
            if text:
                # Processar múltiplos alunos por PDF
                students_list = self.parse_student_data(text, pdf_file)
                
                for student_data in students_list:
                    if student_data and student_data["nome"]:
                        serie = student_data["serie"]
                        nome = student_data["nome"]
                        
                        if serie not in self.students_data:
                            self.students_data[serie] = {}
                        
                        self.students_data[serie][nome] = student_data
                        
                        # Armazenar na estrutura por série
                        if nome not in self.series_data[serie]:
                            self.series_data[serie].append(nome)
                        
                        total_students += 1
                        print(f"  → {nome} ({serie})")
        
        print(f"Processamento concluído. {len(pdf_files)} arquivos processados.")
        print(f"Total de alunos encontrados: {total_students}")
        print(f"Séries encontradas: {list(self.students_data.keys())}")
        
        # Debug: mostrar alguns dados
        for serie, alunos in list(self.students_data.items())[:2]:
            print(f"\nSérie {serie}: {len(alunos)} alunos")
            for nome, dados in list(alunos.items())[:3]:
                print(f"  - {nome}: {len(dados['disciplinas'])} disciplinas, freq: {dados['frequencia_media']}%")
    
    def get_all_series(self):
        """Retorna todas as séries disponíveis"""
        return list(self.students_data.keys())
    
    def get_students_by_serie(self, serie):
        """Retorna todos os estudantes de uma série"""
        return list(self.students_data.get(serie, {}).keys())
    
    def get_student_data(self, serie, nome_aluno):
        """Retorna dados de um estudante específico"""
        return self.students_data.get(serie, {}).get(nome_aluno)
    
    def get_low_grades_report(self):
        """Gera relatório de estudantes com notas abaixo de 5"""
        relatorio = {}
        
        for serie, estudantes in self.students_data.items():
            relatorio[serie] = []
            
            for nome, dados in estudantes.items():
                disciplinas_problema = []
                
                for disciplina in dados.get('disciplinas', []):
                    if disciplina.get('media_semestral', 0) < 5:
                        disciplinas_problema.append({
                            "disciplina": disciplina['nome'],
                            "media": disciplina['media_semestral'],
                            "nota_1bim": disciplina['nota_1bim'],
                            "nota_2bim": disciplina['nota_2bim']
                        })
                
                if disciplinas_problema:
                    relatorio[serie].append({
                        "nome": nome,
                        "disciplinas_problema": disciplinas_problema,
                        "total_disciplinas_problema": len(disciplinas_problema)
                    })
        
        # Remover séries sem problemas
        relatorio = {k: v for k, v in relatorio.items() if v}
        
        return relatorio
    
    def get_low_attendance_report(self):
        """Gera relatório de estudantes com frequência abaixo de 75%"""
        relatorio = {}
        
        for serie, estudantes in self.students_data.items():
            relatorio[serie] = []
            
            for nome, dados in estudantes.items():
                frequencia = dados.get('frequencia_media', 100)
                
                if frequencia < 75:
                    relatorio[serie].append({
                        "nome": nome,
                        "frequencia": frequencia,
                        "risco_nivel": "ALTO" if frequencia < 60 else "MÉDIO"
                    })
        
        # Remover séries sem problemas
        relatorio = {k: v for k, v in relatorio.items() if v}
        
        return relatorio

"""
Processador de PDFs MELHORADO para extração precisa de dados acadêmicos
Baseado na análise real dos boletins escolares do Estado de SP
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
        """Extrai texto de um arquivo PDF usando pdfplumber prioritariamente"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                return text
        except Exception as e:
            print(f"Erro com pdfplumber em {pdf_path}: {str(e)}")
            return ""
    
    def parse_student_data(self, text, filename):
        """Extrai dados de múltiplos alunos do texto do PDF"""
        students_found = []

        # Contagem diagnóstica: quantas ocorrências de "Nome do Aluno:" o texto tem
        ocorrencias_nome = text.count("Nome do Aluno:")
        if ocorrencias_nome == 0:
            # Nada a fazer
            return students_found
        print(f"    → Ocorrências 'Nome do Aluno:' detectadas (bruto): {ocorrencias_nome}")

        # Estratégia mais robusta: sempre dividir por "Nome do Aluno:" e reconstruir
        parts = text.split("Nome do Aluno:")
        for i, part in enumerate(parts[1:], 1):  # ignorar prefixo
            section = "Nome do Aluno:" + part
            student_data = self.parse_single_student(section, filename)
            if student_data and student_data["nome"]:
                students_found.append(student_data)
            else:
                # Diagnóstico mínimo quando falha
                preview = part[:80].replace('\n', ' ')
                print(f"      (Descartado possível aluno {i}: preview='{preview}...')")

        # Se a perda for grande (menos de 50% das ocorrências viraram alunos), avisar
        if students_found and ocorrencias_nome > 0 and len(students_found) < ocorrencias_nome * 0.5:
            print(f"    [ALERTA] Apenas {len(students_found)}/{ocorrencias_nome} seções válidas ({round(len(students_found)/ocorrencias_nome*100,1)}%). Ajustar regex pode ser necessário.")

        return students_found
    
    def parse_single_student(self, section_text, filename):
        """Extrai dados de um único aluno de uma seção do PDF"""
        
        student_data = {
            "nome": "",
            "ra": "",
            "serie": "",
            "turma": "",
            "disciplinas": [],
            "frequencia_media": 0,
            "total_faltas": 0,
            "arquivo_origem": filename
        }
        
        # Extrair nome do aluno
        # Nome pode ir até RA:, Turma:, ou quebra dupla. Permitir letras R no meio (antes regex cortava em qualquer 'R').
        nome_match = re.search(r'Nome do Aluno:\s*(.+?)(?=(RA:|Turma:|\n\n|$))', section_text, flags=re.DOTALL)
        if nome_match:
            nome = nome_match.group(1)
            # Remover possíveis labels truncados no fim
            nome = re.sub(r'(RA:|Turma:).*', '', nome, flags=re.IGNORECASE)
            nome = re.sub(r'\s+', ' ', nome).strip(' -:')
            # Filtrar nomes muito curtos (ruído)
            if len(nome) >= 3:
                student_data["nome"] = nome
        
        # Extrair RA
        ra_match = re.search(r'RA:\s*([0-9X-]+)', section_text)
        if ra_match:
            student_data["ra"] = ra_match.group(1).strip()
        
        # Extrair série/turma
        turma_match = re.search(r'Turma:\s*([^\n]+)', section_text)
        if turma_match:
            turma_info = turma_match.group(1).strip()
            student_data["turma"] = turma_info
            
            # Determinar série com regex genérico (captura 1,2,3,6-9 + SERIE/SÉRIE/ANO com variações de º ° ª)
            serie_regex = re.search(r'\b([1236789])\s*[º°ª]?(?:\s*(?:SERIE|SÉRIE|ANO))', turma_info, flags=re.IGNORECASE)
            if serie_regex:
                student_data["serie"] = f"{serie_regex.group(1)}º ano"
            else:
                # Fallback pelo nome do arquivo
                serie_match = re.search(r'(\d+)[A-Z]', filename)
                if serie_match:
                    ano_num = serie_match.group(1)
                    if ano_num in ['1','2','3','6','7','8','9']:
                        student_data["serie"] = f"{ano_num}º ano"
        
        # Extrair disciplinas
        disciplinas = self.extract_disciplines_from_section(section_text)
        student_data["disciplinas"] = disciplinas
        
        # Calcular frequência média e total de faltas
        frequencias = []
        total_faltas = 0
        
        for disciplina in disciplinas:
            # Frequência do semestre (média dos dois bimestres)
            freq_values = []
            if disciplina.get('freq_1bim', 0) > 0:
                freq_values.append(disciplina['freq_1bim'])
            if disciplina.get('freq_2bim', 0) > 0:
                freq_values.append(disciplina['freq_2bim'])
            
            if freq_values:
                freq_disciplina = sum(freq_values) / len(freq_values)
                frequencias.append(freq_disciplina)
            
            # Somar faltas
            total_faltas += disciplina.get('faltas_1bim', 0) + disciplina.get('faltas_2bim', 0)
        
        if frequencias:
            student_data["frequencia_media"] = round(sum(frequencias) / len(frequencias), 1)
        else:
            student_data["frequencia_media"] = 100
            
        student_data["total_faltas"] = total_faltas
        
        return student_data
    
    def extract_disciplines_from_section(self, section_text):
        """Extrai dados das disciplinas de uma seção"""
        disciplinas = []
        
        # Lista de disciplinas conhecidas
        disciplinas_conhecidas = [
            'BIOLOGIA', 'EDUCACAO FISICA', 'FISICA', 'GEOGRAFIA', 'HISTORIA',
            'LINGUA PORTUGUESA', 'LINGUA INGLESA', 'MATEMATICA', 'QUIMICA',
            'SOCIOLOGIA', 'EDUCAÇÃO FINANCEIRA', 'LIDERANÇA', 'ORATÓRIA',
            'REDAÇÃO E LEITURA', 'ARTE', 'FILOSOFIA'
        ]
        
        lines = section_text.split('\n')
        
        for line in lines:
            line_upper = line.upper()
            
            # Verificar se a linha contém uma disciplina conhecida
            for disciplina_nome in disciplinas_conhecidas:
                if disciplina_nome in line_upper:
                    disciplina_data = self.parse_discipline_line(line, disciplina_nome)
                    if disciplina_data:
                        disciplinas.append(disciplina_data)
                    break
        
        return disciplinas
    
    def parse_discipline_line(self, line, disciplina_nome):
        """Extrai dados de uma linha de disciplina"""
        
        # Normalizar nome da disciplina
        nome_normalizado = self.normalize_discipline_name(disciplina_nome)
        
        # Padrão: DISCIPLINA NOTA1 FALTAS1 FREQ1% - NOTA2 FALTAS2 FREQ2% - ...
        # Exemplo: BIOLOGIA 5 5 75% - 7 7 68% - - - - - - - - - - 12 72% -
        
        disciplina_data = {
            "nome": nome_normalizado,
            "nota_1bim": 0,
            "faltas_1bim": 0,
            "freq_1bim": 0,
            "nota_2bim": 0,
            "faltas_2bim": 0,
            "freq_2bim": 0,
            "media_semestral": 0,
            "total_faltas": 0,
            "freq_semestral": 0
        }
        
        # Remover o nome da disciplina da linha
        dados_line = line.upper().replace(disciplina_nome, "").strip()
        
        # Extrair sequências de números seguidos de %
        # Padrão: NUMERO NUMERO NUMERO% - NUMERO NUMERO NUMERO% - ...
        padrao = r'(\d+)\s+(\d+)\s+(\d+)%'
        matches = re.findall(padrao, dados_line)
        
        if len(matches) >= 1:
            # Primeiro bimestre
            try:
                disciplina_data["nota_1bim"] = int(matches[0][0])
                disciplina_data["faltas_1bim"] = int(matches[0][1])
                disciplina_data["freq_1bim"] = int(matches[0][2])
            except (ValueError, IndexError):
                pass
        
        if len(matches) >= 2:
            # Segundo bimestre
            try:
                disciplina_data["nota_2bim"] = int(matches[1][0])
                disciplina_data["faltas_2bim"] = int(matches[1][1])
                disciplina_data["freq_2bim"] = int(matches[1][2])
            except (ValueError, IndexError):
                pass
        
        # Calcular médias
        notas_validas = []
        if disciplina_data["nota_1bim"] > 0:
            notas_validas.append(disciplina_data["nota_1bim"])
        if disciplina_data["nota_2bim"] > 0:
            notas_validas.append(disciplina_data["nota_2bim"])
        
        if notas_validas:
            disciplina_data["media_semestral"] = round(sum(notas_validas) / len(notas_validas), 1)
        
        # Calcular frequência semestral
        freqs_validas = []
        if disciplina_data["freq_1bim"] > 0:
            freqs_validas.append(disciplina_data["freq_1bim"])
        if disciplina_data["freq_2bim"] > 0:
            freqs_validas.append(disciplina_data["freq_2bim"])
        
        if freqs_validas:
            disciplina_data["freq_semestral"] = round(sum(freqs_validas) / len(freqs_validas), 1)
        
        # Total de faltas
        disciplina_data["total_faltas"] = disciplina_data["faltas_1bim"] + disciplina_data["faltas_2bim"]
        
        return disciplina_data if nome_normalizado else None
    
    def normalize_discipline_name(self, nome):
        """Normaliza nomes de disciplinas"""
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
            'REDAÇÃO E LEITURA': 'Redação e Leitura',
            'ARTE': 'Arte',
            'FILOSOFIA': 'Filosofia'
        }
        
        return normalizacoes.get(nome.upper(), nome.title())
    
    def process_all_pdfs(self, directory):
        """Processa todos os PDFs no diretório"""
        print("Iniciando processamento MELHORADO dos PDFs...")
        
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
                students_list = self.parse_student_data(text, pdf_file)
                
                for student_data in students_list:
                    if student_data and student_data["nome"]:
                        serie = student_data["serie"]
                        nome = student_data["nome"]
                        
                        if serie not in self.students_data:
                            self.students_data[serie] = {}
                        
                        self.students_data[serie][nome] = student_data
                        
                        if nome not in self.series_data[serie]:
                            self.series_data[serie].append(nome)
                        
                        total_students += 1
                        print(f"  → {nome} ({serie}) - {len(student_data['disciplinas'])} disciplinas")
        
        print(f"\nProcessamento concluído!")
        print(f"- {len(pdf_files)} arquivos processados")
        print(f"- {total_students} alunos encontrados")
        print(f"- Séries: {list(self.students_data.keys())}")
        
        # Estatísticas por série
        for serie, alunos in self.students_data.items():
            print(f"  {serie}: {len(alunos)} alunos")
    
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
                    if disciplina.get('media_semestral', 0) < 5 and disciplina.get('media_semestral', 0) > 0:
                        disciplinas_problema.append({
                            "disciplina": disciplina['nome'],
                            "media": disciplina['media_semestral'],
                            "nota_1bim": disciplina['nota_1bim'],
                            "nota_2bim": disciplina['nota_2bim'],
                            "freq_semestral": disciplina.get('freq_semestral', 0)
                        })
                
                if disciplinas_problema:
                    relatorio[serie].append({
                        "nome": nome,
                        "disciplinas_problema": disciplinas_problema,
                        "total_disciplinas_problema": len(disciplinas_problema)
                    })
        
        # Remover séries sem problemas
        return {k: v for k, v in relatorio.items() if v}
    
    def get_low_attendance_report(self):
        """Gera relatório de estudantes com frequência abaixo de 75%"""
        relatorio = {}
        
        for serie, estudantes in self.students_data.items():
            relatorio[serie] = []
            
            for nome, dados in estudantes.items():
                frequencia = dados.get('frequencia_media', 100)
                total_faltas = dados.get('total_faltas', 0)
                
                if frequencia < 75:
                    relatorio[serie].append({
                        "nome": nome,
                        "frequencia": frequencia,
                        "total_faltas": total_faltas,
                        "risco_nivel": "ALTO" if frequencia < 60 else "MÉDIO"
                    })
        
        return {k: v for k, v in relatorio.items() if v}

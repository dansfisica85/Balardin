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
        # Cache simples para agregações (invalidado a cada novo processamento)
        self._cache_series_summary = None
        self._cache_global_discipline_summary = None
        
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
        # Invalidar caches
        self._cache_series_summary = None
        self._cache_global_discipline_summary = None

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
        """Relatório de estudantes por série com disciplinas cuja frequência semestral < 75%.
        Estrutura:
        {
          '1º ano': [
             {
               'nome': 'Aluno X',
               'frequencia_media_aluno': 72.3,
               'disciplinas_freq_baixa': [
                   { 'disciplina': 'Matemática', 'freq_semestral': 60, 'freq_1bim': 55, 'freq_2bim': 65, 'total_faltas': 18 }
               ],
               'total_disciplinas_freq_baixa': 2,
               'risco_nivel': 'ALTO',
               'menor_freq': 60
             }, ...
          ], ...
        }
        """
        relatorio = {}
        for serie, estudantes in self.students_data.items():
            alunos_lista = []
            for nome, dados in estudantes.items():
                disciplinas_baixa = []
                for disc in dados.get('disciplinas', []):
                    freq = disc.get('freq_semestral', 0)
                    if 0 < freq < 75:
                        disciplinas_baixa.append({
                            'disciplina': disc['nome'],
                            'freq_semestral': freq,
                            'freq_1bim': disc.get('freq_1bim', 0),
                            'freq_2bim': disc.get('freq_2bim', 0),
                            'total_faltas': disc.get('total_faltas', 0)
                        })
                if disciplinas_baixa:
                    min_freq = min(d['freq_semestral'] for d in disciplinas_baixa)
                    risco_nivel = 'ALTO' if min_freq < 60 else 'MÉDIO'
                    alunos_lista.append({
                        'nome': nome,
                        'frequencia_media_aluno': dados.get('frequencia_media', 0),
                        'disciplinas_freq_baixa': disciplinas_baixa,
                        'total_disciplinas_freq_baixa': len(disciplinas_baixa),
                        'risco_nivel': risco_nivel,
                        'menor_freq': min_freq
                    })
            if alunos_lista:
                relatorio[serie] = alunos_lista
        return relatorio

    def get_low_attendance_by_discipline_report(self):
        """Relatório de frequência baixa (<75%) por disciplina para cada aluno (usa freq_semestral da disciplina)."""
        relatorio = {}
        for serie, estudantes in self.students_data.items():
            alunos_lista = []
            for nome, dados in estudantes.items():
                disciplinas_baixa = []
                for disc in dados.get('disciplinas', []):
                    freq = disc.get('freq_semestral', 0)
                    if 0 < freq < 75:
                        disciplinas_baixa.append({
                            'disciplina': disc['nome'],
                            'freq_semestral': freq,
                            'freq_1bim': disc.get('freq_1bim', 0),
                            'freq_2bim': disc.get('freq_2bim', 0),
                            'total_faltas': disc.get('total_faltas', 0)
                        })
                if disciplinas_baixa:
                    alunos_lista.append({
                        'nome': nome,
                        'frequencia_media_aluno': dados.get('frequencia_media', 0),
                        'disciplinas_freq_baixa': disciplinas_baixa,
                        'total_disciplinas_freq_baixa': len(disciplinas_baixa)
                    })
            if alunos_lista:
                relatorio[serie] = alunos_lista
        return relatorio

    # ===================== AGREGAÇÕES / RESUMOS =====================
    def get_series_summary(self):
        """Resumo consolidado por série: quantidade de alunos, médias e estatísticas de disciplinas.
        Estrutura:
        {
          '1º ano': {
             'alunos': 261,
             'frequencia_media_serie': 87.5,
             'disciplinas': {
                 'Matemática': {
                     'media_geral': 6.3,
                     'media_1bim': 6.1,
                     'media_2bim': 6.5,
                     'freq_media': 88.2,
                     'alunos_media_baixa': 42,
                     'alunos_media_baixa_pct': 16.1,
                     'registros': 261
                 }, ...
             }
          }, ...
        }
        """
        if self._cache_series_summary is not None:
            return self._cache_series_summary

        resumo = {}
        for serie, alunos_dict in self.students_data.items():
            alunos = list(alunos_dict.values())
            if not alunos:
                continue
            # Frequência média da série (média das frequências médias dos alunos)
            freq_media_serie = round(sum(a.get('frequencia_media', 100) for a in alunos)/len(alunos), 2)
            disciplinas_stats = {}
            # Acumular por disciplina
            for aluno in alunos:
                for disc in aluno.get('disciplinas', []):
                    nome = disc['nome']
                    dstat = disciplinas_stats.setdefault(nome, {
                        'soma_media': 0.0,
                        'count_media': 0,
                        'soma_nota_1': 0.0,
                        'count_nota_1': 0,
                        'soma_nota_2': 0.0,
                        'count_nota_2': 0,
                        'soma_freq_1': 0.0,
                        'count_freq_1': 0,
                        'soma_freq_2': 0.0,
                        'count_freq_2': 0,
                        'alunos_media_baixa': 0,
                        'registros': 0
                    })
                    media = disc.get('media_semestral', 0)
                    if media > 0:
                        dstat['soma_media'] += media
                        dstat['count_media'] += 1
                        if media < 5:
                            dstat['alunos_media_baixa'] += 1
                    n1 = disc.get('nota_1bim', 0)
                    if n1 > 0:
                        dstat['soma_nota_1'] += n1
                        dstat['count_nota_1'] += 1
                    n2 = disc.get('nota_2bim', 0)
                    if n2 > 0:
                        dstat['soma_nota_2'] += n2
                        dstat['count_nota_2'] += 1
                    f1 = disc.get('freq_1bim', 0)
                    if f1 > 0:
                        dstat['soma_freq_1'] += f1
                        dstat['count_freq_1'] += 1
                    f2 = disc.get('freq_2bim', 0)
                    if f2 > 0:
                        dstat['soma_freq_2'] += f2
                        dstat['count_freq_2'] += 1
                    dstat['registros'] += 1

            # Finalizar estatísticas
            disciplinas_formatadas = {}
            for nome, d in disciplinas_stats.items():
                media_geral = round(d['soma_media']/d['count_media'], 2) if d['count_media'] else 0
                media_1 = round(d['soma_nota_1']/d['count_nota_1'], 2) if d['count_nota_1'] else 0
                media_2 = round(d['soma_nota_2']/d['count_nota_2'], 2) if d['count_nota_2'] else 0
                freq_media_1 = round(d['soma_freq_1']/d['count_freq_1'], 2) if d['count_freq_1'] else 0
                freq_media_2 = round(d['soma_freq_2']/d['count_freq_2'], 2) if d['count_freq_2'] else 0
                # Frequência semestral consolidada (média das médias por bimestre existentes)
                freqs_validas = [f for f in [freq_media_1, freq_media_2] if f > 0]
                freq_media = round(sum(freqs_validas)/len(freqs_validas), 2) if freqs_validas else 0
                baixa_pct = round(d['alunos_media_baixa']/d['count_media']*100, 2) if d['count_media'] else 0
                disciplinas_formatadas[nome] = {
                    'media_geral': media_geral,
                    'media_1bim': media_1,
                    'media_2bim': media_2,
                    'freq_media_1bim': freq_media_1,
                    'freq_media_2bim': freq_media_2,
                    'freq_media': freq_media,
                    'alunos_media_baixa': d['alunos_media_baixa'],
                    'alunos_media_baixa_pct': baixa_pct,
                    'registros': d['registros']
                }

            resumo[serie] = {
                'alunos': len(alunos),
                'frequencia_media_serie': freq_media_serie,
                'disciplinas': disciplinas_formatadas
            }

        self._cache_series_summary = resumo
        return resumo

    def get_discipline_summary(self, serie=None):
        """Resumo global ou por série de cada disciplina.
        Se serie for None: considera todos os alunos.
        Estrutura: {
           'Matemática': { ... }, ...
        }
        """
        if serie is None and self._cache_global_discipline_summary is not None:
            return self._cache_global_discipline_summary

        disciplinas_stats = {}
        series_alvo = [serie] if serie else list(self.students_data.keys())

        for s in series_alvo:
            for aluno in self.students_data.get(s, {}).values():
                for disc in aluno.get('disciplinas', []):
                    nome = disc['nome']
                    d = disciplinas_stats.setdefault(nome, {
                        'soma_media': 0.0, 'count_media': 0,
                        'soma_nota_1': 0.0, 'count_nota_1': 0,
                        'soma_nota_2': 0.0, 'count_nota_2': 0,
                        'soma_freq_1': 0.0, 'count_freq_1': 0,
                        'soma_freq_2': 0.0, 'count_freq_2': 0,
                        'alunos_media_baixa': 0,
                        'registros': 0
                    })
                    media = disc.get('media_semestral', 0)
                    if media > 0:
                        d['soma_media'] += media
                        d['count_media'] += 1
                        if media < 5:
                            d['alunos_media_baixa'] += 1
                    n1 = disc.get('nota_1bim', 0)
                    if n1 > 0:
                        d['soma_nota_1'] += n1
                        d['count_nota_1'] += 1
                    n2 = disc.get('nota_2bim', 0)
                    if n2 > 0:
                        d['soma_nota_2'] += n2
                        d['count_nota_2'] += 1
                    f1 = disc.get('freq_1bim', 0)
                    if f1 > 0:
                        d['soma_freq_1'] += f1
                        d['count_freq_1'] += 1
                    f2 = disc.get('freq_2bim', 0)
                    if f2 > 0:
                        d['soma_freq_2'] += f2
                        d['count_freq_2'] += 1
                    d['registros'] += 1

        resultado = {}
        for nome, d in disciplinas_stats.items():
            media_geral = round(d['soma_media']/d['count_media'], 2) if d['count_media'] else 0
            media_1 = round(d['soma_nota_1']/d['count_nota_1'], 2) if d['count_nota_1'] else 0
            media_2 = round(d['soma_nota_2']/d['count_nota_2'], 2) if d['count_nota_2'] else 0
            freq_media_1 = round(d['soma_freq_1']/d['count_freq_1'], 2) if d['count_freq_1'] else 0
            freq_media_2 = round(d['soma_freq_2']/d['count_freq_2'], 2) if d['count_freq_2'] else 0
            freqs_validas = [f for f in [freq_media_1, freq_media_2] if f > 0]
            freq_media = round(sum(freqs_validas)/len(freqs_validas), 2) if freqs_validas else 0
            baixa_pct = round(d['alunos_media_baixa']/d['count_media']*100, 2) if d['count_media'] else 0
            resultado[nome] = {
                'media_geral': media_geral,
                'media_1bim': media_1,
                'media_2bim': media_2,
                'freq_media_1bim': freq_media_1,
                'freq_media_2bim': freq_media_2,
                'freq_media': freq_media,
                'alunos_media_baixa': d['alunos_media_baixa'],
                'alunos_media_baixa_pct': baixa_pct,
                'registros': d['registros']
            }

        if serie is None:
            self._cache_global_discipline_summary = resultado
        return resultado

    # ===================== RELATÓRIO COMBINADO =====================
    def get_combined_issues_report(self):
        """Combina problemas de nota (<5) e frequência (<75%) por série e aluno.
        Estrutura:
        {
          '1º ano': [
             {
               'nome': 'Aluno X',
               'frequencia_media_aluno': 82.5,
               'disciplinas_nota_baixa': [...],  # mesmo formato de get_low_grades_report
               'disciplinas_freq_baixa': [...],  # mesmo formato de get_low_attendance_report
               'total_disciplinas_nota_baixa': n,
               'total_disciplinas_freq_baixa': m,
               'risco_reprovacao': bool,
               'risco_evasao': bool
             }, ...
          ], ...
        }
        """
        notas = self.get_low_grades_report()
        freq = self.get_low_attendance_report()
        combinado = {}

        series = set(list(notas.keys()) + list(freq.keys()))
        for serie in series:
            alunos_map = {}
            # Notas
            for registro in notas.get(serie, []):
                alunos_map[registro['nome']] = {
                    'nome': registro['nome'],
                    'frequencia_media_aluno': 0,
                    'disciplinas_nota_baixa': registro['disciplinas_problema'],
                    'disciplinas_freq_baixa': [],
                    'total_disciplinas_nota_baixa': registro['total_disciplinas_problema'],
                    'total_disciplinas_freq_baixa': 0,
                    'risco_reprovacao': True,
                    'risco_evasao': False
                }
            # Frequência
            for registro in freq.get(serie, []):
                entry = alunos_map.get(registro['nome'])
                if not entry:
                    entry = {
                        'nome': registro['nome'],
                        'frequencia_media_aluno': registro.get('frequencia_media_aluno', 0),
                        'disciplinas_nota_baixa': [],
                        'disciplinas_freq_baixa': registro.get('disciplinas_freq_baixa', []),
                        'total_disciplinas_nota_baixa': 0,
                        'total_disciplinas_freq_baixa': registro.get('total_disciplinas_freq_baixa', 0),
                        'risco_reprovacao': False,
                        'risco_evasao': True if registro.get('menor_freq', 100) < 75 or registro.get('frequencia_media_aluno', 100) < 75 else False
                    }
                    alunos_map[registro['nome']] = entry
                else:
                    entry['frequencia_media_aluno'] = registro.get('frequencia_media_aluno', entry.get('frequencia_media_aluno', 0))
                    entry['disciplinas_freq_baixa'] = registro.get('disciplinas_freq_baixa', [])
                    entry['total_disciplinas_freq_baixa'] = registro.get('total_disciplinas_freq_baixa', 0)
                    if registro.get('menor_freq', 100) < 75 or registro.get('frequencia_media_aluno', 100) < 75:
                        entry['risco_evasao'] = True
            # Ajustar risco evasão para itens que vieram só de notas mas possuem frequência baixa calculável em dados originais
            for nome, entry in alunos_map.items():
                if not entry['risco_evasao'] and entry['frequencia_media_aluno'] and entry['frequencia_media_aluno'] < 75:
                    entry['risco_evasao'] = True
            combinado[serie] = list(alunos_map.values())
        return combinado

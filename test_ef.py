#!/usr/bin/env python3
"""
Teste específico para arquivos do Ensino Fundamental
"""

import pdfplumber
import re

def extract_student_from_ef_pdf(filepath):
    """Extrair dados de um arquivo do Ensino Fundamental"""
    try:
        with pdfplumber.open(filepath) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            
            # Extrair informações básicas
            print(f"\n=== ANALISANDO {filepath} ===")
            
            # Nome do aluno
            nome_match = re.search(r'Nome do Aluno:\s*([^R]+?)(?=RA:|$)', text)
            if nome_match:
                nome = nome_match.group(1).strip()
                nome = re.sub(r'\s+', ' ', nome)
                print(f"Nome: {nome}")
            
            # RA
            ra_match = re.search(r'RA:\s*([0-9X-]+)', text)
            if ra_match:
                ra = ra_match.group(1).strip()
                print(f"RA: {ra}")
            
            # Turma
            turma_match = re.search(r'Turma:\s*([^\n]+)', text)
            if turma_match:
                turma = turma_match.group(1).strip()
                print(f"Turma: {turma}")
                
                # Determinar série
                serie = ""
                if "6° ANO" in turma or "6ª ANO" in turma:
                    serie = "6º ano"
                elif "7° ANO" in turma or "7ª ANO" in turma:
                    serie = "7º ano"
                elif "8° ANO" in turma or "8ª ANO" in turma:
                    serie = "8º ano"
                elif "9° ANO" in turma or "9ª ANO" in turma:
                    serie = "9º ano"
                
                print(f"Série detectada: {serie}")
            
            # Verificar disciplinas
            print("Primeiras linhas com disciplinas:")
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if re.search(r'\d+\s+\d+\s+\d+%', line):
                    print(f"  Linha {i}: {line.strip()}")
                    if i > lines.index([l for l in lines if 'Disciplina' in l][0]) + 10:  # Limitar output
                        break
                        
    except Exception as e:
        print(f"Erro ao processar {filepath}: {e}")

# Testar alguns arquivos do EF
arquivos_ef = ['6A.pdf', '7A.pdf', '8A.pdf', '9A.pdf']

for arquivo in arquivos_ef:
    try:
        extract_student_from_ef_pdf(arquivo)
    except Exception as e:
        print(f"Erro com {arquivo}: {e}")

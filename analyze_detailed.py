"""
Script para analisar e melhorar a extração de dados dos PDFs
"""

import pdfplumber
import re

def analyze_specific_pdf(filename):
    """Analisa um PDF específico para entender melhor o formato"""
    print(f"\n{'='*60}")
    print(f"ANÁLISE DETALHADA: {filename}")
    print(f"{'='*60}")
    
    with pdfplumber.open(filename) as pdf:
        for page_num, page in enumerate(pdf.pages[:2]):  # Analisar 2 primeiras páginas
            print(f"\n--- PÁGINA {page_num + 1} ---")
            
            text = page.extract_text()
            if not text:
                continue
                
            lines = text.split('\n')
            
            # Procurar por padrões específicos
            for i, line in enumerate(lines):
                # Nome do aluno
                if "Nome do Aluno:" in line:
                    print(f"NOME ENCONTRADO: {line}")
                    if i + 1 < len(lines):
                        print(f"LINHA SEGUINTE: {lines[i+1]}")
                
                # RA
                if "RA:" in line:
                    print(f"RA ENCONTRADO: {line}")
                
                # Turma
                if "Turma:" in line:
                    print(f"TURMA ENCONTRADA: {line}")
                
                # Disciplinas com dados numéricos
                if any(disc in line.upper() for disc in ['BIOLOGIA', 'MATEMATICA', 'FISICA', 'PORTUGUES']):
                    print(f"DISCIPLINA: {line}")
                    
                    # Tentar extrair padrões numéricos
                    numeros = re.findall(r'\d+', line)
                    if len(numeros) >= 4:
                        print(f"  NÚMEROS ENCONTRADOS: {numeros}")
                        
                    # Tentar padrão específico do boletim
                    padrao = re.findall(r'(\d+)(\d{2,3}%)', line)
                    if padrao:
                        print(f"  PADRÃO NOTA-FREQ: {padrao}")

if __name__ == "__main__":
    analyze_specific_pdf("2A.pdf")

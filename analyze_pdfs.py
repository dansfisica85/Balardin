"""
Script para examinar o conteúdo real dos PDFs e entender a estrutura dos dados
"""

import pdfplumber
import PyPDF2
import os

def analyze_pdf(pdf_path):
    """Analisa um PDF e extrai todo o conteúdo possível"""
    print(f"\n{'='*60}")
    print(f"ANALISANDO: {os.path.basename(pdf_path)}")
    print(f"{'='*60}")
    
    # Tentar com pdfplumber (melhor para tabelas)
    try:
        print("\n--- USANDO PDFPLUMBER ---")
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                print(f"\n>>> PÁGINA {i+1} <<<")
                
                # Extrair texto
                text = page.extract_text()
                if text:
                    print("TEXTO EXTRAÍDO:")
                    print(text[:1000] + "..." if len(text) > 1000 else text)
                
                # Tentar extrair tabelas
                tables = page.extract_tables()
                if tables:
                    print(f"\n{len(tables)} TABELA(S) ENCONTRADA(S):")
                    for j, table in enumerate(tables):
                        print(f"\nTabela {j+1}:")
                        for row in table[:5]:  # Mostrar primeiras 5 linhas
                            print(row)
                        if len(table) > 5:
                            print(f"... e mais {len(table)-5} linhas")
                
    except Exception as e:
        print(f"Erro com pdfplumber: {e}")
    
    # Tentar com PyPDF2 como fallback
    try:
        print("\n--- USANDO PyPDF2 ---")
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(pdf_reader.pages):
                print(f"\n>>> PÁGINA {i+1} <<<")
                text = page.extract_text()
                if text:
                    print("TEXTO EXTRAÍDO:")
                    print(text[:1000] + "..." if len(text) > 1000 else text)
                
    except Exception as e:
        print(f"Erro com PyPDF2: {e}")

def main():
    """Analisa alguns PDFs para entender a estrutura"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Analisar os primeiros PDFs
    test_files = ['1A.pdf', '1B.pdf', '2A.pdf']
    
    for filename in test_files:
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            analyze_pdf(filepath)
        else:
            print(f"Arquivo não encontrado: {filename}")

if __name__ == "__main__":
    main()

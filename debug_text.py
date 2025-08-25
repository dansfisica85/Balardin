"""
Debug do texto extraído
"""

from pdf_processor_v2 import PDFProcessor
import re

def debug_pdf_text():
    processor = PDFProcessor()
    
    text = processor.extract_text_from_pdf("2A.pdf")
    
    print("TEXTO COMPLETO EXTRAÍDO:")
    print("="*60)
    print(text[:2000])  # Primeiros 2000 caracteres
    print("\n" + "="*60)
    
    # Procurar por padrões de notas
    print("\nPROCURANDO PADRÕES DE NOTAS:")
    
    # Padrão que achamos antes
    pattern1 = r'([A-ZÁÊÃÇÕ\s]+)\s+(\d+)\s+(\d+)\s+(\d+%)\s+-\s+(\d+)\s+(\d+)\s+(\d+%)\s+-'
    matches1 = re.findall(pattern1, text)
    print(f"\nPadrão 1 encontrou {len(matches1)} matches:")
    for match in matches1[:3]:
        print(f"  {match}")
    
    # Padrão mais flexível
    pattern2 = r'([A-ZÁÊÃÇÕ\s]+)\s+(\d+(?:\.\d+)?)\s+(\d+)\s+(\d+%)'
    matches2 = re.findall(pattern2, text)
    print(f"\nPadrão 2 encontrou {len(matches2)} matches:")
    for match in matches2[:5]:
        print(f"  {match}")
    
    # Procurar por linhas que contenham números e %
    print("\nLINHAS COM NÚMEROS E %:")
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if '%' in line and any(char.isdigit() for char in line):
            print(f"  Linha {i}: {line.strip()}")
            if i > 50:  # Limitar saída
                break

if __name__ == "__main__":
    debug_pdf_text()

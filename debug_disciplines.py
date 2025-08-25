"""
Debug específico das disciplinas
"""

from pdf_processor_v2 import PDFProcessor
import re

def debug_disciplines():
    processor = PDFProcessor()
    
    text = processor.extract_text_from_pdf("2A.pdf")
    
    # Extrair dados do aluno diretamente
    students = processor.parse_student_data(text, "2A.pdf")
    
    print(f"Estudantes encontrados: {len(students)}")
    
    if students:
        # Pegar primeiro estudante
        first_student = students[0]
        
        print("\nPrimeiro estudante:")
        print("="*60)
        print(f"Nome: {first_student['nome']}")
        print(f"RA: {first_student['ra']}")
        print(f"Série: {first_student['serie']}")
        print(f"Disciplinas: {len(first_student['disciplinas'])}")
        
        # Mostrar algumas disciplinas
        for i, disc in enumerate(first_student['disciplinas'][:3]):
            print(f"\nDisciplina {i+1}:")
            for key, value in disc.items():
                print(f"  {key}: {value}")
        
        # Testar linha específica
        print("\nTestando linha específica:")
        linha_teste = "BIOLOGIA 5 5 75% - 7 7 68% - - - - - - - - - - 12 72% -"
        
        resultado = processor.parse_discipline_line(linha_teste, "BIOLOGIA")
        
        print("Resultado do parse:")
        if resultado:
            for key, value in resultado.items():
                print(f"  {key}: {value}")
        else:
            print("  Nenhum resultado obtido")
            
        # Testar com uma linha do texto real
        print("\nTestando com linha real do PDF:")
        lines = text.split('\n')
        for line in lines:
            if 'BIOLOGIA' in line.upper() and '%' in line:
                print(f"Linha encontrada: {line}")
                resultado_real = processor.parse_discipline_line(line, "BIOLOGIA")
                if resultado_real:
                    print("Resultado:")
                    for key, value in resultado_real.items():
                        print(f"  {key}: {value}")
                break

if __name__ == "__main__":
    debug_disciplines()

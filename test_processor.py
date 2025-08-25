"""
Teste do novo processador de PDFs
"""

from pdf_processor import PDFProcessor
import os

def test_processor():
    processor = PDFProcessor()
    
    # Testar com um PDF específico
    test_file = "2A.pdf"  # Escolher um arquivo que sabemos ter dados
    
    if os.path.exists(test_file):
        print(f"Testando processamento de {test_file}...")
        
        # Extrair texto
        text = processor.extract_text_from_pdf(test_file)
        print(f"Texto extraído: {len(text)} caracteres")
        
        # Processar dados
        students = processor.parse_student_data(text, test_file)
        
        print(f"Alunos encontrados: {len(students)}")
        
        for i, student in enumerate(students[:3]):  # Mostrar primeiros 3
            print(f"\n--- ALUNO {i+1} ---")
            print(f"Nome: {student['nome']}")
            print(f"RA: {student['ra']}")
            print(f"Série: {student['serie']}")
            print(f"Frequência média: {student['frequencia_media']}%")
            print(f"Disciplinas: {len(student['disciplinas'])}")
            
            for disc in student['disciplinas'][:3]:  # Mostrar primeiras 3 disciplinas
                print(f"  - {disc['nome']}: N1={disc['nota_1bim']}, N2={disc['nota_2bim']}, Média={disc['media_semestral']}")
    else:
        print(f"Arquivo {test_file} não encontrado")

if __name__ == "__main__":
    test_processor()

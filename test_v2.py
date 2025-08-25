"""
Teste do processador melhorado
"""

from pdf_processor_v2 import PDFProcessor
import os

def test_new_processor():
    processor = PDFProcessor()
    
    print("Testando novo processador...")
    
    # Testar com um PDF específico
    test_file = "2A.pdf"
    
    if os.path.exists(test_file):
        text = processor.extract_text_from_pdf(test_file)
        students = processor.parse_student_data(text, test_file)
        
        print(f"\nAlunos encontrados: {len(students)}")
        
        for i, student in enumerate(students[:2]):  # Mostrar primeiros 2
            print(f"\n{'='*50}")
            print(f"ALUNO {i+1}")
            print(f"{'='*50}")
            print(f"Nome: {student['nome']}")
            print(f"RA: {student['ra']}")
            print(f"Série: {student['serie']}")
            print(f"Frequência média: {student['frequencia_media']}%")
            print(f"Total de faltas: {student['total_faltas']}")
            print(f"Disciplinas: {len(student['disciplinas'])}")
            
            print(f"\nDisciplinas detalhadas:")
            for disc in student['disciplinas']:
                print(f"  {disc['nome']}:")
                print(f"    1º Bim: Nota={disc['nota_1bim']}, Faltas={disc['faltas_1bim']}, Freq={disc['freq_1bim']}%")
                print(f"    2º Bim: Nota={disc['nota_2bim']}, Faltas={disc['faltas_2bim']}, Freq={disc['freq_2bim']}%")
                print(f"    Média: {disc['media_semestral']}, Freq Semestral: {disc['freq_semestral']}%")
                
                # Destacar problemas
                if disc['media_semestral'] < 5 and disc['media_semestral'] > 0:
                    print(f"    ⚠️  RISCO DE REPROVAÇÃO!")
                if disc['freq_semestral'] < 75:
                    print(f"    🔴 RISCO DE EVASÃO!")
                print()
    else:
        print(f"Arquivo {test_file} não encontrado")

if __name__ == "__main__":
    test_new_processor()

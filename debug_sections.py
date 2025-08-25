"""
Debug das seções de estudantes
"""

from pdf_processor_v2 import PDFProcessor

def debug_sections():
    processor = PDFProcessor()
    
    text = processor.extract_text_from_pdf("2A.pdf")
    
    # Dividir por seções como faz o processador
    sections = text.split("GOVERNO DO ESTADO DE SÃO PAULO")
    
    print(f"Seções encontradas: {len(sections)}")
    
    for i, section in enumerate(sections):
        if "Nome do Aluno:" in section and "Boletim Escolar" in section:
            print(f"\n{'='*60}")
            print(f"SEÇÃO {i} - VÁLIDA")
            print(f"{'='*60}")
            
            # Mostrar início da seção
            print("Início da seção:")
            print(section[:500])
            print("\n" + "-"*40)
            
            # Procurar por disciplinas
            lines = section.split('\n')
            
            disciplinas_encontradas = []
            for line_num, line in enumerate(lines):
                line_upper = line.upper()
                if 'BIOLOGIA' in line_upper and '%' in line:
                    print(f"Linha {line_num}: {line}")
                    disciplinas_encontradas.append(line)
            
            print(f"\nDisciplinas com BIOLOGIA encontradas: {len(disciplinas_encontradas)}")
            
            # Testar extração
            disciplinas = processor.extract_disciplines_from_section(section)
            print(f"Disciplinas extraídas pelo processador: {len(disciplinas)}")
            
            if disciplinas:
                bio = [d for d in disciplinas if 'biologia' in d['nome'].lower()]
                if bio:
                    print(f"Dados da Biologia extraídos:")
                    for key, value in bio[0].items():
                        print(f"  {key}: {value}")
            
            break  # Só analisar primeiro aluno
        else:
            print(f"Seção {i}: Não é uma seção válida de aluno")

if __name__ == "__main__":
    debug_sections()

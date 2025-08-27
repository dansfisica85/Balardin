import os, json
from pdf_processor_v2 import PDFProcessor

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    proc = PDFProcessor()
    proc.process_all_pdfs(base_dir)
    out_path = os.path.join(base_dir, 'data', 'alunos_compilado.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(proc.export_data(), f, ensure_ascii=False, separators=(',', ':'))
    print('Gerado:', out_path)

if __name__ == '__main__':
    main()

from pathlib import Path
from pypdf import PdfReader,PdfWriter

ROOT=Path('/Users/ever/Documents/ChatGPT/Vision')
filled=PdfReader(ROOT/'tmp/pdfs/filled_source.pdf')
solutions=PdfReader(ROOT/'tmp/pdfs/midsem_solutions.pdf')
assert len(filled.pages)==93 and len(solutions.pages)==13
w=PdfWriter()
for p in filled.pages[:91]:w.add_page(p)
for p in solutions.pages:w.add_page(p)
for p in filled.pages[91:]:w.add_page(p)
for title,page in [('Worksheet 1 - Unit I',0),('Worksheet 2 - Unit II',20),
                   ('Worksheet 3 - Unit III',49),('Mid-semester question paper',89),
                   ('Mid-semester answers Q1-Q11',91),('OR choices - study appendix',102),
                   ('Completed literature survey',104)]:w.add_outline_item(title,page)
w.add_metadata({'/Title':'Research Methodology - Completed Assignment',
                '/Author':'Veer Vikram Singh',
                '/Subject':'Worksheets 1-3, mid-semester solutions and seven-paper literature survey'})
path=ROOT/'output/pdf/Research_Methodology_Completed_Assignment.pdf'
with path.open('wb') as f:w.write(f)
assert len(PdfReader(path).pages)==106
print('Revised assignment assembled: 106 pages.')

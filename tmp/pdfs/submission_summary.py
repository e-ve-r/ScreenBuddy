from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from pypdf import PdfReader

ROOT = Path('/Users/ever/Documents/ChatGPT/Vision')
OUT = ROOT / 'output/pdf/Research_Methodology_8_Page_Summary.pdf'
PAGES = [
('Worksheet 1: Understanding research', 'Part 1 of 2', [
('What the worksheet was about', 'Worksheet 1 introduced the basic meaning and purpose of research. It asked me to distinguish a broad topic from a research problem, arrange the research process, identify research approaches, and develop a focused question. I understood research as a planned investigation that uses evidence to answer a clear question.'),
('How I approached the answers', 'I answered the definition and classification questions briefly, then used examples to explain the differences. A topic such as artificial intelligence is broad. A research problem needs a specific difficulty, a question, suitable evidence and a manageable scope. I placed problem identification first, followed by a hypothesis, data collection and analysis, and interpretation.'),
('My proposed study', 'For the personal activities, I used lightweight network intrusion detection. My question was whether a random forest using 15 features could reduce prediction time while keeping its F1 score close to the full-feature model. F1 combines precision and recall. I proposed using the public UNSW-NB15 dataset, Python and one laptop within eight weeks.'),
('What I learned', 'I learned that a popular subject is only a starting point. A useful research problem should be clear, feasible and relevant. Its question, objectives, scope and measurements must support the same purpose.'),
]),
('Worksheet 1: Planning and interpreting', 'Part 2 of 2', [
('What the activities asked', 'The later activities asked me to write SMART objectives, define study boundaries, classify data, select collection tools, and distinguish analysis from interpretation. They also asked me to use given performance values to make a sensible choice.'),
('How I built the plan', 'I made the objectives specific, measurable, achievable, relevant and time-bound. For the proposed intrusion-detection study, I planned to prepare the data, train both models, and compare F1, false-positive rate and prediction time. I limited the study to one dataset and one laptop. I treated the existing dataset as secondary data and any timings I would collect as primary data.'),
('How I answered the examples', 'I matched each tool to its purpose: a questionnaire for opinions, Wireshark for packets, and a timer for execution time. In the supplied model comparison, B had the highest accuracy and A was fastest. When accuracy had to be at least 93% and speed mattered, I selected C for further investigation.'),
('My main takeaway', 'Analysis describes a result; interpretation explains what it means for the research question. The best method depends on the objective. I also learned that calibration, consistent conditions and repeatable measurements matter. The proposed study is a plan, so I did not present expected improvements as measured findings.'),
]),
('Worksheet 2: Reasoning and evidence', 'Part 1 of 2', [
('What the worksheet was about', 'Worksheet 2 explored how researchers form claims, challenge them, and decide what evidence can support them. It asked about dialectic, deduction, induction, abduction, demonstrations, experiments and mathematical proofs.'),
('How I handled claims', 'I looked for assumptions and possible counterexamples before accepting a claim. For example, greedy choices do not always give the best solution. With coins of values 1, 3 and 4, making 6 greedily uses 4+1+1, while 3+3 uses fewer coins. I therefore restricted the claim to problems where the required greedy-choice property holds.'),
('How I distinguished the methods', 'I described deduction as moving from a general rule to a specific conclusion. Induction uses observations to suggest a wider pattern. Abduction looks for a likely explanation, such as investigating slow database queries when an application becomes slow. I matched demonstrations to selected working examples, experiments to measured comparisons, and proofs to statements that must follow logically.'),
('What I learned from proof activities', 'I used simple examples for direct proof, contradiction, induction and contrapositive reasoning. For direct proof, adding two even numbers gives another even number. The main lesson was that successful examples cannot prove a universal claim. Evidence should match the claim, and every conclusion should state its assumptions and limits.'),
]),
('Worksheet 2: Models and fair testing', 'Part 2 of 2', [
('What the later activities asked', 'The worksheet then asked me to choose theoretical models, describe an algorithm, outline research software, write a mathematical model, and plan performance evaluation. It also used an irrigation example to connect these ideas.'),
('How I answered the modelling tasks', 'I connected graphs with networks, finite automata with regular languages, and Turing machines with computability. For the algorithm activity, I chose binary search: define the sorted-array input, identify the output, explain the search steps, and state its time and space requirements. I included tests for an empty array, boundary values and a missing target.'),
('How I planned evaluation', 'For the proposed intrusion detector, I kept the test data, laptop and measurement method the same for both models. I planned to compare detection quality, false alerts and prediction time. For irrigation, I suggested comparing adaptive and fixed watering in similar plots, while checking rainfall and sensor accuracy. In the supplied model table, A had higher accuracy and recall, while B had higher precision and F1.'),
('My main takeaway', 'A model simplifies reality, so its assumptions matter. Good research software needs testing, documentation and recorded settings. A fair experiment needs a baseline and controlled conditions. I learned to separate a hypothesis or expected result from an observation actually obtained through testing.'),
]),
('Worksheet 3: Finding and reviewing literature', 'Part 1 of 2', [
('What the worksheet was about', 'Worksheet 3 introduced literature searching, critical reading, synthesis, mapping and citation. It asked me to choose databases and keywords, build search strings, examine papers, and identify a possible research gap.'),
('How I approached the search', 'I started with the intrusion-detection question and used terms such as machine learning, lightweight detection, latency and feature selection. I used AND to combine ideas and OR to include alternatives. I chose computing sources such as IEEE Xplore and ACM Digital Library. I also used original papers and institutional repositories to check publication details and methods.'),
('How I organized the evidence', 'For each paper, I recorded its problem, method, dataset, finding and limitation. I grouped the seven papers in the literature review around benchmark datasets and efficient attack detection. I compared the studies rather than assuming that the highest reported accuracy was automatically the strongest result. I treated differences in datasets and test conditions as important.'),
('What I learned', 'A literature review should connect findings, not simply list paper summaries. Backward citation searching finds earlier sources; forward searching finds later related work. Mapping helps reveal recurring themes and limitations. I identified lightweight detection on independent traffic as a possible gap that would need further evidence before being claimed as new.'),
]),
('Worksheet 3: Writing and research ethics', 'Part 2 of 2', [
('What the activities asked', 'The later activities asked me to format references, paraphrase a passage, identify plagiarism and ethical violations, and plan responsible data use. They also covered authorship, informed consent and institutional ethics review.'),
('How I answered the writing tasks', 'I used simple independent wording and gave references for borrowed ideas. I understood that replacing a few words is not proper paraphrasing. Exact wording needs quotation marks, and paraphrased ideas still need citation. I distinguished plagiarism from fabrication, which invents evidence, and falsification, which changes evidence misleadingly.'),
('How I approached ethical planning', 'For the proposed dataset study, I did not claim to recruit participants. I explained that dataset terms and privacy risks still need checking. I proposed restricted access, removal of direct identifiers, and sharing only permitted results. In the healthcare case, I considered consent, withdrawal, false alerts, missed events and unequal performance. I also linked authorship to real contributions and responsibility.'),
('My main takeaway', 'Research quality includes honesty and respect for people. A similarity percentage alone cannot decide whether writing is ethical. Citations, source wording and context must be checked. Removing names may still leave re-identification risks. I learned to report limitations openly and avoid presenting imagined data or predicted outcomes as completed research.'),
]),
('Mid-semester: Explaining the research process', 'Part 1 of 2', [
('What the questions covered', 'The mid-semester questions asked me to explain the research process, the importance of defining a problem, plagiarism prevention, fact-finding, literature review, experimental designs, hypotheses, reasoning and types of research. They brought together ideas from the three worksheets.'),
('How I structured the answers', 'I followed the question numbers and subparts. For questions with fewer marks, I gave a definition and a few clear points. For longer questions, I added explanations, examples and limitations. I linked problem definition to scope, objectives, methods and evaluation, and explained how a literature review helps avoid repeating existing work.'),
('How I explained designs and reasoning', 'For experimental designs, I described how before-and-after measurements, control groups, randomization, blocks and factorial combinations help make comparisons fair. I explained a hypothesis as a testable prediction with measurable variables. I distinguished deduction from induction using their starting points and the certainty of their conclusions.'),
('What I learned', 'Basic or fundamental research builds general knowledge, while applied research addresses a practical need. Industrial research is guided by organizational goals and may also be applied. My main learning was that definitions become more useful when connected to examples. An answer should explain why a method is suitable, instead of merely naming it.'),
]),
('Mid-semester: Applying ideas and reflecting', 'Part 2 of 2', [
('How I approached the statistical question', 'The vaccine question asked whether vaccination was associated with survival. I first checked the table: 15 vaccinated goats survived and 2 died; 4 unvaccinated goats survived and 10 died. The death counts add to 12, although the printed total was 21. I used the cell counts to avoid carrying that error into the calculation.'),
('How I interpreted the answer', 'I stated the null hypothesis as independence between vaccination and survival. The chi-square value was about 11.52, above the 5% critical value of 3.84 for one degree of freedom. I therefore rejected independence. The given data supported an association favoring vaccination, but wider causal claims would depend on the study design.'),
('How I answered the remaining topics', 'I explained experience and pilot surveys, problem components and rephrasing. For the academic-integrity questions, I emphasized independent paraphrasing, citation and checking the meaning of similarity matches. I treated AI-assisted rewriting as something requiring factual verification, attribution and compliance with institutional rules.'),
('My overall learning', 'Across the assignments, I learned to move from a broad interest to a clear question, choose suitable evidence, test fairly and explain results carefully. I also learned to check numerical consistency and question assumptions. A good research answer combines clear reasoning, honest reporting, useful examples and proper credit to sources.'),
]),
]

def main():
    from detailed_summary_content import PAGES, HEADINGS
    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setTitle('Research Methodology - Student Assignment Summary')
    c.setAuthor('Veer Vikram Singh')
    w, h = A4
    body = ParagraphStyle('body', fontName='Helvetica', fontSize=11.5, leading=16.1, textColor=HexColor('#202a31'))
    counts = []
    for page_no, (title, part, blocks) in enumerate(PAGES, 1):
        assert tuple(heading for heading,_ in blocks)==HEADINGS
        c.setFillColor(HexColor('#202a31'))
        c.setFont('Helvetica', 9)
        c.drawString(48, h-33, 'RESEARCH METHODOLOGY - ASSIGNMENT SUMMARY')
        c.setStrokeColor(HexColor('#b8c4c8')); c.line(48, h-43, w-48, h-43)
        c.setFont('Helvetica-Bold', 17)
        c.drawString(48, h-76, title)
        c.setFont('Helvetica', 10)
        c.drawString(48, h-95, part)
        y = h-117
        for heading, text in blocks:
            c.setFillColor(HexColor('#202a31')); c.setFont('Helvetica-Bold', 12)
            c.drawString(48, y, heading); y -= 10
            for paragraph in ([text] if isinstance(text,str) else text):
                p = Paragraph(escape(paragraph), body)
                _, ph = p.wrap(w-96, h)
                p.drawOn(c, 48, y-ph); y -= ph+7
            y -= 12
        assert y >= 64, (page_no, y)
        c.setStrokeColor(HexColor('#b8c4c8')); c.line(48, 47, w-48, 47)
        c.setFillColor(HexColor('#202a31')); c.setFont('Helvetica', 8.5)
        c.drawString(48, 31, 'Veer Vikram Singh  |  SAP ID: 590014281  |  Batch: CCVT- 2')
        c.drawRightString(w-48, 31, f'{page_no} / 8')
        c.showPage()
        counts.append(len(' '.join(t if isinstance(t,str) else ' '.join(t) for _,t in blocks).split()))
    c.save()
    assert len(PdfReader(OUT).pages) == 8
    print('Eight-page submission summary created. Words per page:', counts)

if __name__ == '__main__':
    main()

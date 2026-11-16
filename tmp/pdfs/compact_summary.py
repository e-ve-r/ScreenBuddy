from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from pypdf import PdfReader

ROOT = Path('/Users/ever/Documents/ChatGPT/Vision')
OUT = ROOT / 'output/pdf/Research_Methodology_4_Page_Summary.pdf'
HEADINGS = ('1. What was asked or tested', '2. How I answered and explained it', '3. My learning and takeaways')
PAGES = [
('Worksheet 1: Research, planning and evidence', [
('1. What was asked or tested', 'Worksheet 1 tested my understanding of research, its stages and approaches, and the difference between a topic and a research problem. It asked me to create a study, write SMART objectives, set boundaries, classify data, choose tools and interpret supplied results.'),
('2. How I answered and explained it', [
'I defined research as a planned investigation using evidence. I arranged the chain as problem identification, hypothesis, data collection and analysis, then interpretation. I distinguished exploratory research, which investigates unfamiliar issues, from descriptive research, which reports characteristics, and analytical research, which examines relationships. Theoretical research uses logic and models; empirical research uses observations or experiments.',
'I classified "Artificial Intelligence in Smart Cities" as a topic because it lacks a precise question. For my own problem, I proposed comparing full-feature and 15-feature random forests on UNSW-NB15. My question was whether fewer features could reduce prediction time while limiting the F1-score loss to 0.02. I used literature limitations and practical difficulties as sources of research questions.',
'I made the objectives specific, measurable, achievable, relevant and time-bound: prepare data by week 2, train models by week 6 and report results by week 8. I limited the study to one laptop and dataset. I selected F1, which combines precision and recall, false-positive rate and prediction time, with the same test data and five timing runs.',
'I classified existing network data as secondary and my proposed timing measurements as primary. Numerical readings are quantitative; user comments are qualitative. I matched questionnaires to opinions, Wireshark to packets and monitoring tools to processor use. In the supplied results, B was most accurate and A fastest. When at least 93% accuracy and speed mattered, I chose C: 94% accuracy in 25 milliseconds.'
]),
('3. My learning and takeaways', 'I learned that a useful problem needs a clear question, realistic scope and suitable evidence. Analysis identifies patterns; interpretation explains their meaning. The best model depends on the objective. Calibration and consistent settings improve reliability. My personal study remained a proposal, so I did not report expected improvements as measured results.'),
]),
('Worksheet 2: Reasoning, models and testing', [
('1. What was asked or tested', 'Worksheet 2 tested how I challenged claims, classified reasoning, selected validation methods and constructed proofs. It also asked me to choose theoretical models, describe an algorithm, plan software, use mathematical modelling and evaluate performance through computing and irrigation examples.'),
('2. How I answered and explained it', [
'I explained dialectic as examining, challenging and refining a claim. To challenge "greedy algorithms are always optimal," I used coins worth 1, 3 and 4 to make 6. Greedy gives 4+1+1, but 3+3 uses fewer coins. I therefore restricted the claim to problems where the best immediate choices give the best complete solution.',
'I described deduction as applying a general rule to a case, induction as suggesting a wider pattern from observations, and abduction as proposing a likely explanation to investigate. Demonstrations establish selected working cases; empirical tests compare measurements; mathematical proofs establish conclusions under assumptions. For direct proof, 2m+2n equals 2(m+n), so two even integers have an even sum. I also used contradiction, a base case and induction step, and contrapositive reasoning.',
'I matched graphs to networks and finite automata to regular languages. For binary search, I specified a sorted array and target as inputs, and a position or -1 as output. Halving the search range gives O(log n) time; the iterative version uses O(1) extra space. I included empty arrays, boundary items and missing targets as tests.',
'I proposed modular software, version control, documentation and recorded settings. In the queue model, arrival rate lambda and service rate mu determine mean time W = 1/(mu - lambda), under the M/M/1 assumptions with lambda below mu. For evaluation, I kept conditions equal and compared quality and speed. The supplied A model had higher accuracy and recall; B had higher precision and F1. For irrigation, I proposed moisture thresholds and comparison with fixed watering, checking rainfall and sensor errors.'
]),
('3. My learning and takeaways', 'I learned that evidence must match the claim. A few successful cases cannot prove universal correctness, while a counterexample can expose an overstatement. Models depend on assumptions, software needs testing, and experiments need fair baselines. I distinguished expected improvement from an observed result and mathematical induction from uncertain generalization based on observations.'),
]),
('Worksheet 3: Literature and research ethics', [
('1. What was asked or tested', 'Worksheet 3 tested academic searching, keyword selection, critical reading, synthesis, mapping and citation. It also asked me to format references, paraphrase, identify misconduct, and plan responsible data use, consent, authorship and ethics review.'),
('2. How I answered and explained it', [
'I chose IEEE Xplore and ACM Digital Library for computing literature. My search combined "intrusion detection" AND "machine learning" AND (latency OR lightweight). AND connects required ideas; OR includes alternatives. I checked original papers and repositories, recording each study\'s problem, method, dataset, finding and limitation.',
'I examined test independence, fair comparisons and whether conclusions matched the evidence. I used analysis to examine individual papers and synthesis to connect them. In the seven-paper review, I grouped benchmark quality and efficient detection. Moustafa and Slay (2015) introduced UNSW-NB15; Sharafaldin and colleagues (2018) introduced CICIDS2017. Different datasets and test conditions mean accuracy figures cannot always be ranked directly.',
'I explained backward chaining as following references and forward chaining as finding later citing papers. Mapping helped organize dataset quality, detection cost and testing on new traffic. I treated lightweight detection outside the original environment as a possible gap requiring further evidence.',
'I practised IEEE numbered references and APA author-year references. I paraphrased using a new structure and retained citation. Exact borrowed wording needs quotation marks. I identified copying without credit as plagiarism, invented results as fabrication, and changing 82% to 94% as falsification. A similarity score requires inspection of the matches.',
'For the public-dataset proposal, I checked permitted use and privacy risks without claiming participant recruitment. I proposed restricted access and exclusion of identifiers. A coded ID linked through a separate key is pseudonymization, not full anonymity. For healthcare monitoring, I considered consent, withdrawal, false alerts, missed events and unequal performance. I linked authorship to substantial contributions and responsibility, with ethics review where needed.'
]),
('3. My learning and takeaways', 'I learned that a review should connect evidence and support its claimed gap. Responsible research also requires honest results, accurate attribution, fair credit and protection of people. Paraphrased ideas still need citation, and public data can create privacy risks. I should collect only necessary information and report limitations openly.'),
]),
('Mid-semester: Concepts and application', [
('1. What was asked or tested', 'The mid-semester tested research concepts, experimental designs, hypotheses, reasoning, survey methods, statistical interpretation and academic integrity. I followed question numbers and subparts, using brief points for fewer marks and explanations with examples for longer answers.'),
('2. How I answered and explained it', [
'For Q1-Q5, I connected problem definition, literature review, objectives, design, collection, analysis and reporting. A clear problem guides scope and evidence. I explained plagiarism prevention through independent writing, quotation and citation, and connected reliable fact-finding with critical evaluation. A review compares earlier studies and identifies a supported gap.',
'For Q6, I described before-and-after designs with and without controls, after-only comparisons, completely randomized designs, blocks, Latin squares and factorial designs. Controls help separate treatment from other causes; randomization reduces allocation bias. Blocks group similar units, Latin squares control two sources of variation, and factorial designs examine combined factors.',
'For Q7-Q8, I described a hypothesis as a testable prediction, such as fewer features lowering prediction time. I distinguished deduction from induction. Basic or fundamental research develops knowledge; applied research addresses practical needs; industrial research serves organizational goals and may also be applied.',
'For Q9, I checked the vaccine table: vaccinated goats had 15 survivors and 2 deaths; unvaccinated goats had 4 survivors and 10 deaths. Total deaths were 12, not the printed 21. I tested independence between vaccination and survival. Expected counts came from row total times column total divided by 31. Chi-square was 11.52, above the 5% critical value of 3.84 with one degree of freedom, so I rejected independence. The association favored vaccination; wider causal claims depend on study design.',
'For Q10, I distinguished experience surveys, which gather informed views, from pilot surveys, which test questions and procedures. I explained how rephrasing makes a problem focused and measurable. For Q11 and the OR discussions, I explained proper paraphrasing, AI source checks, database searches and citation chaining. Eighteen percent similarity is not automatically a verdict. Mosaic plagiarism combines borrowed fragments, and tools can miss misconduct or flag legitimate quotations.'
]),
('3. My learning and takeaways', 'I learned to explain why a method fits, check arithmetic and assumptions, and separate association from causation. Not rejecting a null hypothesis does not prove it true. Across the assignments, my main habits were clear questions, suitable evidence, fair comparisons, careful interpretation, honest reporting and proper credit.'),
]),
]

def main():
    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setTitle('Research Methodology - Four-Page Student Summary')
    c.setAuthor('Veer Vikram Singh')
    w,h = A4
    body = ParagraphStyle('body', fontName='Helvetica', fontSize=11.5, leading=16.1, textColor=HexColor('#202a31'))
    counts=[]
    for number,(title,blocks) in enumerate(PAGES,1):
        assert tuple(heading for heading,_ in blocks)==HEADINGS
        c.setFillColor(HexColor('#202a31')); c.setFont('Helvetica',9)
        c.drawString(48,h-33,'RESEARCH METHODOLOGY - ASSIGNMENT SUMMARY')
        c.setStrokeColor(HexColor('#b8c4c8'));c.line(48,h-43,w-48,h-43)
        c.setFont('Helvetica-Bold',17);c.drawString(48,h-76,title)
        y=h-106
        for heading,text in blocks:
            c.setFillColor(HexColor('#202a31'));c.setFont('Helvetica-Bold',12)
            c.drawString(48,y,heading);y-=10
            for part in ([text] if isinstance(text,str) else text):
                p=Paragraph(escape(part),body);_,ph=p.wrap(w-96,h)
                p.drawOn(c,48,y-ph);y-=ph+7
            y-=12
        assert y>=64,(number,y)
        c.setStrokeColor(HexColor('#b8c4c8'));c.line(48,47,w-48,47)
        c.setFillColor(HexColor('#202a31'));c.setFont('Helvetica',8.5)
        c.drawString(48,31,'Veer Vikram Singh  |  SAP ID: 590014281  |  Batch: CCVT- 2')
        c.drawRightString(w-48,31,f'{number} / 4');c.showPage()
        counts.append(len(' '.join(t if isinstance(t,str) else ' '.join(t) for _,t in blocks).split()))
    c.save()
    assert len(PdfReader(OUT).pages)==4
    print('Four pages created. Words per module:',counts)

if __name__=='__main__':main()

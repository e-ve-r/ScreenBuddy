import io, os, json, re, math
from xml.sax.saxutils import escape
import pdfplumber
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.pagesizes import A4
from PIL import Image
from layout_tools import fit_rule, on_rule, LEADING, CHANGES

ROOT='/Users/ever/Documents/ChatGPT/Vision'
SRC='/Users/ever/Downloads/Final_Assignment.pdf'
TMP=ROOT+'/tmp/pdfs'
OUT=ROOT+'/output/pdf'
os.makedirs(OUT,exist_ok=True)
G=json.load(open(TMP+'/geometry.json'))
original=pdfplumber.open(SRC)
BLUE=HexColor('#15476b'); INK=HexColor('#172b40'); TEAL=HexColor('#007e87')
ops={}; warnings=[]; audit=[]

def put(n,x,y,w,h,text,size=9,whiteout=False,bold=False):
    ops.setdefault(n,[]).append((x,y,w,h,text,size,whiteout,bold))
def line(n,match,occ=0):
    exact=[l for l in G[str(n)] if l['t']==match]
    hits=exact or [l for l in G[str(n)] if match in l['t']]
    if len(hits)<=occ: raise ValueError((n,match,occ))
    return hits[occ]
def after(n,match,text,h=28,size=9,x=None,w=None,occ=0,dy=9):
    l=line(n,match,occ);xx=x if x is not None else 60
    fitted=fit_rule(original,n,l,text,size,xx,h,'after')
    if fitted:
        ops.setdefault(n,[]).append(fitted);return
    put(n,xx,l['b']+dy,w or (540-xx),h,text,size)
def inline(n,match,text,x=None,w=None,size=9,occ=0):
    l=line(n,match,occ);xx=x if x is not None else l['r']+8
    fitted=fit_rule(original,n,l,text,size,xx,14,'inline')
    if fitted:
        ops.setdefault(n,[]).append(fitted);return
    put(n,xx,l['y']-3,w or (540-xx),14,text,size)
def rows(n,labels,values,x=200,size=9,w=None):
    for label,value in zip(labels,values): inline(n,label,value,x=x,w=w,size=size)
def numbered(n,start,end,answers,x=64,size=9):
    # Fill lines containing only list numbers inside a specified region.
    ls=[l for l in G[str(n)] if start<=l['y']<=end and re.fullmatch(r'\d+\.',l['t'])]
    assert len(ls)==len(answers),(n,len(ls),len(answers))
    for l,a in zip(ls,answers): put(n,x,l['y']+1,540-x,24,a,size)
def table(n,y,values,skip=1,cols=None,size=9,after_label=False):
    ts=[t for t in original.pages[n-1].find_tables() if t.bbox[1]-2<=y<=t.bbox[3]+2 and t.bbox[2]-t.bbox[0]>350]
    assert ts,(n,y)
    t=min(ts,key=lambda t:abs(t.bbox[1]-y))
    rr=t.rows[skip:]
    assert len(rr)==len(values),(n,len(rr),len(values))
    for row,vv in zip(rr,values):
        if isinstance(vv,str): vv=[vv]
        cc=cols or list(range(len(row.cells)-len(vv),len(row.cells)))
        for col,text in zip(cc,vv):
            x0,y0,x1,y1=row.cells[col]
            yy=y0+(1.5 if y1-y0<18 else 3)
            if after_label:
                ll=[l for l in G[str(n)] if y0-2<=l['y']<y1 and l['x']>=x0 and l['x']<x1 and l['r']<x1+2]
                if ll: yy=max(l['b'] for l in ll)+2
            if n==14 and 'synthetic four-way' in text:
                x0+=27
            put(n,x0+5,yy,x1-x0-10,y1-yy-2,text,size)
def check(n,x,y,size=7): put(n,x,y,10,12,'__TICK__',size,bold=True)

NAME='Veer Vikram Singh'; SAP='590014281'; BATCH='CCVT- 2'; DATE='30/09/2026'
# Cover details.
put(1,89,276,260,14,NAME,10);put(1,439,276,105,14,SAP,10)
put(1,97,296,240,14,BATCH,10);put(1,446,296,100,14,DATE,10)
put(21,84,206,210,14,NAME,10);put(21,355,206,180,14,SAP,10)
put(21,91,233,200,14,BATCH,10);put(21,334,233,170,14,DATE,10)
for label,val in [('Name:',NAME),('Roll No.:',SAP),('Section:',BATCH),('Date:',DATE)]: inline(50,label,val,x=316,w=215,size=11)
put(92,116,86,190,14,NAME,9);put(92,377,86,150,14,SAP,9)
put(92,128,111,160,14,BATCH,9);put(92,359,111,170,14,DATE,9)
# Original exam identity fields.
inline(90,'Name:',NAME,x=110,w=310,size=10)
inline(90,'Enrolment No:',SAP,x=150,w=300,size=10)

# WORKSHEET I
for ch in original.pages[0].chars:
    if ch['text']=='□': check(1,ch['x0'],ch['top']+2)
# A sensible hypothesis-testing sequence (hypothesis is developed before final analysis).
for x0,x1,a in [(55.931,169.284,'4'),(169.284,288.486,'1'),(288.486,421.415,'3'),(421.415,539.224,'2')]:
    put(2,(x0+x1)/2-3,252,12,11,a,9)
after(2,'Why is this order useful','It gives a clear question, a testable prediction, evidence to test it, and a conclusion linked to the problem.',h=45)
table(2,381,[
 'Develop a faster shortest-path algorithm.',
 'Automated tests reduce software defects.',
 'Compare methods and learn to test claims.',
 'Use traffic data to guide signal timings.',
 'Test whether a smaller intrusion detector runs faster.'
],skip=0)
table(2,548,[
 'Compare two intrusion detectors using measured F1 and latency.',
 'Check how traffic load affects network delay.',
 'Test whether binary-search time grows logarithmically.'
])
after(2,'problem? Explain what is missing.','No. A trend is only a topic. It needs a specific problem, a research question, a gap, a feasible scope and measurable evidence.',h=28,x=62,w=470,size=8.8)
for anchor,answer in [('1. Investigating','E'),('2. Measuring','EM'),('3. Developing','T'),('4. Summarizing','D'),('5. Comparing','A')]: inline(3,anchor,answer,x=470,w=65)
table(3,459,[['Theoretical','Uses a logical proof rather than observations.'],['Empirical','Tests predictions against measured dataset results.'],['Theoretical','Describes protocol behavior using formal rules.'],['Empirical','Collects interview evidence; also exploratory.']],size=8.8)
inline(4,'Pick a CS domain:','Network security',x=150)
numbered(4,340,490,['Recent intrusion-detection papers and their limitations.','Security teams reporting too many false alerts.','Public network datasets such as UNSW-NB15.','A networking project that reveals slow detection.'])
inline(4,'Topic/domain:','Lightweight network intrusion detection',x=129)
after(4,'1. Explore broadly:','Network security and machine-learning-based intrusion detection.',h=29)
after(4,'2. Narrow through reading:','The trade-off between false alerts and inference time on a laptop.',h=29)
after(4,'3. Formulate question(s):','Does reducing random-forest features lower latency without a large fall in F1?',h=28)
after(4,'4. Validate:','Check dataset access, laptop memory, time, and whether prior work already answers this.',h=18,size=8.5)
for anchor,a in [('1. “Artificial','Topic'),('2. “AI','Weak problem'),('3. “How','Research problem'),('4. “Cyber','Topic')]: inline(5,anchor,a,x=438,w=94,size=8.4)
inline(5,'5. Your own statement:','Can fewer RF features reduce IDS latency? (Research problem)',x=187,w=345,size=8.2)
table(5,265,['Compare full-feature and reduced-feature random forests on UNSW-NB15.','Measure F1, false-positive rate and inference time.','Use public CSV files, Python and one laptop within eight weeks.','Fast detection with fewer false alerts can help network monitoring.','Test a defined feature-cost trade-off; confirm novelty through reading.','Labeled flows and repeated timings allow a fair comparison.'])
for o,(err,better) in enumerate([
 ('Vague and too broad.','Compare two models for detecting spam in one public email dataset.'),
 ('Unmanageable scope.','Compare false-alert rates of two IDS models on UNSW-NB15 in eight weeks.'),
 ('Unrealistic accuracy and time.','Evaluate two classifiers on a public diabetes dataset within eight weeks.')]):
 inline(6,'Error:',err,x=106,occ=o)
 after(6,'Improved version:',better,h=24,x=66,occ=o,size=8.8)
table(7,47,['Eight weeks.','Offline laptop experiment; no live production network.','Official UNSW-NB15 training and test CSV files.','Python, scikit-learn, random forest and decision tree.','Live attacks, packet payloads and claims about all networks.'],skip=0)
after(7,'then convert it into a narrower study.','1. It covers many services, such as traffic, water and waste.\n2. It gives no location, dataset or target users.\n3. It gives no metric or time limit.\nNarrower study: compare adaptive and fixed signals at one simulated junction over six weeks.',h=125)
inline(8,'Research topic/problem:','Reducing IDS inference cost',x=178)
put(8,135,386,405,13,'Compare a full-feature RF with a 15-feature RF.',9)
put(8,135,426,405,13,'F1, false-positive rate and mean inference time per flow.',9)
put(8,135,465,405,13,'Public CSV data and one laptop are sufficient.',9)
put(8,135,505,405,13,'Directly tests the speed versus detection-quality trade-off.',9)
put(8,135,544,405,13,'Complete within eight weeks.',9)
after(8,'Final SMART objective:','Within eight weeks, compare full-feature and 15-feature random forests on the official UNSW-NB15 split; report F1, false-positive rate and mean latency over five timing runs.',h=43,size=9)
for m in ['1. Can I','2. Can I','3. Is the','4. Does it','5. Is a']: inline(8,m,'Yes (self-check)',x=422,w=108,size=8)
after(8,'Partner’s one improvement suggestion:','Suggested self-review: name the fixed split and include latency.',h=15,x=62,size=8.2)
table(9,318,[['Primary','Qualitative'],['Primary','Quantitative'],['Secondary','Depends on its contents'],['Primary','Quantitative'],['Primary if collected here','Qualitative'],['Secondary','May contain both']],size=8.6)
for m,a in [('1. What data','Labeled network flows, prediction outputs and timing logs.'),('2. Why is','They show detection errors and the cost of making predictions.'),('3. Primary','Both: existing flows plus timings measured in my experiment.'),('4. Qualitative','Mainly quantitative: feature values, class labels and metrics.')]: after(9,m,a,h=19)
table(10,275,[['Google Forms','Collect the same satisfaction ratings from all students.'],['Wireshark','Capture and inspect packet timing and protocols.'],['PerfMon','Measure processor and memory use.'],['Observation log','Record task completion, errors and user actions.'],['BeautifulSoup','Extract permitted public page data consistently.']],size=8.5)
# experiment-log checkbox
check(10,290.4,495)
inline(10,'Research problem:','Does reducing RF features improve IDS speed?',x=148)
table(10,535,['F1, false-positive rate, mean prediction time and peak memory.','RF predictions on the fixed UNSW-NB15 test set.','After training; five timing runs for each model.','Python experiment log and time.perf_counter.','Same split, laptop, seed, timing method and background workload.'],skip=0,size=8.9)
after(11,'1. Which model','Model B: 95% accuracy.',h=16)
after(11,'2. Which model','Model A: 20 ms.',h=16)
after(11,'Why?','Model C: it exceeds 93% accuracy and is faster than B (25 ms versus 70 ms).',h=19)
after(11,'4. Is “B','No. Best depends on the goal; higher accuracy may be outweighed by slow response.',h=19)
inline(11,'1. “Model','Description',x=395,w=130)
after(11,'real-time deployment.”','Interpretation',h=12,x=390,size=8.3,dy=0)
inline(11,'3. “The system','Description',x=395,w=130)
inline(11,'4. “The observed','Interpretation',x=454,w=85,size=8)
after(11,'you would ask before claiming','Was the result caused by the model, or by a different split, workload or hardware?',h=19,x=62,size=8.5)
table(12,277,[['Laptop hardware','Execution time and memory use.'],['Python / scikit-learn','Model predictions and class probabilities.'],['Fixed test set + timer','Comparable F1, false alerts and latency.'],['CSV logging script','Settings, seeds and results from every run.']],size=8.6)
after(12,'Why should a sensor','Calibration checks measurements against a known reference and reduces systematic error.',h=19)
after(12,'What could happen','The result may be unreliable; others cannot verify whether the effect is real.',h=30)
for yy,a in [(143.1,'Network security.'),(190.1,'Large intrusion detectors can be slow and generate false alerts.'),
 (237.0,'Compare full-feature and reduced-feature RF detection on UNSW-NB15.'),
 (284.0,'Can 15 features lower latency while keeping F1 within 0.02 of the full model?'),
 (330.9,'It tests whether a simpler model is practical on limited hardware.')]:
    ops.setdefault(13,[]).append(on_rule(13,61.7,yy,533.6,a,8.5))
for x,y in [(228.3,368),(387.4,368),(62,381)]: check(13,x,y)
for x0,yy,x1,a,s in [(94,418.5,212,'Eight weeks',8.3),(328,418.5,479,'UNSW-NB15 official split',8.3),
 (183.3,432,409.9,'Python / scikit-learn',8.1),(61.7,445.6,179.7,'Live deployment',8.1)]:
    ops.setdefault(13,[]).append(on_rule(13,x0,yy,x1,a,s))
inline(13,'O1:','By week 2, clean the training data and fix a leakage-free pipeline.',x=86,size=8.8)
inline(13,'O2:','By week 6, train both RF variants using training data only.',x=86,size=8.8)
inline(13,'O3:','By week 8, report F1, false-alert rate and five-run mean latency.',x=86,size=8.8)
for x0,yy,x1,a in [(130.4,573.6,295.5,'Quantitative; both sources'),(362.3,573.6,527.5,'UNSW data + own timings'),
 (226.1,587.2,414.8,'Python CSV logger'),(61.7,600.7,203.3,'Laptop + timer')]:
    ops.setdefault(13,[]).append(on_rule(13,x0,yy,x1,a,8.1))
after(13,'What will you measure/analyze?','Compare F1 loss, false alerts and timing. The reduced model is useful if it is faster and its F1 loss is no more than 0.02.',h=24,x=63,size=8.5)
check(14,196.2,215)
after(14,'Specific pain-point:','Fixed signals waste time when traffic is uneven.',h=22)
after(14,'Refined research problem:','Does queue-based adaptive timing reduce mean vehicle waiting time at one simulated junction?',h=30)
inline(14,'Dominant approach:','Empirical and applied',x=155)
after(14,'Why is it theoretical','Simulation produces measured waiting times for adaptive and fixed signals.',h=24)
numbered(14,440,540,['By week 2, build one four-way junction in SUMO.','By week 4, implement fixed and queue-based signal control.','By week 6, compare mean waits over five seeds at three traffic loads.'])
table(14,575,['Six weeks.','One junction; low, medium and high simulated traffic loads.','A synthetic four-way urban junction.','SUMO and Python.','Whole-city traffic, emergency routing and live road testing.'],skip=0)
numbered(15,135,238,['"Better" is not defined by any measurable metric.','It covers too many query types and languages.','The required training data and computing budget are unclear.','There is no stated gap, baseline test or time limit.'],x=81,size=8.5)
after(15,'Rewrite it as','Compare retrieval-based and FAQ-only chatbots on 100 campus-admission questions using answer accuracy and latency in six weeks.',h=24,x=63,w=467,size=8.5)
for m,a in [
 ('1. One possible','Can moisture-based control reduce water use without drying the soil too much?'),
 ('2. Two data','Soil-moisture readings and historical weather records.'),
 ('3. One primary','Readings collected from the experiment’s soil-moisture sensor.'),
 ('4. One secondary','Existing weather-station rainfall records.'),('5. One data-collection','A timestamped sensor logging program.'),
 ('6. One research','A calibrated soil-moisture sensor.'),('7. One measurable','Compare daily water use and soil moisture over four weeks.'),
 ('8. One scope','One crop type in two small test plots.')]: after(15,m,a,h=14,size=8.1,x=82,w=445,dy=1)
numbered(15,640,730,['Was the test set independent, with no training-data leakage?','How balanced are the classes, and what are precision and recall?','Does performance hold on new data and against a simple baseline?'],x=81,size=8.4)
# Tick the selected alternatives directly beside their printed options.
for j,letter in enumerate(['b','a','b','b','a','a','a','d','a']):
    qs=[l for l in G['16'] if re.match(r'\d+\.',l['t'])]
    y0=qs[j]['y']; y1=qs[j+1]['y'] if j+1<len(qs) else 790
    opt=[l for l in G['16'] if y0<l['y']<y1 and f'({letter})' in l['t']][0]
    words=[z for z in original.pages[15].extract_words() if abs(z['top']-opt['y'])<2 and z['text']==f'({letter})']
    assert len(words)==1,(j,letter,words)
    check(16,words[0]['x0']-11,words[0]['top']+1)
check(17,53.5,48)
for m,a in [
 ('1. Define','A planned investigation that answers a question using evidence.'),
 ('2. One difference','A topic is broad; a research problem is a specific question to investigate.'),
 ('3. One source','A gap found while reading research papers.'),('4. One common','Choosing a problem that is too broad.'),
 ('5. Expand','Specific, Measurable, Achievable, Relevant, Time-bound.'),
 ('6. One primary','CPU-use logs collected in my own experiment.'),('7. One secondary','The published UNSW-NB15 network dataset.'),
 ('8. One data','A questionnaire in Google Forms.'),('9. One research','A calibrated soil-moisture sensor.'),
 ('10. Difference','Analysis finds patterns; interpretation explains their meaning for the question.')]: after(17,m,a,h=20)
after(18,'Answers:','1-C, 2-A, 3-D, 4-B, 5-E, 6-F, 7-G, 8-H.',h=14,dy=1)
after(18,'Problem: Gap: Objective: Evidence/data:','Problem: intrusion models may be slow on a laptop.\nGap to verify: the detection-quality cost of using only 15 features.\nObjective: compare full and reduced RF models within eight weeks.\nEvidence: fixed-test F1, false-positive rate, memory and five-run timings.\nI will limit conclusions to the dataset and hardware tested.',h=150,size=9.5)
# Self-assessment is personal, so use a candid provisional rating rather than invented confidence.
table(19,136,[[ 'X' ] for _ in range(16)],cols=[2],size=8)
put(19,60,374,460,12,'Provisional self-check: 2 = partly; revise these ratings after practicing.',8)
after(19,'The most important idea','A clear problem connects scope, objectives, evidence and conclusions.',h=20)
after(19,'The concept I still','How to choose and interpret performance metrics fairly.',h=17)
after(19,'One research problem','Can a 15-feature RF reduce IDS latency with an F1 loss no greater than 0.02?',h=20)
put(19,296,568,84,12,'What can I build?',8)
put(19,62,583,83,12,'What is missing?',8)
after(19,'Explain your answer','Research should first identify a real gap. Building a tool is useful only when it helps answer a clear question.',h=25,x=62,size=8.7)

# WORKSHEET II
for l in G['22']:
    if '□' in l['t'] and '1–5' in l['t']:
        put(22,535,l['y']+2,15,11,'3',8)
for ch in original.pages[21].chars:
    if ch['text']=='□':check(22,ch['x0'],ch['top']+2)
put(22,60,322,470,12,'Provisional confidence: 3/5; adjust after personal revision.',8)
for m,a in [('1. General','Deduction.'),('2. Specific','Induction.'),('3. Reasoning','Abduction.'),('4. A claim','Supported by valid reasoning, evidence and checks of alternatives.')]: after(22,m,a,h=24)
after(23,'1. What is','Every greedy choice is claimed to lead to a globally optimal solution.',h=26)
after(23,'2. Give a','Coins {1,3,4}, amount 6: greedy uses 4+1+1; optimal uses 3+3.',h=40)
after(23,'3. Write a','Greedy algorithms are optimal for problems with a suitable greedy-choice property and optimal substructure.',h=40)
after(23,'4. What evidence','A correctness proof under stated assumptions, plus tests that check the implementation.',h=27)
rows(24,['Initial idea','Possible claim','Counter-argument','Evidence required','Refined research problem'],[
 'IoT security using a lightweight intrusion detector.',
 'Fewer RF features can reduce inference time.',
 'Important attack patterns may be lost when features are removed.',
 'F1, false-positive rate and timings on a fixed test split.',
 'Do 15 RF features lower latency with an F1 loss of at most 0.02?'
],x=182,size=8.6)
after(25,'General rule:','Every connected undirected graph has a spanning tree.',h=33)
after(25,'Specific case:','Graph G is connected and undirected.',h=33)
after(25,'Conclusion:','Therefore, G has a spanning tree.',h=31)
after(26,'1. What are','The new model beats the baseline on eight tested datasets.',h=32)
after(26,'2. What general','It may perform better on similar datasets.',h=32)
after(26,'3. Why is','Eight datasets cannot represent all future data; selection bias may affect the pattern.',h=33)
numbered(26,470,540,['The database has slow queries or missing indexes.','The server is overloaded by a traffic spike.','A network link has become slow.'],x=80)
after(26,'Which explanation','Check slow database queries first, using query logs and timing; investigate the others if needed.',h=34)
for m,a in [('1. Running','D'),('2. Benchmarking','E'),('3. Proving algorithm','M'),('4. Testing','E'),('5. Proving a','M')]: inline(27,m,a,x=505,w=30)
rows(27,['A sorting algorithm','A new ML','A robot prototype','A cryptographic'],['M','E','D','M'],x=288,w=68,size=8)
rows(27,['A sorting algorithm','A new ML','A robot prototype','A cryptographic'],['Prove order and permutation properties.','Compare metrics on unseen test data.','Show path following in a prototype.','Prove security under stated assumptions.'],x=362,w=180,size=8.2)
for m,a in [('1. Test case 1:','Ask a clear delivery-status question with a valid order number.'),('2. Test case 2:','Ask for a refund under a known policy.'),('3. Test case 3:','Use a misspelled product question.'),('4. Onecorner','A mixed-language or ambiguous request with no order number.')]: after(28,m,a,h=31)
rows(29,['Demonstration proves that','Demonstration cannot prove that','A better next step'],['The prototype works for the shown cases.','It works for every possible case.','Test varied unseen inputs against clear metrics.'],x=243,size=8.8)
rows(30,['Independent variable','Dependent variable','Baseline','Dataset / workload','Metric','Number of trials','Possible limitation'],[
 'Protocol version: existing versus proposed.',
 'Packet delivery delay.',
 'Existing protocol under identical settings.',
 'Same topology, packet sizes and three traffic loads.',
 'Mean and 95th-percentile latency in milliseconds.',
 'Ten runs per load and protocol, with controlled seeds.',
 'Simulation results may differ from real network conditions.'
],x=185,w=351,size=8.7)
after(32,'Statement to prove:','The sum of two even integers is even.',h=42)
after(32,'Given / assumptions:','Let a = 2m and b = 2n, where m and n are integers.',h=42)
after(32,'Logical steps:','a + b = 2m + 2n = 2(m + n). Since m + n is an integer, the sum is divisible by 2.',h=55)
after(32,'Conclusion:','Therefore, a + b is even.',h=32)
after(33,'Claim:','There is no largest integer.',h=37)
after(33,'Opposite assumption:','Assume L is the largest integer.',h=37)
after(33,'Contradiction:','L + 1 is an integer greater than L, contradicting the assumption.',h=36)
after(33,'Conclusion:','Hence no largest integer exists.',h=34)
# Complete the printed induction without crowding its supplied working.
put(34,317,74,30,13,'k + 2',9)
after(34,'Conclusion:','The formula holds for n = 1. If it holds for k, it holds for k + 1; therefore it holds for all positive integers n.',h=37)
after(35,'Original statement:','If an algorithm terminates, then it produces an output.',h=41)
after(35,'Contrapositive:','If an algorithm does not produce an output, then it does not terminate.',h=42)
after(35,'Explain why','Both have the same truth value: each fails only when termination occurs without an output. This is a logical equivalence of the stated claim, not a rule for every actual program.',h=54)
for m,a in [('1. Assume','Contradiction'),('2. Prove the','Induction'),('3. Prove ¬Q','Contrapositive'),('4. Start','Direct')]: inline(35,m,a,x=458,w=81,size=8.5)
rows(35,['Algorithm correctness','Complexity analysis','Cryptography','Automata / formal'],['Prove a loop invariant by induction.','Directly bound operation counts.','Use a reduction under a security assumption.','Prove language properties by contradiction.'],x=205,w=334,size=8.2)
for m,a in [('1. A theorem','D'),('2. A researcher','I'),('3. A program','A'),('4. A formal','D')]: inline(36,m,a,x=503,w=35)
after(36,'Choose any one','Item 2 is inductive: a repeated pattern is used to propose a general rule, but untested cases may differ.',h=41)
rows(37,['Recognize a formal','Represent a network','Study computability','Represent Boolean','Reason about logical'],['Finite automaton (regular languages).','Graph.','Turing machine.','Boolean algebra.','Propositional / predicate logic.'],x=215,size=8.8)
after(37,'1. Why can','It removes unneeded details so we can reason clearly about behavior and limits.',h=36)
after(37,'2. What is','Whether a problem can be solved by an algorithm that finishes for every valid input.',h=36)
after(37,'3. Give one','Can a finite automaton recognize the proposed pattern language?',h=36)
rows(39,['Problem','Input','Output','Algorithm idea','Time complexity','Space complexity','Correctness argument','Test cases'],[
 'Find an item in a sorted array.', 'A sorted array of n items and target x.', 'The target index, or -1 if absent.',
 'Binary search: compare the middle and halve the search range.', 'O(log n).', 'O(1) for an iterative version.',
 'If x exists, it remains in the search interval after each step.', 'Empty array; first/last item; duplicates; missing target.'
],x=180,w=357,size=8.7)
after(39,'Why should a researcher','Complexity shows growth as input increases. Runtime also reflects hardware, constants and implementation, so both are needed for a useful comparison.',h=44)
rows(40,['Requirements','System design','Implementation','Testing','Future enhancement'],[
 'Train and compare intrusion classifiers; record timing and errors.',
 'Separate preprocessing, training, evaluation and logging modules.',
 'Python and scikit-learn with saved configuration files.',
 'Check leakage, missing values, metric calculations and repeat runs.',
 'Evaluate another dataset and a streaming prototype.'
],x=169,w=368,size=8.7)
rows(40,['Version control','Documentation','Reproducibility'],['Track changes and recover a previous experiment.','Explain settings, inputs and how to run the study.','Let others repeat the same steps and compare results.'],x=153,w=384,size=8.6)
inline(40,'Testing','Find errors that could distort conclusions.',x=153,w=384,size=8.6,occ=1)
after(40,'oped systematically?','Faulty research software can create misleading evidence. A clear process makes results easier to check and reproduce.',h=42)
rows(41,['System','Research question','Assumption 1','Assumption 2','Variable 1','Variable 2','Variable 3','Relationship / equation','How will you validate'],[
 'A network server queue (M/M/1 model).','How does arrival rate affect mean response time?',
 'Poisson arrivals and exponential service times.','One server; stable operation with lambda < mu.',
 'lambda: arrival rate in packets/s.','mu: service rate in packets/s.','W: mean time in system in seconds.',
 'W = 1 / (mu - lambda), for lambda < mu.', 'Compare predicted mean times with repeated simulations.'
],x=179,w=358,size=8.7)
after(41,'1. What does','lambda is the average number of packets arriving per second.',h=34)
after(41,'2. What does','mu is the average number of packets the server can process per second.',h=34)
after(41,'3. What would','The queue grows; delays rise. With a finite buffer, packets are dropped because service cannot keep up.',h=47)
rows(42,['Research claim','Metric 1','Metric 2','Dataset / workload','Baseline','Environment','Number of experiments','Possible limitation'],[
 'Reducing RF features may lower latency with little F1 loss.', 'F1-score.', 'Mean prediction time per flow.',
 'Official UNSW-NB15 training/test split.', 'Full-feature RF; decision tree as a simple reference.',
 'Same laptop, software versions and workload.', 'Five timing runs per trained variant; fixed model seed.',
 'One dataset and one machine do not prove general performance.'
],x=182,w=355,size=8.7)
after(42,'1. Which model','A: 94%.',h=10,dy=1,size=8.2)
after(42,'2. Which model','B: 95%.',h=10,dy=1,size=8.2)
after(42,'3. Which model','B: reported F1 is 90%.',h=10,dy=1,size=8.2)
after(42,'4. Can you','No. The choice depends on the goal: A has higher accuracy and recall, while B has higher precision and F1. Also compare latency, costs and performance on new data.',h=43,size=8.6)
for m,a in [('1. Measure','A profiler such as Valgrind/Massif for memory, plus CPU profiling.'),('2. Simulate','NS-3 or OMNeT++.'),('3. Compare','SPEC CPU for standardized CPU workloads; MLPerf for ML workloads.'),('4. Monitor','Prometheus collects metrics; Grafana displays them.')]: after(43,m,a,h=34,size=8.8)
after(43,'Experiment title:','Full-feature versus 15-feature RF on UNSW-NB15.',h=27)
after(43,'Hypothesis:','Fewer features lower latency while keeping F1 within 0.02 of the full model.',h=27)
after(44,'Metric(s):','F1, false-positive rate, peak memory and mean prediction time per flow.',h=45)
after(44,'Observed result:','Not yet measured. This is a proposed experiment; no result is claimed.',h=45)
after(44,'Interpretation:','Support the hypothesis only if measured latency falls and F1 loss stays at or below 0.02.',h=45)
after(44,'Limitation:','One dataset and laptop; traffic changes may alter future performance.',h=44)
after(45,'Original claim:','AI irrigation reduces water use while maintaining crop health.',h=38)
after(45,'Counter-argument 1:','Water savings may come from rainfall rather than the controller.',h=36)
after(45,'Counter-argument 2:','A faulty moisture sensor could under-water the plants.',h=36)
after(45,'Refined claim:','For matched test plots over four weeks, adaptive control may use less water than a fixed schedule while keeping soil moisture in a safe range.',h=42,size=8.8)
rows(45,['Using observations','Applying a known','Finding the most'],['Induction','Deduction','Abduction'],x=317,size=8.7)
after(45,'Explain your choice:','Demonstration checks the prototype. Empirical trials compare water use and plant condition. A mathematical model can check control assumptions but cannot prove real crop-health effects.',h=44,size=8.8)
put(45,60,675,470,14,'Selected: Demonstration + Empirical; mathematical model for supporting checks.',8.1)
after(47,'What algorithm','Threshold control: start watering below a low moisture limit and stop above a higher limit.',h=34)
after(47,'What would be its input','Current soil moisture and the low/high moisture thresholds.',h=32)
after(47,'What would be its output','Pump ON or OFF.',h=32)
put(47,136,342,86,13,'Moisture (%)',8.2);put(47,269,342,85,13,'Rainfall (mm)',8.2);put(47,400,342,86,13,'Water used (L)',8.2)
after(47,'Write one assumption:','The sensor is calibrated and both plots receive comparable rainfall.',h=37)
after(47,'Write a simple','Daily water W = pump flow rate q multiplied by total ON time t.',h=37)
rows(47,['Metric 1','Metric 2','Baseline','Experiment condition','Expected result'],['Litres of water used each day.','Soil moisture and plant-health score.','A fixed watering schedule.','Matched plots, crop, soil, rainfall and four-week duration.','Lower water use with similar health; a prediction, not an observed result.'],x=178,w=359,size=8.5)
rows(48,['Research Title','Research problem','Research question','Claim / hypothesis','Counter-argument','Reasoning model','Validation / proof method','Theoretical model','Algorithmic approach','Mathematical model','Performance metric','Baseline','Expected contribution'],[
 'A smaller random forest for offline intrusion detection.',
 'Detection may be too costly on limited hardware.',
 'Can 15 features reduce latency with F1 loss <= 0.02?',
 'The reduced model is faster with only a small F1 loss.',
 'Removed features may be important for rare attacks.',
 'Induction from measured test results.',
 'Empirical comparison on a fixed, unseen test set.',
 'A classifier mapping a feature vector to a class.',
 'Rank features on training data; fit full and reduced RF models.',
 'Mean latency = total prediction time / test-flow count.',
 'F1, false-positive rate and latency.',
 'Full-feature RF, plus a simple decision tree.',
 'A reproducible comparison of detection quality and cost.'
],x=209,w=331,size=8.3)

# WORKSHEET III
for l in G['51']:
    if '□' in l['t']:
        check(51,456,l['y']+3)
        put(51,519,l['y']+3,25,12,'3/5',8)
put(51,60,679,475,12,'Provisional confidence scores; adjust after your own revision.',8)
# Answer the warm-up explicitly, then fill its own topic lines.
put(52,60,223,474,52,'1. Search academic libraries and follow paper references.  2. Start with IEEE Xplore and ACM DL.  3. Check venue, methods, evidence, limitations and publication status.',8.2)
inline(52,'My research topic:','ML-based intrusion detection',x=178,w=360,size=8.1)
inline(52,'Where I would search first:','IEEE Xplore and ACM DL',x=215,w=320,size=8.1)
inline(52,'Why?','Relevant scholarly methods and publication details.',x=94,w=437,size=8.1)
after(53,'What should the student','Search existing CNN methods, plant-image datasets, baselines, data leakage, field performance and open limitations before claiming a new contribution.',h=38)
after(54,'What changed between','The second search found scholarly evidence, methods and limitations rather than broad claims. It helped identify a focused research question.',h=35)
rows(55,['Research Question:','Database:','Keywords:','Search String:','How will I screen'],[
 'Can lightweight ML detect network attacks with low latency?',
 'IEEE Xplore; ACM DL; publisher repositories.',
 'intrusion detection; machine learning; latency; feature selection.',
 '"intrusion detection" AND "machine learning" AND (latency OR lightweight)',
 'Check relevance, dataset, venue, methods and limitations.'
],x=224,w=315,size=8.1)
for m,a in [('1. Robotics','IEEE Xplore.'),('2. Algorithms','ACM Digital Library.'),('3. AI and','IEEE Xplore or ACM DL; arXiv for preprints.'),('4. Citation','Scopus or Web of Science.')]: inline(56,m,a,x=232,w=307,size=8.6)
rows(57,['Keyword 1','Keyword 2','Keyword 3','Synonym','Related term'],['drones','precision agriculture','crop monitoring','unmanned aerial vehicle (UAV)','remote sensing'],x=160,size=8.7)
after(58,'Your search string:','("machine learning" OR "deep learning") AND (crop OR plant) AND ("disease detection" OR "disease classification")',h=55,size=9)
# Search record reflects verified sources, not invented database hit counts.
for y,db,q,note in [(417,'UNSW repository','UNSW-NB15 dataset paper','Original dataset and citation verified.'),(442,'arXiv','N-BaIoT autoencoders','Original authors and method verified.'),(467,'Sensors / MDPI','CICIoT2023 benchmark','Paper and dataset scope verified.')]:
 put(59,48,y,63,20,DATE,8)
 put(59,115,y,91,20,db,8)
 put(59,209,y,148,20,q,8)
 put(59,360,y,176,22,note,8)
after(60,'Answer:','1. Look in the selected paper’s reference list (backward chaining).\n2. Use a citation index or Scholar’s cited-by list (forward chaining).',h=33)
after(60,'how could search alerts','They help find new related papers and citations during the project, so the review stays current.',h=32)
rows(61,['Research Problem','Research Question','Method / Algorithm','Dataset / Experimental','Main Result','Performance Metric','Limitation','Future Scope'],[
 'Need a realistic benchmark for intrusion detection.',
 'Can diverse labeled traffic support fair IDS evaluation?',
 'IXIA traffic generation; packet capture; flow-feature extraction.',
 'UNSW-NB15: normal traffic plus nine attack types.',
 'A labeled public dataset and standard train/test partitions.',
 'Baseline classifier detection metrics; no personal result claimed.',
 'One laboratory environment limits deployment generalization.',
 'Test models on newer traffic and independent environments.'
],x=190,w=349,size=8.3)
after(62,'Explain your reasoning.','1. Study B first: it reports 96% accuracy; C has no exact value.\n2. Study A first for lower computational cost.\n3. A is a starting point for real-time testing, but measure latency. Different datasets prevent a fair direct ranking.',h=59,size=8.5)
after(64,'What has been solved?','The examples show that ML methods can classify attacks on the tested benchmark data.',h=40)
after(64,'What remains unsolved?','Reliable detection on modern traffic, fair comparisons and real-time cost are not established.',h=40)
after(64,'Possible research gap:','Compare a lightweight and a larger model on the same recent dataset, measuring F1 and latency.',h=40)
after(66,'My theme groups:','Dataset quality: Tavallaee et al. (2009), duplicate analysis; NSL-KDD.\nModern traffic: Moustafa & Slay (2015), generated flows; UNSW-NB15; Sharafaldin et al. (2018), flow features; CICIDS2017.\nAutoencoder detection: Mirsky et al. (2018), online ensemble; KitNET; Meidan et al. (2018), deep autoencoders; N-BaIoT.',h=95,size=8.6)
rows(67,['Theme 1:','Theme 2:','Theme 3:'],['Cost efficiency: resource allocation and pricing.','Scalability: workload growth and elastic services.','Energy use: server power and efficient scheduling.'],x=112,size=8.6)
after(67,'What research gap','Few studies may jointly compare cost, scaling and energy under the same workload. This is a possible gap to verify, not an established claim.',h=42)
after(69,'Write the reference in IEEE','[1] J. Smith, "AI for Cybersecurity," Journal of Computer Science, vol. 45, no. 3, pp. 120-135, 2021.',h=46)
after(69,'Now write it in APA','Smith, J. (2021). AI for cybersecurity. Journal of Computer Science, 45(3), 120-135.',h=46)
after(70,'Explain.','No. This is citation padding. Cite only the two papers that support the claim and provide your own measured evidence of efficiency.',h=37)
rows(72,['1','2','3','4','5'],[
 'Unethical','Ethical if properly credited and reuse is permitted','Unethical','Ethical if meaning is preserved','Unethical'
],x=108,w=175,size=8,)
rows(72,['1','2','3','4','5'],['Copied words are unacknowledged.','Citation does not replace any required permission.','Code attribution and license terms matter.','Independent wording still credits the source idea.','Old work is presented as new without disclosure.'],x=291,w=248,size=8.2)
after(73,'Write your own version.','Cloud services can handle changing demand more easily, while data protection still needs careful attention [1].',h=35)
inline(73,'Citation marker:','[1] (placeholder for the exercise’s source)',x=153,size=8.4)
after(74,'able?','Citations credit ideas, but copied wording still needs quotation marks. Patchwork retains others’ phrasing and structure; rewrite from understanding and cite the sources.',h=36)
after(76,'Identify the ethical','Falsification: the researcher changes a real result from 82% to 94%. This misleads readers, prevents fair comparison and may lead to harmful decisions.',h=37)
after(78,'Which data is actually','For study-time tracking, keep study duration and an anonymous ID. Use broad age groups or grades only if the research question needs them; avoid names, precise location and device identifiers.',h=42)
after(78,'How would you anonymize','Remove direct identifiers, generalize ages, aggregate results and check re-identification risks. A coded ID with a separate key is pseudonymization, not full anonymity.',h=42)
after(78,'How would you obtain','Explain purpose, collected data, risks, access, storage duration and withdrawal. Ask for voluntary agreement before collection, without affecting marks.',h=42)
after(79,'Discuss which','A and D make substantial research contributions. B may qualify if implementation is intellectually significant and the authorship policy is met. C’s presentation-only help usually merits acknowledgment. Authors should approve the manuscript and accept responsibility.',h=39,size=8.7)
for m,a in [('1 The same','Simultaneous submission.'),('2 A friend','Gift authorship.'),('3 A negative','Selective reporting / hiding evidence.'),('4 A dataset','Unverified provenance and possible privacy misuse.'),('5 A collaborator','Ghost authorship / missing credit.')]: after(80,m,a,h=14,size=8.5,dy=1)
after(81,'searchers have before','Assess risks, obtain independent ethics review and appropriate informed consent, protect privacy, allow withdrawal, and have a plan to monitor harm. Any proposed consent waiver needs review.',h=38)
after(81,'Additional consideration:','Check whether records can be re-identified by linking datasets; set a retention and deletion plan.',h=28)
after(84,'Topic:','Machine learning for lightweight network intrusion detection.',h=39)
after(84,'Research Question:','Can a reduced-feature RF lower latency without a large loss in F1?',h=39)
rows(84,['Primary keyword','Synonym','Related keyword','Technical term'],['intrusion detection','network anomaly detection','machine learning','feature selection'],x=170,size=8.7)
after(84,'Step 3 – Create','("intrusion detection" OR "network anomaly detection") AND "machine learning" AND ("feature selection" OR lightweight)',h=67,dy=6)
rows(84,['Title','Author(s)','Year','Database','Method','Main Finding','Limitation'],[
 'UNSW-NB15: a comprehensive data set for network intrusion detection systems (UNSW-NB15 network data set).',
 'Nour Moustafa and Jill Slay.', '2015.', 'IEEE Xplore / UNSW repository.',
 'IXIA generation, tcpdump, Argus/Bro flow extraction.',
 'Labeled traffic with nine attack categories.',
 'Lab-generated traffic; external deployment remains to be tested.'
],x=151,w=388,size=8.1)
put(85,151,130,192,11,'Moustafa & Slay (2015)',8.2);put(85,360,130,178,11,'Sharafaldin et al. (2018)',8.2)
for label,a,b in [
 ('Research Problem','Need modern labeled IDS traffic.','Need realistic varied IDS traffic.'),
 ('Method','IXIA + flow extraction.','User profiles + CICFlowMeter.'),
 ('Dataset','UNSW-NB15.','CICIDS2017.'),
 ('Main Result','Nine labeled attack categories.','Five days of normal/attack flows.'),
 ('Strength','Explicit train/test partitions.','Varied attacks and detailed flows.'),
 ('Limitation','One laboratory environment.','Limited capture period and testbed.')]:
 inline(85,label,a,x=151,w=188,size=8.1)
 inline(85,label,b,x=359,w=180,size=8.1)
after(85,'Across the two papers','Labeled normal and attack traffic enables reproducible intrusion-detector evaluation.',h=52)
after(85,'The major difference','UNSW-NB15 uses IXIA-generated traffic; CICIDS2017 uses profiled user behavior and scheduled attacks.',h=52)
after(85,'A possible research gap','Test whether low-cost models retain performance on independent traffic; results from one testbed may not transfer.',h=47)
after(85,'One earlier paper','Tavallaee et al. (2009), A Detailed Analysis of the KDD CUP 99 Data Set [1].',h=34)
after(85,'One newer paper','Koroniotis et al. (2019), Bot-IoT dataset [6], cites Moustafa and Slay’s UNSW-NB15 work.',h=33)
# Offline study: no participants; identifiers excluded from model and outputs.
for yy in [121,135,148,162,175]: check(86,420,yy)
after(86,'Consent procedure:','No participants are recruited. Verify dataset terms and provenance; seek institutional guidance before using any identifiable data.',h=37)
after(86,'Data protection method:','Use access-controlled storage and share only permitted, aggregated results.',h=37)
after(86,'Anonymization method:','Exclude IP addresses and other identifiers; check linkage risks before any release.',h=37)
after(86,'Who will have access','Veer Vikram Singh and the project guide, if access is needed and permitted.',h=33)
after(86,'Potential ethical risk:','Traffic identifiers could reveal activity; avoid re-identification and unsupported security claims.',h=31)
rows(86,['Research Design','Implementation','Data Collection','Data Analysis','Writing','Supervision / Guid-'],[
 NAME,NAME,'Use cited public dataset; log own timings.',NAME,NAME,
 'Project guide, if assigned; authorship only for qualifying contributions.'
],x=179,w=360,size=8.3)
numbered(87,220,280,['IEEE Xplore','ACM Digital Library','PubMed'],x=66)
numbered(87,300,383,['smart healthcare monitoring','wearable sensors','anomaly detection','machine learning'],x=66)
after(87,'Boolean search string:','("smart healthcare" OR "remote patient monitoring") AND (wearable OR sensor) AND ("machine learning" OR "anomaly detection")',h=38)
after(87,'What methods would','Threshold alerts, random forests and time-series neural models.',h=34)
after(87,'What datasets would','Public wearable or physiological-signal datasets with documented consent and labels.',h=34)
after(87,'What limitations would','False alarms, missing signals, biased samples, device differences, privacy and external validation.',h=34)
check(87,344.6,686)
after(87,'Why?','Methodological mapping shows which methods fit the same monitoring task and what evidence is missing.',h=38)
numbered(88,125,208,['Health records may be exposed or linked to named people.','Unclear consent for continuous monitoring.','False alerts or missed events may distress or harm participants.','Biased training data may work poorly for some groups.'],x=66,size=8.8)
after(88,'What personal information','Avoid names, addresses, government IDs, phone numbers and precise location unless essential.',h=35)
after(88,'How will sensitive','Encrypt storage and transfer, restrict access, separate ID keys, aggregate outputs and delete data on schedule.',h=35)
after(88,'Write a short statement','Participation is voluntary. You should know what signals we collect, why, the possible discomforts, who can access them, how long we keep them, and how to withdraw. The system is a research prototype, not a diagnosis.',h=45)
for m,a in [('I will not fabricate','data or results'),('I will not falsify','measurements, methods or findings'),('I will acknowledge','sources and genuine contributions'),('I will protect','participants and their personal information'),('I will report limitations','honestly, including negative findings')]: after(88,m,a,h=20)

# Seven verified literature sources; full references are provided on the original reference page.
REFERENCES=[
 ('M. Tavallaee, E. Bagheri, W. Lu and A. A. Ghorbani (2009). A Detailed Analysis of the KDD CUP 99 Data Set. IEEE Symposium on Computational Intelligence for Security and Defense Applications (CISDA), pp. 1-6. DOI: 10.1109/CISDA.2009.5356528.','https://doi.org/10.1109/CISDA.2009.5356528'),
 ('N. Moustafa and J. Slay (2015). UNSW-NB15: a comprehensive data set for network intrusion detection systems (UNSW-NB15 network data set). Military Communications and Information Systems Conference (MilCIS), pp. 1-6. DOI: 10.1109/MilCIS.2015.7348942.','https://doi.org/10.1109/MilCIS.2015.7348942'),
 ('I. Sharafaldin, A. H. Lashkari and A. A. Ghorbani (2018). Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization. ICISSP, pp. 108-116. DOI: 10.5220/0006639801080116.','https://doi.org/10.5220/0006639801080116'),
 ('Y. Mirsky, T. Doitshman, Y. Elovici and A. Shabtai (2018). Kitsune: An Ensemble of Autoencoders for Online Network Intrusion Detection. Network and Distributed System Security Symposium (NDSS). DOI: 10.14722/ndss.2018.23204.','https://doi.org/10.14722/ndss.2018.23204'),
 ('Y. Meidan, M. Bohadana, Y. Mathov, Y. Mirsky, D. Breitenbacher, A. Shabtai and Y. Elovici (2018). N-BaIoT: Network-based Detection of IoT Botnet Attacks Using Deep Autoencoders. IEEE Pervasive Computing, 17(3), pp. 12-22. DOI: 10.1109/MPRV.2018.03367731.','https://doi.org/10.1109/MPRV.2018.03367731'),
 ('N. Koroniotis, N. Moustafa, E. Sitnikova and B. Turnbull (2019). Towards the development of realistic botnet dataset in the Internet of Things for network forensic analytics: Bot-IoT dataset. Future Generation Computer Systems, 100, pp. 779-796. DOI: 10.1016/j.future.2019.05.041.','https://doi.org/10.1016/j.future.2019.05.041'),
 ('E. C. P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian, R. Lu and A. A. Ghorbani (2023). CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment. Sensors, 23(13), article 5941. DOI: 10.3390/s23135941.','https://doi.org/10.3390/s23135941')
]
inline(92,'Research Topic:','Machine learning for network and IoT intrusion detection',x=141,size=9)
# Reflow within the existing blank reference area to fit full entries legibly.
put(92,42,469,510,323,'',9,True)
for i,(ref,url) in enumerate(REFERENCES):
 put(92,48,474+i*42,494,39,f'[{i+1}] {ref}',7.8)
put(92,48,774,494,15,'References verified from original papers, publishers and institutional repositories.',7.3)
table(93,43,[
 ['Tavallaee et al.\n2009 [1]','Reduce bias in KDD99 evaluation.','Duplicate analysis; difficulty-based selection; NSL-KDD.','Less redundant benchmark for fairer model testing.','Still based on old KDD99 traffic; modern attacks need newer data.'],
 ['Moustafa & Slay\n2015 [2]','Provide modern labeled network traffic.','IXIA traffic; tcpdump; Argus/Bro features; UNSW-NB15.','Normal flows and nine attack categories with labels.','One controlled lab testbed; results need validation on other traffic.'],
 ['Sharafaldin et al.\n2018 [3]','Improve realism and coverage of IDS data.','User-behavior profiles; attack scenarios; CICFlowMeter.','CICIDS2017 offers labeled normal and attack flows.','A five-day testbed capture; it cannot cover every deployment.'],
 ['Mirsky et al.\n2018 [4]','Enable low-cost online anomaly detection.','KitNET ensemble of small autoencoders; streaming features.','Detects abnormal traffic without labeled attack training.','Assumes a clean initial training period; training contamination is a risk.'],
 ['Meidan et al.\n2018 [5]','Detect compromised IoT devices rapidly.','Deep autoencoders; nine devices infected with Mirai/BASHLITE.','Behavior-based models detected botnet attacks in lab tests.','Transfer to other devices/networks remains future work.'],
 ['Koroniotis et al.\n2019 [6]','Support IoT botnet detection and forensics.','Bot-IoT testbed; flow features; SVM, RNN and LSTM evaluation.','A labeled benchmark with varied botnet scenarios.','Simulated IoT services; real-device traffic is a useful extension.'],
 ['Neto et al.\n2023 [7]','Broaden realistic IoT attack benchmarking.','105-device topology; 33 attacks; ML/DL baselines.','Public CICIoT2023 data across seven attack categories.','Transferability and model optimization remain future work.']
],skip=1,size=8.5)
for x,y in [(64,682),(214.2,682),(64,698),(170.3,698),(359.6,698)]: check(93,x,y)

def fill_source():
    from final_refinements import apply, remove_detail_rules
    apply(__import__(__name__))
    reader=PdfReader(SRC); writer=PdfWriter()
    for n,page in enumerate(reader.pages,1):
        remove_detail_rules(page,reader,n,original)
        if n in ops:
            buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=(float(page.mediabox.width),float(page.mediabox.height)))
            H=float(page.mediabox.height)
            # Sample the source background so typed answers can interrupt ruled lines
            # cleanly while preserving the color and structure of the provided spaces.
            preview=Image.open(TMP+f'/s-{n:02}.png').convert('RGB')
            pw,ph=preview.size; sx=pw/float(page.mediabox.width);sy=ph/H
            for x,y,w,h,txt,size,erase,bold in ops[n]:
                if erase:
                    crop=preview.crop((max(0,int(x*sx)),max(0,int(y*sy)),min(pw,int((x+w)*sx)),min(ph,int((y+h)*sy))))
                    hist=crop.getcolors(maxcolors=crop.width*crop.height)
                    bg=max(hist,key=lambda pair:pair[0])[1] if hist else (255,255,255)
                    c.setFillColorRGB(*(v/255 for v in bg));c.rect(x,H-y-h,w,h,fill=1,stroke=0)
                    audit.append({'page':n,'x':x,'y':y,'w':w,'h':h,'text':'MASK'})
                if not txt:continue
                if txt in ('__BOX__','__RULE__'):
                    c.setStrokeColor(BLUE if txt=='__BOX__' else INK);c.setLineWidth(.4)
                    if txt=='__BOX__':c.rect(x,H-y-h,w,h,fill=0,stroke=1)
                    else:c.line(x,H-y,x+w,H-y)
                    continue
                if txt in ('X','__TICK__'):
                    c.setStrokeColor(BLUE);c.setLineWidth(1.15)
                    tx=x+1.1; ty=H-y-5
                    c.lines([(tx,ty,tx+2.4,ty-2.4),(tx+2.4,ty-2.4,tx+7,ty+3.8)])
                    audit.append({'page':n,'x':x,'y':y,'w':9,'h':10,'font':size,'text':'TICK'})
                    continue
                is_label=txt.startswith('__LABEL__:')
                if is_label:txt=txt[len('__LABEL__:'):]
                s=size
                while True:
                    style=ParagraphStyle('answer',fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=s,leading=LEADING.get((n,x,y,txt),s*1.17),textColor=INK if is_label else BLUE,spaceAfter=0)
                    p=Paragraph(escape(txt).replace('\n','<br/>'),style);ww,hh=p.wrap(w,h)
                    if hh<=h+.1 or s<=7:break
                    s-=.2
                if hh>h+.1:warnings.append((n,'overflow',x,y,h,hh,txt))
                if s<size-1:warnings.append((n,'small',round(s,1),txt))
                if n!=92 and not bold:
                    # Whiten only the narrow text footprint, using the actual panel
                    # color, when an existing rule would cross a line of the answer.
                    yy=y
                    for ln in p.blPara.lines:
                        extra=ln[0] if isinstance(ln,tuple) else ln.extraSpace
                        lw=w-extra
                        crosses=any(e['orientation']=='h' and e['x0']<x+lw and e['x1']>x and yy+1<e['top']<yy+s+2 for e in original.pages[n-1].edges)
                        if crosses and lw>0:
                            box=(max(0,int(x*sx)),max(0,int(yy*sy)),min(pw,int((x+lw)*sx)),min(ph,int((yy+s+2)*sy)))
                            crop=preview.crop(box)
                            hist=crop.getcolors(maxcolors=crop.width*crop.height)
                            bg=max(hist,key=lambda pair:pair[0])[1] if hist else (255,255,255)
                            c.setFillColorRGB(*(v/255 for v in bg))
                            c.rect(x-.4,H-yy-s-2,lw+.8,s+2,fill=1,stroke=0)
                        yy+=style.leading
                p.drawOn(c,x,H-y-hh)
                audit.append({'page':n,'x':x,'y':y,'w':w,'h':hh,'font':s,'text':txt})
            if n==92:
                for i,(_,url) in enumerate(REFERENCES):
                    c.linkURL(url,(48,H-474-i*42-39,542,H-474-i*42),relative=0,thickness=0)
            c.save();page.merge_page(PdfReader(buf).pages[0])
        writer.add_page(page)
    # Named section bookmarks and PDF metadata are added to the final combined file below.
    with open(TMP+'/filled_source.pdf','wb') as f:writer.write(f)
    print('Answer placements:',len(audit),'Warnings:',len(warnings))
    for warn in warnings:print(warn)
    json.dump(audit,open(TMP+'/placement_audit.json','w'),indent=2)

if __name__=='__main__':
    fill_source()

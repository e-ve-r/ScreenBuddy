from build_assignment import *

styles={
 'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=21,leading=25,textColor=INK,spaceAfter=12),
 'sub':ParagraphStyle('sub',fontName='Helvetica-Bold',fontSize=12,leading=15,textColor=TEAL,spaceBefore=10,spaceAfter=6),
 'body':ParagraphStyle('body',fontName='Helvetica',fontSize=10.5,leading=15,textColor=INK,spaceAfter=8),
 'small':ParagraphStyle('small',fontName='Helvetica',fontSize=8.5,leading=11,textColor=INK,spaceAfter=6),
 'note':ParagraphStyle('note',fontName='Helvetica',fontSize=9,leading=13,textColor=BLUE,spaceAfter=10),
}
def P(text,kind='body'):return Paragraph(text,styles[kind])
def block(title,text):return [P(title,'sub'),P(text)]
def points(items):return [P(f'<b>{i+1}.</b> {t}') for i,t in enumerate(items)]
def tableflow(data,widths,size=9.4):
 s=ParagraphStyle('cell',fontName='Helvetica',fontSize=size,leading=size*1.3,textColor=INK)
 t=Table([[Paragraph(str(v),s) for v in row] for row in data],colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#dcecf0')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.4,HexColor('#bccbd3')),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
 return t
def furniture(c,d,summary=False):
 W,H=A4;c.setStrokeColor(HexColor('#cbd9e1'));c.line(45,H-47,W-45,H-47)
 c.setFillColor(TEAL);c.setFont('Helvetica-Bold',9)
 c.drawString(45,H-34,'RESEARCH METHODOLOGY IN CS')
 c.setFillColor(INK);c.setFont('Helvetica',8)
 c.drawRightString(W-45,H-34,'REVISION NOTES' if summary else 'MID-SEMESTER SOLUTIONS')
 c.line(45,43,W-45,43)
 c.drawString(45,29,NAME+'  |  '+SAP+'  |  '+BATCH)
 c.drawRightString(W-45,29,('Summary ' if summary else 'Solutions ')+str(d.page))
def build_pdf(path,story,summary=False):
 doc=SimpleDocTemplate(path,pagesize=A4,leftMargin=45,rightMargin=45,topMargin=66,bottomMargin=58,title='Research Methodology - '+('Eight-page Summary' if summary else 'Mid-semester Solutions'),author=NAME)
 doc.build(story,onFirstPage=lambda c,d:furniture(c,d,summary),onLaterPages=lambda c,d:furniture(c,d,summary))

EXAM=[]
def exam(q,title,marks,body):
 if EXAM:EXAM.append(PageBreak())
 EXAM.extend([P(q+' - '+title,'title'),P(marks,'note')]+body)

exam('Q1','Steps in the research process','4 marks',[
 P('Research follows a planned sequence, although some steps may be revisited.'),
 *points([
 'Identify a clear problem, review related work and define the question and scope.',
 'Set objectives and, when appropriate, form a testable hypothesis.',
 'Choose a research design, sample, instruments and data-collection method; collect data responsibly.',
 'Analyze the data, interpret results against the objectives, state limitations and report the findings with references.'
 ]),P('Example: compare two intrusion detectors on the same unseen test data, then explain the difference in F1 and response time.')
])
exam('Q2','Why define a research problem?','4 marks',[
 P('A research problem states the specific issue or unanswered question that the study will address. It turns a broad interest into a manageable investigation.'),
 *points([
 'It gives the study a clear purpose and helps set suitable objectives.',
 'It defines boundaries, preventing unnecessary work.',
 'It guides the choice of data, methods, sample and performance measures.',
 'It helps check feasibility and novelty, and provides a basis for judging the final result.'
 ]),P('For example, "AI in security" is broad; "compare false-alert rates of two IDS models on UNSW-NB15" is researchable.')
])
exam('Q3','Plagiarism and prevention','2 + 2 = 4 marks',[
 *block('(a) Meaning of plagiarism - 2 marks','Plagiarism is presenting another person\'s words, ideas, code, figures or data as your own without proper acknowledgment. Changing a few words does not make copied text original. Undisclosed reuse of earlier work can also be a problem.'),
 *block('(b) How to avoid it - 2 marks','Understand the source, write independently and cite the original idea. Put exact borrowed words in quotation marks and give a citation. Credit reused code, figures and data, follow their reuse terms, and check both citations and similarity matches before submission.')
])
exam('Q4','Fact-finding, analysis and evaluation','4 marks',[
 P('Yes. These activities make research evidence-based rather than a matter of personal opinion.'),
 *points([
 '<b>Fact-finding:</b> collect relevant and reliable observations, such as measured execution times.',
 '<b>Analysis:</b> organize and compare the data to identify patterns or differences.',
 '<b>Evaluation:</b> judge whether the method is sound and the evidence supports the claim.',
 '<b>Interpretation:</b> explain what the result means, considering alternative explanations and limitations.'
 ]),P('For example, one quick program run is insufficient to call an algorithm faster. Repeated runs under equal conditions provide a stronger basis for the conclusion.')
])
exam('Q5','Literature review and study approach','2 + 2 = 4 marks',[
 *block('(a) Literature review - 2 marks','A literature review is a critical account of existing work on a research question. It explains what is known, compares methods and findings, and identifies gaps. It should connect studies rather than merely list their summaries.'),
 *block('(b) Effective approach - 2 marks','Define the question; select academic databases; search with keywords, synonyms and Boolean operators. Screen titles and abstracts, read relevant papers critically, record methods and limitations, and follow citations. Group the findings into themes, identify a defensible gap and cite every borrowed idea.')
])
exam('Q6','Designs for experimental hypothesis testing','10 marks',[
 P('An experimental design states how treatments are assigned, variables are controlled and outcomes are compared. A good design separates the treatment effect from other causes.'),
 *block('1. Before-and-after without a control group','Measure one group before and after treatment. Example: measure server delay before and after a software upgrade. It is simple, but a change in workload or hardware can also explain the difference.'),
 *block('2. After-only with a control group','Assign comparable units to treatment and control groups, preferably at random, and compare post-treatment outcomes. Example: compare two interfaces using separate randomized groups. A pretest is not required, but group comparability matters.'),
 *block('3. Before-and-after with a control group','Measure both groups before and after treatment. Compare their changes, rather than only final scores. Example: compare improvements in two learning groups when only one receives a new tool. This helps account for initial differences and common time effects.'),
 *block('4. Completely randomized design','Assign experimental units randomly to treatments. This reduces systematic allocation bias and suits fairly similar units, such as equivalent virtual machines testing two scheduling policies.'),
 *block('5. Randomized block design','First group units by a known source of variation, then randomize treatments within each block. For example, block machines by processor type before comparing algorithms. Blocking helps separate machine differences from the algorithm effect.'),
 *block('6. Latin square design','Arrange treatments so each appears once in every row and column. Rows and columns control two nuisance factors, such as machine and testing period. It requires suitable assumptions and the same number of levels for treatments and both blocking factors.'),
 *block('7. Factorial design','Study two or more factors together using their combinations. A 2 x 2 experiment could vary algorithm and traffic load. It estimates each factor\'s effect and whether the effect of one depends on the other.'),
 P('Randomization, replication, fair controls and a preselected outcome measure make hypothesis tests more credible.','note')
])
exam('Q7','Hypotheses, deduction and induction','5 + 5 = 10 marks',[
 *block('(a) Formulation and purpose of a hypothesis - 5 marks','A research hypothesis is a clear, testable prediction about a difference or relationship. Begin with a defined problem, review evidence and theory, identify measurable variables, specify the population and conditions, and state a prediction that data could contradict.'),
 P('<b>Example:</b> using the same UNSW-NB15 split and laptop, a 15-feature random forest has lower mean prediction latency than a full-feature random forest. The independent variable is the feature configuration; latency is the dependent variable.'),
 P('For a statistical test, the null hypothesis H0 may state no reduction in mean latency, while H1 states lower mean latency. Decide the test, assumptions and significance level before examining the result. The hypothesis guides data collection and analysis, makes the claim precise and helps avoid choosing a convenient explanation after seeing the data. Failure to reject H0 does not prove it true.'),
 *block('(b) Deductive and inductive research - 5 marks','Deduction moves from a general rule or theory to a specific prediction. A valid deductive conclusion follows necessarily when its premises are true. Induction moves from particular observations to a broader pattern; its conclusion remains uncertain.'),
 tableflow([
 ['Aspect','Deduction','Induction'],
 ['Starting point','Theory or general rule','Observed cases or data'],
 ['Direction','General to specific','Specific to general'],
 ['Typical task','Test a prediction; prove a property','Identify a pattern; develop a theory'],
 ['Example','Apply a shortest-path theorem to a graph meeting its assumptions','Observe lower latency across several tests and propose that a method is generally faster']
 ],[90,207,207],9),
 P('A study may use both: observations suggest a hypothesis, then a planned experiment tests predictions derived from it.')
])
exam('Q8','Types of research with examples','2.5 + 2.5 + 2.5 + 2.5 = 10 marks',[
 *block('(a) Fundamental research - 2.5 marks','Fundamental research develops general knowledge, principles or explanations without requiring an immediate practical product. It asks how or why something works. Example: studying which problems can be computed by different abstract machine models. Its contribution is theoretical understanding that may later support applications.'),
 *block('(b) Basic research - 2.5 marks','Basic research is commonly another name for fundamental research; there is no necessary separate category. It explores underlying ideas and builds knowledge. Example: proving a new lower bound on the number of comparisons needed for a sorting problem. A useful result can exist even without building software.'),
 *block('(c) Applied research - 2.5 marks','Applied research uses knowledge to address a specific practical problem. It usually evaluates a proposed solution in a defined setting. Example: comparing feature-selection methods to reduce intrusion-detector latency on a low-cost machine. Its value is judged by both sound evidence and usefulness for the target problem.'),
 *block('(d) Industrial research - 2.5 marks','Industrial research is carried out for an organization\'s operational, product or process needs. It often combines applied research, testing and development under cost and deployment constraints. Example: a software company experiments with scheduling methods to reduce cloud-service delay and running costs. It should still use fair comparisons and report limitations.'),
 P('These labels overlap: an industrial project may be applied, while basic and fundamental research usually describe the same broad aim.','note')
])
exam('Q9','Inference on vaccine effectiveness','10 marks - main choice',[
 P('<b>Correction to the question:</b> the total deaths should be 2 + 10 = <b>12</b>, not 21. Survival totals 19 and the grand total 31 are correct. The calculation below uses the four given cell counts.'),
 tableflow([['Group','Survived','Died','Total'],['Inoculated','15','2','17'],['Not inoculated','4','10','14'],['Total','19','12','31']],[170,110,110,114]),
 *block('1. State the hypotheses','H0: vaccination status and survival are independent. H1: they are associated. Use a 5% significance level.'),
 *block('2. Compare the observed survival','Inoculated survival = 15/17 = 88.24%. Non-inoculated survival = 4/14 = 28.57%. The survival difference is 59.67 percentage points, favoring the vaccinated group.'),
 *block('3. Calculate expected counts','Under H0, expected count = (row total x column total) / 31. Expected counts are 10.42 survived and 6.58 died for inoculated goats, and 8.58 survived and 5.42 died for non-inoculated goats. All exceed 5, so the Pearson chi-square approximation is reasonable if observations are independent.'),
 *block('4. Test the association','For a 2 x 2 table, chi-square = N(ad - bc)^2 / [(a+b)(c+d)(a+c)(b+d)].<br/>Here a = 15, b = 2, c = 4 and d = 10.<br/>chi-square = 31(15 x 10 - 2 x 4)^2 / (17 x 14 x 19 x 12) = <b>11.52</b>.<br/>Degrees of freedom = (2 - 1)(2 - 1) = 1. The 5% critical value is 3.84; p is approximately 0.00069.'),
 *block('5. Inference','Since 11.52 exceeds 3.84, reject H0. Survival is significantly associated with vaccination, and the observed direction supports vaccine effectiveness in this experiment. The small sample and unknown allocation procedure limit wider or purely causal claims. The vaccine is not shown to be perfectly protective: two inoculated goats died.')
])
exam('Q10','Short notes on research problem development','5 + 5 + 5 + 5 = 20 marks',[
 *block('(a) Experience survey - 5 marks','An experience survey gathers insights from people with practical knowledge of the topic, such as developers, users or domain experts. It is mainly useful during exploratory research when the problem is not yet clear. Use open questions, select people for relevant experience, and record recurring issues and alternative explanations. For example, interview network administrators about the causes of false intrusion alerts. Their answers may suggest variables and hypotheses, but they are not a representative statistical estimate of all administrators. Protect participants\' privacy and avoid leading questions.'),
 *block('(b) Pilot survey - 5 marks','A pilot survey is a small trial of the planned survey before the main data collection. It checks whether questions are clear, answer choices are suitable, instructions work and the survey takes a reasonable time. It can reveal missing options, technical faults and recruitment difficulties. For example, try an app-usability questionnaire with five volunteers and ask which questions were confusing. Revise the instrument before the full study. A pilot is for checking feasibility and measurement; its small results should not be treated as strong population findings.'),
 *block('(c) Components of a research problem - 5 marks','A research problem contains a person or group facing a difficulty, a defined setting, a desired outcome, possible alternative actions, and uncertainty about which alternative works best. In an IDS study, the affected group is network operators; the setting is limited hardware; the goal is timely detection with fewer false alerts; alternatives include full and reduced-feature models; uncertainty concerns their performance trade-off. A good statement should also make the variables, target dataset and boundaries clear. These components explain who needs an answer, what must improve and what evidence will resolve the uncertainty.'),
 *block('(d) Rephrasing the research problem - 5 marks','Rephrasing converts an initial vague idea into a precise, researchable statement after reading, discussion and feasibility checks. Identify the main difficulty, clarify terms, narrow the setting, state the variables and define measurable outcomes. The revised statement should preserve the real need while removing impossible claims. Example: change "make AI security better" to "compare full-feature and 15-feature random forests on UNSW-NB15 using F1, false-positive rate and latency within eight weeks." This statement guides method selection and makes success assessable. Further rephrasing is appropriate if a pilot exposes missing data or unrealistic assumptions.')
])
exam('Q11','Paraphrasing and academic integrity','5 + 5 + 5 + 5 = 20 marks - main choice',[
 *block('(a) Three copied sentences with changed words and a citation - 5 marks','Yes, this can still be plagiarism through close paraphrasing or patchwriting. A citation credits the source idea, but replacing a few words does not make the wording and structure independent. If distinctive wording is kept, it needs quotation marks as well as a citation. If the passage is paraphrased, read until you understand it, set the source aside, write a new explanation and compare it with the original for accuracy. For instance, replacing "large labeled datasets" with "big annotated datasets" while keeping the whole sentence pattern is insufficient. Both language and ideas require proper handling.'),
 *block('(b) Paraphrasing, similarity and integrity - 5 marks','Good paraphrasing often reduces text matches because the writer explains the meaning using independent wording and sentence structure. The aim is an accurate account of the source, not a target similarity score. Identify the central point, write from understanding, keep necessary technical terms and cite the source. Then check that no qualifiers or conclusions have changed. A low similarity score cannot prove originality, and correct technical phrases may still match. Combine paraphrasing with your own comparison or analysis so the assignment shows understanding. Do not manipulate wording simply to conceal copying.'),
 *block('(c) AI paraphrasing of entire sections - 5 marks','The main concerns are loss of meaning, invented claims or references, hidden copying, weak personal understanding and lack of transparency. AI may remove important conditions or turn a cautious result into a strong claim. Uploading unpublished or sensitive material can also create confidentiality risks. The researcher should verify every factual statement and reference against the original, retain necessary citations, protect confidential information, and follow the institution\'s rules about AI use and disclosure. The researcher remains responsible for the final work. A rewritten section is not evidence of original research or independent analysis.'),
 *block('(d) Citation in paraphrasing - 5 marks','A citation identifies the source of a borrowed idea, lets the reader verify it and distinguishes source knowledge from the writer\'s contribution. Paraphrasing changes expression, not ownership of the idea. Therefore, paraphrasing alone does <b>not</b> remove the need for citation; the premise in the question is incorrect. Cite the original paper close to the borrowed claim and include a matching full reference. Exact retained wording also requires quotation marks and a locator where the style calls for one. Common knowledge and your own clearly identified analysis may not need citations, but specific borrowed findings, methods and arguments do.')
])

exam('Q9 OR','Alternative study answers','5 + 5 = 10 marks - optional study appendix',[
 P('This appendix answers the OR choice for revision. In the actual examination, submit one Q9 choice only.','note'),
 *block('(a) Necessity of defining a research problem - 5 marks','A defined research problem converts a broad area into a question that can be answered with evidence. It states what is uncertain, why it matters and the setting in which it will be investigated. This directs the objectives, boundaries, design and data collection. It also helps assess whether time, skills and resources are sufficient, and whether prior work already provides the answer. For example, "network security" becomes "does a 15-feature random forest reduce prediction latency on UNSW-NB15 with only a small F1 loss?" A precise problem prevents scattered work and provides a clear basis for judging the conclusion.'),
 *block('(b) Modern means of conducting literature surveys - 5 marks','Use digital libraries such as IEEE Xplore and ACM DL for original papers, and indexing databases such as Scopus or Web of Science to trace citations. Google Scholar can broaden discovery; arXiv provides preprints whose review status must be checked. Search titles and abstracts with exact phrases, synonyms, AND and OR; apply relevant year or subject filters. Use backward and forward citation chaining to find related studies. Read full papers, record methods and limitations, remove duplicates, and manage references in Zotero or a similar tool. Group findings by theme or method and use alerts to identify relevant new work. Check original sources rather than relying on generated summaries.')
])
exam('Q11 OR','Similarity reports and plagiarism','5 + 5 + 5 + 5 = 20 marks - optional study appendix',[
 P('These are the OR answers for study. In the actual examination, submit one Q11 choice only.','note'),
 *block('(a) Is 18% similarity acceptable? - 5 marks','There is no universal percentage that decides plagiarism. Eighteen percent may be acceptable if the matches are properly marked quotations, references, standard technical phrases or other legitimate overlap, and the work meets the institution\'s rules. It may be unacceptable if even a small part contains uncredited results, distinctive wording, copied code or closely paraphrased argument. Examine the largest source matches, where they occur, whether citations and quotation marks are present, and the report\'s filters. A score depends on database coverage and settings. Keep required quotations and citations; do not remove them just to lower the number. A human judgment of attribution and originality is still necessary.'),
 *block('(b) Mosaic plagiarism and missed detection - 5 marks','Mosaic plagiarism combines phrases, sentence patterns or ideas from one or several sources with small changes, presenting the assembled text as independent writing. It may produce only small scattered matches, especially if sources are not in the tool\'s database, are translated, or contain changed wording. The total score can therefore look modest despite substantial copying. For example, joining each source\'s opening phrase with another source\'s explanation is not an original synthesis. To avoid it, take idea-based notes, explain the relationship between studies in your own structure, cite the sources and quote any distinctive wording that must be retained.'),
 *block('(c) Improper citation after paraphrasing - 5 marks','A paraphrased idea still belongs to its source. Omitting the citation, placing it so far away that attribution is unclear, citing a source that does not support the claim, or listing a reference only in the bibliography can all mislead readers. A citation should appear near the borrowed idea and match an accurate reference entry. If several sources support a paragraph, show which findings come from which source. When only a secondary account was read, do not imply that the original was consulted. Correct paraphrasing and precise attribution work together; neither substitutes for the other.'),
    *block('(d) Role and limitations of similarity tools - 5 marks','Turnitin and iThenticate compare submitted text against indexed material and show matching passages and sources. They help reviewers find unattributed overlap, close paraphrasing and some reused material. They are screening aids, not automatic verdicts. Their coverage is incomplete; settings affect scores; legitimate quotations and references may match; translated or heavily rewritten text may escape detection; and text tools do not fully assess copied ideas, code, images, fabrication or the quality of an argument. Review the actual passages, source evidence and citation practice. A high score can be legitimate, while a low score can still hide misconduct.'),
    P('Source for similarity-report interpretation: <link href="https://guides.turnitin.com/hc/en-us/articles/34400565079053-Turnitin-and-plagiarism" color="#15476b">Turnitin Guides, "Turnitin and plagiarism"</link>.','small')
])

# Exactly two summary pages per requested component, without an extra cover page.
SUMMARY=[]
def summary(title,subtitle,body):
 if SUMMARY:SUMMARY.append(PageBreak())
 SUMMARY.extend([P(title,'title'),P(subtitle,'note')]+body)

summary('Worksheet 1 - Research problems','Page 1 of 2 | Finding a clear, feasible question',[
 *block('What research means','Research is a systematic investigation that uses evidence to answer a question. A software project becomes research when it investigates a defined uncertainty and evaluates a claim, rather than only producing an app.'),
 *block('A useful research chain','Problem identification - literature reading - question and hypothesis - design - data collection - analysis - interpretation - reporting. Exploratory studies may develop a hypothesis after observing patterns, then test it in a later study.'),
 *block('Where problems come from','Look for gaps in papers, practical difficulties, recent technologies, earlier coursework, datasets and conversations with experienced people. Start broadly, narrow through reading, formulate a question, and check feasibility and novelty.'),
 tableflow([['Topic','Research problem'],['Network security','Can a 15-feature RF lower intrusion-detection latency with only a small F1 loss?'],['AI in smart cities','Does adaptive timing reduce waiting at one simulated junction?']],[170,334]),
 *block('Quality check','A good problem is clear, researchable, feasible, relevant and non-trivial. It identifies what will be measured and permits data collection and analysis. A possible gap must be checked in the literature before it is called novel.'),
 *block('Common selection mistakes','Avoid vague promises, enormous scope, trivial questions, missing resources and ignoring prior work. "Detect every threat perfectly" is not realistic. Limit the study by time, dataset, target setting, tools and what is out of scope.'),
 *block('SMART objective','Specific, Measurable, Achievable, Relevant and Time-bound. Example: within eight weeks, compare full-feature and 15-feature random forests on the official UNSW-NB15 split using F1, false-positive rate and five-run mean latency.'),
 P('<b>Remember:</b> a topic names an area; a problem names the uncertainty; an objective states what the study will accomplish.','note')
])
summary('Worksheet 1 - Evidence and meaning','Page 2 of 2 | Data, instruments and interpretation',[
 tableflow([['Approach','Main purpose / example'],['Exploratory','Discover ideas where little is known; interview developers.'],['Descriptive','Describe characteristics; summarize usability ratings.'],['Analytical','Study relationships or differences in existing information.'],['Theoretical','Use models, logic or proof; prove an algorithm property.'],['Empirical','Use observations or experiments; benchmark an IDS.']],[125,379]),
 *block('Two ways to classify data','Primary data are collected directly for the study; secondary data already exist. Qualitative data describe meanings or experiences; quantitative data contain numerical measurements. These classifications are independent. Downloaded network flows are secondary; timings you measure are primary.'),
 *block('Choose a collection tool','Use a questionnaire for satisfaction, an observation log for user behavior, Wireshark for packets, and monitoring tools for CPU or memory. For web collection, check permission, terms and privacy. Record what is collected, its source, frequency and the consistency checks.'),
 *block('Instrumentation and repeatability','Instrumentation includes sensors, simulators, benchmark suites, timers and custom software. Calibration checks measurement accuracy. Repeatability requires controlled settings, recorded versions and the same measurement procedure. Without it, a difference may be noise rather than a real effect.'),
 *block('Analyze, then interpret','Analysis identifies the measurements and patterns. Interpretation connects them to the question. With A = 92%/20 ms, B = 95%/70 ms and C = 94%/25 ms, B is most accurate and A is fastest. If accuracy must be at least 93% and fast response matters, investigate C first.'),
 *block('Defend a study in one minute','State the practical problem, the gap to verify, the objective and the evidence. For the IDS example, report F1 loss, false alerts and latency on the same independent test split. Do not generalize to every network from one benchmark.'),
 P('<b>Quick recall:</b> relevance tells you why the study matters; scope tells you its limits; evidence tells you whether the claim is supported.','note')
])
summary('Worksheet 2 - Reasoning and proof','Page 1 of 2 | Claims, challenges and valid conclusions',[
 *block('Dialectic','A claim is challenged using counterarguments, evidence and assumptions, then refined. "Greedy algorithms are always optimal" fails for coins {1,3,4} and amount 6: greedy takes 4+1+1, but 3+3 uses fewer coins. The improved claim specifies a problem with a valid greedy-choice property.'),
 tableflow([['Reasoning','Direction','Certainty / example'],['Deduction','General to specific','Necessary if premises and logic are sound; apply a theorem.'],['Induction','Cases to a general pattern','Probable; a model wins on several datasets.'],['Abduction','Observation to likely explanation','Plausible; investigate a slow query after an app slowdown.']],[95,133,276]),
 *block('Validation methods','A demonstration shows that a prototype works for selected cases. Empirical validation measures performance under tested conditions. Mathematical proof establishes a statement logically under explicit assumptions. A few successful examples cannot prove universal correctness or efficiency.'),
 *block('Four mathematical proof methods','<b>Direct:</b> derive the result from assumptions. If a = 2m and b = 2n, then a+b = 2(m+n), which is even.<br/><b>Contradiction:</b> assume the opposite; a supposed largest integer L is contradicted by L+1.<br/><b>Induction:</b> prove a base case, assume the k case, then show k+1.<br/><b>Contrapositive:</b> prove "not Q implies not P" to establish "P implies Q."'),
 *block('Induction example','For 1 + 2 + ... + n = n(n+1)/2, the n=1 case is true. Assuming the k case, adding k+1 gives (k+1)(k+2)/2. Therefore the formula holds for every positive integer.'),
 *block('Choose evidence for the claim','Use a formal proof for algorithm correctness, empirical trials for a faster ML model, a prototype for robot feasibility and a proof under explicit assumptions for a cryptographic construction.'),
 P('<b>Remember:</b> mathematical induction is a proof method. Inductive research generalization remains uncertain.','note')
])
summary('Worksheet 2 - Models and evaluation','Page 2 of 2 | Build a method and test it fairly',[
 *block('Theoretical models','Finite automata represent regular languages; graphs represent networks; Turing machines help study computability; Boolean algebra represents logical operations. Models simplify a system so that its behavior can be analyzed, but may omit practical constraints.'),
 *block('Algorithmic research','Define input and output, propose an algorithm, analyze time and space, establish correctness, and test the implementation. Binary search on a sorted array takes O(log n) time and O(1) extra space iteratively. Include empty arrays, absent targets and boundary cases in tests.'),
 *block('Research software','Use clear requirements, modular design, version control, testing and documentation. Record dependencies, configurations, data splits and seeds so another person can reproduce the experiment. Faulty code can create faulty research evidence.'),
 *block('Mathematical modelling','Define the system, assumptions, variables and equations; analyze and validate against observations. In an M/M/1 queue, arrival rate is lambda and service rate is mu. Under the model assumptions and lambda &lt; mu, mean system time W = 1/(mu - lambda). If arrivals exceed service, an unbounded queue is unstable; finite buffers drop packets.'),
 tableflow([['Evaluation need','Useful evidence / tool'],['Detection quality','Precision, recall, F1, false-positive rate; unseen test data.'],['Speed and resources','Latency, throughput and peak memory; timers and profilers.'],['Scaling / reliability','Several workloads, repeated trials and failure checks.'],['Network simulation','NS-3 or OMNeT++.'],['Continuous monitoring','Prometheus collects metrics; Grafana displays them.']],[155,349]),
 *block('Fair empirical comparison','Keep the split, environment and measurement method equal. Report baselines and variability. Choose the best model for the goal; accuracy alone is insufficient. In the supplied table, A has higher accuracy and recall, while B has higher precision and F1. Both F1 values are consistent with rounding.'),
 P('<b>Irrigation example:</b> compare adaptive and fixed control in matched plots; measure water use and crop condition; check rainfall and sensor errors. Expected improvement is a hypothesis, not an observed result.','note')
])
summary('Worksheet 3 - Find and connect papers','Page 1 of 2 | Search, analysis, synthesis and mapping',[
 *block('Literature search and review','Search finds relevant existing studies systematically. A review explains what they collectively show, where they differ and what remains uncertain. Original papers are primary scholarly sources; surveys and reviews are secondary. A preprint may be useful, but its review status must be checked.'),
 *block('A practical search sequence','Define the question; choose academic sources; list keywords and synonyms; form a query; screen titles and abstracts; read full papers; record citations; compare and group the findings. Keep a log of dates, queries, sources and selection decisions.'),
 tableflow([['Search element','Meaning / example'],['AND','Require both terms: "intrusion detection" AND "machine learning".'],['OR','Include alternatives: IoT OR "Internet of Things".'],['NOT','Exclude a term, but avoid accidentally losing relevant work.'],['Quotation marks','Search an exact phrase where supported.'],['Filters','Use relevant subject, year and publication-type limits.']],[125,379]),
 *block('Where to search','IEEE Xplore and ACM DL are useful computing libraries. SpringerLink and ScienceDirect provide publisher collections. Scopus and Web of Science help with indexing and citations. Scholar broadens discovery; check important claims in original papers.'),
 *block('Read critically','For each paper, record the problem, method, dataset, metrics, main finding and limitations. Ask whether the test data are independent, the baseline is fair and the conclusions match the evidence. Different datasets can make headline accuracy values incomparable.'),
 *block('Analysis, synthesis and mapping','Analysis examines one study. Synthesis connects several studies into a supported conclusion. Mapping organizes them by theme, date, method, citation links or concepts. For IDS research, compare dataset quality, lightweight detection and transfer to new traffic.'),
 *block('Citation chaining','Backward chaining examines a paper\'s references. Forward chaining finds later work that cites it. Search alerts help keep a long project current. A proposed gap, such as weak deployment validation, needs evidence across the literature.'),
 P('<b>Selected review:</b> seven real papers cover NSL-KDD, UNSW-NB15, CICIDS2017, Kitsune, N-BaIoT, Bot-IoT and CICIoT2023. Full references are in the completed literature-survey pages.','note')
])
summary('Worksheet 3 - Write and research ethically','Page 2 of 2 | Attribution, privacy, authorship and approval',[
 *block('Citation and reference management','Cite borrowed ideas close to the claim and provide a matching full reference. Keep one citation style. IEEE commonly numbers sources; APA commonly uses author and year. Reference managers help organize entries, but check author names, dates, titles and identifiers yourself.'),
 *block('Paraphrase properly','Understand the source, set it aside, explain the idea using a new structure, check meaning and cite it. Replacing words with synonyms is not enough. Exact wording needs quotation marks. A citation alone does not turn patchwork copying into original writing.'),
 tableflow([['Issue','Meaning'],['Direct plagiarism','Copying words without proper acknowledgment.'],['Mosaic / patchwriting','Joining copied fragments or retaining source structure.'],['Undisclosed reuse','Presenting earlier work as a new contribution.'],['Fabrication','Inventing data or results.'],['Falsification','Changing evidence so the research record is misleading.']],[145,359]),
 *block('Similarity is not a verdict','Inspect what matched, its source and whether attribution is adequate. Legitimate references or quotations can match. Uncredited ideas, translations or excluded sources may escape detection. No universal percentage proves integrity.'),
 *block('Protect participants and data','Collect only what the question needs. Explain purpose, procedures, risks, access and withdrawal; obtain appropriate consent. Use secure storage and restrict access. Removing a name may not prevent re-identification. A coded ID with a retained key is pseudonymization rather than complete anonymity.'),
 *block('Authorship and publication ethics','Credit significant contributors fairly. Avoid gift authorship, omitted authors, simultaneous duplicate submissions and hidden negative findings. Presentation-only help usually receives acknowledgment. Apply the venue\'s authorship policy and ensure authors accept responsibility.'),
 *block('Ethical review','Ask the institutional ethics committee about work involving people, sensitive data or identifiable records. Protect voluntary participation, confidentiality, minimal risk, withdrawal and fair recruitment. For healthcare monitoring, consider false alerts, missed events and unequal model performance.'),
 P('<b>Remember:</b> public data can still create privacy risks. Verify provenance, permitted use and re-identification risk before using or sharing it.','note')
])
summary('Mid-semester - Core answer framework','Page 1 of 2 | Q1-Q8 and mark-based writing',[
 *block('Write to the marks','For a 4-mark answer, give a short definition and four linked points or steps. For 5 marks, explain the idea, its purpose, a simple example and a limitation. For 10 marks, develop the major parts with suitable examples. Keep question numbers and subpart letters visible.'),
 tableflow([
 ['Question','What the answer should contain'],
 ['Q1: research process','Problem and review; objectives/hypothesis; design and collection; analysis, interpretation and reporting.'],
 ['Q2: defining a problem','Direction, scope, method choice, feasibility, novelty and a basis for evaluation.'],
 ['Q3: plagiarism','Definition (2 marks), then independent paraphrasing, quotation and citation (2 marks).'],
 ['Q4: fact-finding','Agree with reasons: reliable facts, analysis, critical evaluation and cautious interpretation.'],
 ['Q5: review','Critical connection of prior work; then a systematic search, screening and synthesis process.']
 ],[133,371],9.5),
 *block('Q6: experimental designs','Explain before/after without control, after-only with control, before/after with control, completely randomized, randomized block, Latin square and factorial designs. Compare what each controls and its limitations. Randomization reduces allocation bias; replication estimates variability.'),
 *block('Q7(a): hypothesis','Form a clear prediction using literature, measurable variables, a defined setting and a suitable test. State H0 and H1 when testing statistically. A hypothesis guides evidence collection and can be contradicted; a test that fails to reject H0 does not establish it as true.'),
 *block('Q7(b): reasoning','Deduction derives a specific conclusion from general premises; induction develops a broader claim from observations. Deduction can be logically certain under true premises. Induction remains uncertain because unseen cases may differ.'),
 *block('Q8: research types','Fundamental/basic research develops general knowledge; the terms usually overlap. Applied research addresses a specific practical need. Industrial research serves an organization\'s product or process goals and can also be applied.'),
 P('<b>Exam choice rule:</b> Q9 and Q11 each contain OR options. The combined PDF separates the alternatives into a study appendix; choose one option per question in an actual exam.','note')
])
summary('Mid-semester - Statistics and integrity','Page 2 of 2 | Q9-Q11 and the OR choices',[
 *block('Q9: vaccine table correction','The cells are 15 survived/2 died for 17 inoculated goats and 4 survived/10 died for 14 non-inoculated goats. Total deaths are <b>12, not the printed 21</b>; survival is 19 and N is 31.'),
 tableflow([['Step','Result'],['Survival rates','15/17 = 88.24%; 4/14 = 28.57%.'],['H0','Vaccination and survival are independent.'],['Expected counts','10.42, 6.58, 8.58 and 5.42.'],['Pearson test','chi-square = 11.52; df = 1; 5% critical value = 3.84.'],['Decision','Reject H0; p approximately 0.00069.'],['Inference','Association favors vaccination; wider causal claims depend on study design.']],[130,374],9.4),
 *block('Q10: four short notes','<b>Experience survey:</b> ask knowledgeable people to clarify an emerging problem; expert views are not a population estimate.<br/><b>Pilot survey:</b> run a small trial to check questions, instructions and feasibility.<br/><b>Problem components:</b> affected group, setting, desired goal, alternatives and uncertainty.<br/><b>Rephrasing:</b> narrow a vague idea into a measurable, feasible question.'),
 *block('Q11: main integrity answers','A few changed words plus a citation can still be close paraphrasing. Good paraphrasing explains meaning independently and still cites the source. AI rewriting needs factual checks, original citations, privacy care and compliance with institutional rules. Paraphrasing does <b>not</b> remove the need for citation.'),
 *block('OR choices: what to remember','For Q9 OR, explain why a clear problem guides the study and how modern databases, Boolean searches, screening, citation chaining and reference tools support a survey. For Q11 OR, interpret similarity matches in context, explain mosaic plagiarism, show why attribution is required after paraphrasing, and discuss detection tools\' incomplete coverage.'),
 P('<b>Final check:</b> use correct question numbers, answer every chosen subpart, show workings for the statistical question, and distinguish measured facts from predictions and examples.','note')
])

if __name__=='__main__':
 build_pdf(TMP+'/midsem_solutions.pdf',EXAM)
 build_pdf(OUT+'/Research_Methodology_8_Page_Summary.pdf',SUMMARY,True)
 r=PdfReader(TMP+'/midsem_solutions.pdf');s=PdfReader(OUT+'/Research_Methodology_8_Page_Summary.pdf')
 print('Exam pages',len(r.pages),'Summary pages',len(s.pages))
 assert len(s.pages)==8,'Summary must contain exactly 8 pages'
 # Preserve all supplied pages, adding the numbered solutions after the exam paper.
 filled=PdfReader(TMP+'/filled_source.pdf');w=PdfWriter()
 for p in filled.pages[:91]:w.add_page(p)
 for p in r.pages:w.add_page(p)
 for p in filled.pages[91:]:w.add_page(p)
 w.add_outline_item('Worksheet 1 - Unit I',0)
 w.add_outline_item('Worksheet 2 - Unit II',20)
 w.add_outline_item('Worksheet 3 - Unit III',49)
 w.add_outline_item('Mid-semester question paper',89)
 w.add_outline_item('Mid-semester answers Q1-Q11',91)
 w.add_outline_item('OR choices - study appendix',102)
 w.add_outline_item('Completed literature survey',91+len(r.pages))
 w.add_metadata({'/Title':'Research Methodology - Completed Assignment','/Author':NAME,'/Subject':'Worksheets 1-3, mid-semester solutions and seven-paper literature survey'})
 with open(OUT+'/Research_Methodology_Completed_Assignment.pdf','wb') as f:w.write(f)
 print('Combined pages',len(w.pages))

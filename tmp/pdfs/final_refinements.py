from pypdf.generic import ContentStream

def remove_detail_rules(page, reader, n, original):
    areas={1:(270,310),21:(200,246),50:(333,452),92:(80,123)}
    if n not in areas:return
    lo,hi=areas[n]; H=float(page.mediabox.height)
    targets=[(e['x0'],H-e['top'],e['x1'],H-e['top'])
             for e in original.pages[n-1].lines
             if abs(e['y0']-e['y1'])<.1 and lo<e['top']<hi]
    stream=ContentStream(page.get_contents(),reader)
    matrix=(1,0,0,1,0,0);stack=[];segments=[];last=None;removed=0
    def pt(x,y):
        a,b,c,d,e,f=matrix;return a*x+c*y+e,b*x+d*y+f
    for i,(args,op) in enumerate(stream.operations):
        if op==b'q':stack.append(matrix)
        elif op==b'Q':matrix=stack.pop()
        elif op==b'cm':
            a,b,c,d,e,f=matrix;aa,bb,cc,dd,ee,ff=map(float,args)
            matrix=(a*aa+c*bb,b*aa+d*bb,a*cc+c*dd,b*cc+d*dd,a*ee+c*ff+e,b*ee+d*ff+f)
        elif op==b'm':last=pt(*map(float,args))
        elif op==b'l':
            end=pt(*map(float,args));segments.append((*last,*end));last=end
        elif op in (b're',b'c',b'v',b'y',b'h'):segments.append(None)
        elif op in (b'S',b's',b'f',b'f*',b'F',b'B',b'B*',b'b',b'b*',b'n'):
            if op==b'S' and len(segments)==1 and segments[0] is not None:
                seg=segments[0]
                if any(max(abs(a-b) for a,b in zip(seg,t))<.07 for t in targets):
                    stream.operations[i]=([],b'n');removed+=1
            segments=[];last=None
    assert removed==len(targets),(n,removed,len(targets))
    page.replace_contents(stream)

def apply(b):
    def replace(n,old,new):
        hits=[i for i,o in enumerate(b.ops[n]) if o[4]==old]
        assert len(hits)==1,(n,old,hits)
        i=hits[0];o=list(b.ops[n][i]);o[4]=new;b.ops[n][i]=tuple(o)
    def drop(n,check):b.ops[n]=[o for o in b.ops[n] if not check(o)]
    def label(n,x,y,w,text,size=9,bold=False):b.put(n,x,y,w,22,'__LABEL__:'+text,size,bold=bold)
    def field(n,anchor,text,x,w,size=10):
        b.put(n,x,b.line(n,anchor)['y']-.207*size,w,14,text,size)
    # Personal details occupy the intended fields; remove their unused rules.
    for n in (1,21,50,92):
        drop(n,lambda o:o[4] in [b.NAME,b.SAP,b.BATCH,b.DATE])
    for n,coords in [(1,[(89,260),(439,105),(97,240),(446,100)]),
                     (21,[(101,185),(365,183),(101,185),(365,183)]),
                     (50,[(233,249)]*4),
                     (92,[(187,122),(409,102),(187,122),(409,102)])]:
        for (anchor,value),(x,w) in zip([('Name:',b.NAME),('Roll No.:',b.SAP),('Section:',b.BATCH),('Date:',b.DATE)],coords):
            field(n,anchor,value,x,w,9 if n==92 else 10)

    # Short blanks need short, single-line answers.
    drop(5,lambda o:o[4] in ['Research problem','Can fewer RF features reduce IDS latency? (Research problem)'])
    b.ops[5].append(b.on_rule(5,433.296,137.0,533.6,'Research problem',8.4))
    b.ops[5].append(b.on_rule(5,184.145,172.1,533.6,'Can fewer RF features reduce IDS latency?',8.2))
    replace(42,'B: reported F1 is 90%.','B: 90%.')
    for old,new in [('Prove order and permutation properties.','Prove the output is sorted.'),
                    ('Compare metrics on unseen test data.','Test on unseen data.'),
                    ('Show path following in a prototype.','Show a working prototype.'),
                    ('Prove security under stated assumptions.','Prove security assumptions.')]:replace(27,old,new)

    # Two source form rows wrap their final label back to the left. Reflow each
    # into two aligned pairs while preserving the original fields and answers.
    drop(13,lambda o:o[4] in ['Eight weeks','UNSW-NB15 official split','Python / scikit-learn','Live deployment',
                              'Quantitative; both sources','UNSW data + own timings','Python CSV logger','Laptop + timer'])
    b.put(13,60,407.4,476,38.5,'',9,True)
    b.put(13,60,562.6,476,38.7,'',9,True)
    for yy,left,right in [(411,('Time:','Eight weeks'),('Dataset:','UNSW-NB15 official split')),
                          (430,('Tools:','Python / scikit-learn'),('Out of scope:','Live deployment')),
                          (566,('Data type(s):','Quantitative; both sources'),('Source(s):','UNSW data + own timings')),
                          (585,('Collection tools:','Python CSV logger'),('Instrumentation:','Laptop + timer'))]:
        label(13,62,yy,100,left[0],8.6);b.put(13,145,yy,148,14,left[1],8.1)
        label(13,305,yy,106,right[0],8.6);b.put(13,397,yy,137,14,right[1],8.1)

    # Search strings belong inside the provided answer area, not above two
    # extremely shallow empty boxes in the source layout.
    for n,mask_y,mask_h,box_y,box_w in [(58,556,80,563,450.5),(84,418,84,426,466)]:
        query=[o[4] for o in b.ops[n] if o[4].startswith('("')][0]
        drop(n,lambda o:o[4]==query)
        bx=72.4 if n==58 else 64.65
        b.put(n,bx-2,mask_y,box_w+4,mask_h,'',9,True)
        b.put(n,bx,box_y,box_w,66,'__BOX__',9)
        b.put(n,bx+8,box_y+16,box_w-16,40,query,9)

    # Keep all three theme groups within their coloured activity panel.
    drop(66,lambda o:o[4].startswith('Dataset quality:'))
    b.put(66,50,533.2,495,46,'',9,True)
    groups=[
        'Dataset quality: Tavallaee et al. (2009), duplicate analysis; NSL-KDD.',
        'Modern traffic: Moustafa & Slay (2015), generated flows/UNSW-NB15; Sharafaldin et al. (2018), flow features/CICIDS2017.',
        'Autoencoders: Mirsky et al. (2018), online ensemble/KitNET; Meidan et al. (2018), deep models/N-BaIoT.'
    ]
    for y,text in zip([535,550,565],groups):
        b.put(66,54,y,487,12,text,7.8)
        b.put(66,51.13,y+12,493,0,'__RULE__',9)

    # Put publication-ethics answers in the Issue column and wrap the supplied
    # situations within their own column, keeping all five questions verbatim.
    drop(80,lambda o:True)
    b.put(80,42.5,324,510.3,182.2,'',9,True)
    label(80,50,331,335,'Situation',10,True);label(80,420,331,124,'Issue',10,True)
    b.put(80,43,349,509,0,'__RULE__',9)
    situations=[
        '1. The same manuscript is submitted simultaneously to two conferences.',
        '2. A friend is added as an author without contribution.',
        '3. A negative experimental result is hidden.',
        '4. A dataset is used without checking its provenance.',
        '5. A collaborator\'s major contribution is not acknowledged.'
    ]
    issues=['Simultaneous submission.','Gift authorship.','Selective reporting.','Unverified provenance; privacy misuse.','Ghost authorship / missing credit.']
    for i,(question,answer) in enumerate(zip(situations,issues)):
        y=353+i*30.2
        label(80,50,y,347,question,9.1)
        b.put(80,420,y,125,26,answer,8.3)
        b.put(80,43,y+27,509,0,'__RULE__',9)

    # Include paper identities in the existing header row, not on its border.
    drop(85,lambda o:o[4] in ['Moustafa & Slay (2015)','Sharafaldin et al. (2018)'])
    b.put(85,44,110,507,24,'',9,True)
    label(85,151,119,188,'Paper 1: Moustafa & Slay (2015)',8.4,True)
    label(85,359,119,182,'Paper 2: Sharafaldin et al. (2018)',8.4,True)

    # The original validation options are also selections, so tick them.
    drop(45,lambda o:o[4].startswith('Selected:'))
    b.check(45,184.7,693.2)
    b.check(45,267.3,693.2)

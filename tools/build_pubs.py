import re, math, colorsys, os

# paths are resolved relative to this script so it runs from anywhere: `python3 tools/build_pubs.py`
HERE = os.path.dirname(os.path.abspath(__file__))          # the tools/ directory
ROOT = os.path.dirname(HERE)                                # repo root (one level up)

# per-year colour ramp: a violet->magenta->red->amber "sunset", held at constant
# perceived luminance so every label stays legible on BOTH the light and dark themes
def _year_ramp(years, h0=252, h1=392, S=0.60, target=0.21):
    def _lum(r,g,b):
        f=lambda u:(u/12.92 if u<=0.03928 else ((u+0.055)/1.055)**2.4)
        return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
    cols={}; n=len(years)
    for i,y in enumerate(years):
        h=((h0+(h1-h0)*i/(n-1))%360)/360.0
        lo,hi=0.0,1.0
        for _ in range(40):
            L=(lo+hi)/2; r,g,b=colorsys.hls_to_rgb(h,L,S)
            if _lum(r,g,b)<target: lo=L
            else: hi=L
        r,g,b=colorsys.hls_to_rgb(h,(lo+hi)/2,S)
        cols[y]='#%02X%02X%02X'%(round(r*255),round(g*255),round(b*255))
    return cols
YEARS=list(range(2016,2027))
YEAR_COLORS=_year_ramp(YEARS)

FIG = open(os.path.join(HERE, 'kenji_lee_trajectory_figure.html'), encoding='utf-8').read()
PUB = open(os.path.join(ROOT, 'publications.html'), encoding='utf-8').read()  # existing page: nav + footer are lifted from it

svg_raw = re.search(r'<svg\b.*?</svg>', FIG, re.S).group(0)
svg_raw = svg_raw.replace('Cell-type methods', 'Cell types &amp; methods')
talks = re.search(r'<h2>Conference talks.*?</table>', FIG, re.S).group(0)
talks = talks.replace('<span class="stream" style="background:#1D9E75"></span>Cell-type &times; Primate', '<span class="stream" style="background:#1D9E75"></span>Primate').replace('Cell-type', 'Cell types')
# recolour talk years with the same per-year gradient pill (skip the year-less "upcoming" row)
talks = re.sub(r'<td class="yr">(\d{4})</td>', lambda m: '<td class="yr"><span class="stat yr%s">%s</span></td>'%(m.group(1),m.group(1)) if int(m.group(1)) in YEAR_COLORS else m.group(0), talks)
# the Rutgers seminar and Gordon Research Seminar move to the new "Invited talks & seminars" grouping below
for _kw in ['Cell type-informed dynamical systems','Manifolds for identification of cell types']:
    talks = re.sub(r'<tr>(?:(?!</tr>).)*?'+re.escape(_kw)+r'(?:(?!</tr>).)*?</tr>', '', talks, flags=re.S)
STREAMS={'cell':('Cell types','#7F77DD'),'primate':('Primate','#1D9E75'),'mouse':('Mouse VC','#378ADD'),'other':('Other','#888780')}
def _stream(sk):
    if sk=='cellxprim': return '<span class="stream stream-split"></span>Cell types &times; Primate'
    if sk=='cellxmouse': return '<span class="stream stream-split-cm"></span>Cell types &times; Mouse VC'
    lbl,col=STREAMS[sk]; return '<span class="stream" style="background:%s"></span>%s'%(col,lbl)
# actual titles (from the pre-rebuild page / Google Scholar); Wyrick preprint added
PUBS_DATA=[
 ('sPrep','in prep (writing)','Population dynamics during mnemonic working memory are structured by a single inhibitory cell type.','&mdash;','r1','First','cellxprim'),
 ('sPrep','in prep (analysis)','The computational geometry of flexible decision-making in prefrontal cortex.','&mdash;','r1','First','primate'),
 ('sPrep','in prep (writing)','Prefrontal neural dynamics underlying abstract perceptual decisions.','&mdash;','r1','First','primate'),
 ('sPre','in submission','Multimodal characterization of pan-inhibitory enhancers for assessing inhibitory neuron function in macaque monkeys.','&mdash;','r3','Co-author','cellxprim'),
 ('sPre','2026 pre','Distinct neural dynamics in prefrontal and premotor cortex during flexible perceptual decisions.','bioRxiv','r2','Second','primate'),
 ('sPub','2026','A multimodal approach for visualizing and identifying electrophysiological cell types in vivo.','Nature Communications','r1','First','cellxmouse'),
 ('sPub','2026','Neuropixels reveal laminar microcircuit organization in monkey V1 in vivo.','PNAS','r3','Co-author','primate'),
 ('sPub','2025','In vivo cell-type and brain region classification via multimodal contrastive learning.','ICLR (Spotlight)','r3','Co-author','cell'),
 ('sPub','2024','Responses to pattern-violating visual stimuli evolve differently over days in somata and distal apical dendrites.','J. Neuroscience','r3','Co-author','mouse'),
 ('sPre','2023 pre','Differential encoding of temporal context and expectation under representational drift across hierarchically connected areas.','bioRxiv','r3','Co-author','mouse'),
 ('sPub','2023','WaveMAP for identifying putative cell types from in vivo electrophysiology.','STAR Protocols','r1','First','cell'),
 ('sPub','2023','A cortical information bottleneck during decision-making.','eLife','r3','Co-author','primate'),
 ('sPub','2023','A whole-brain monosynaptic input connectome to neuron classes in mouse visual cortex.','Nature Neuroscience','r3','Co-author','mouse'),
 ('sPub','2023','Responses of pyramidal cell somata and apical dendrites in mouse visual cortex over multiple days.','Scientific Data','r3','Co-author','mouse'),
 ('sPub','2022','A standardized nonvisual behavioral event is broadcasted homogeneously across cortical visual areas without modulating visual responses.','eNeuro','r2','Second','mouse'),
 ('sPub','2022','Measuring stimulus-evoked neurophysiological differentiation in distinct populations of neurons in mouse visual cortex.','eNeuro','r3','Co-author','mouse'),
 ('sPub','2021','Non-linear dimensionality reduction on extracellular waveforms reveals cell type diversity in premotor cortex.','eLife','r1','First','cell'),
 ('sPub','2020','A large-scale standardized physiological survey reveals functional organization of the mouse visual cortex.','Nature Neuroscience','r3','Co-author','mouse'),
 ('sPub','2020','VIP interneurons in mouse primary visual cortex selectively enhance responses to weak but specific stimuli.','eLife','r3','Co-author','mouse'),
 ('sPub','2019','Biological variation in the sizes, shapes and locations of visual cortical areas in the mouse.','PLOS ONE','r2','Second','mouse'),
 ('sPub','2017','Aberrant cortical activity in multiple GCaMP6-expressing transgenic mouse lines.','eNeuro','r3','Co-author','mouse'),
 ('sPub','2017','Neuropathological and transcriptomic characteristics of the aged brain.','eLife','r3','Co-author','other'),
 ('sPub','2016','Low-dose exposure to Bisphenol A alters development of gonadotropin-releasing hormone 3 neurons and larval locomotor behavior in Japanese Medaka.','NeuroToxicology','r3','Co-author','other'),
]
def _statpill(sc,sl):
    # colour the pill by its year (matches the plot's year gradient); rows with no year (in prep) stay neutral
    m=re.search(r'(\d{4})', sl)
    if m and int(m.group(1)) in YEAR_COLORS: return '<span class="stat yr%s">%s</span>'%(m.group(1),sl)
    return '<span class="stat %s">%s</span>'%(sc,sl)
_rows=''.join('<tr><td class="yr">%s</td><td>%s</td><td>%s</td><td><span class="role %s">%s</span></td><td>%s</td></tr>'%(_statpill(sc,sl),t,v,rc,rl,_stream(sk)) for (sc,sl,t,v,rc,rl,sk) in PUBS_DATA)
pubs='<h2>Publications</h2>\n      <table>\n        <thead><tr><th>Year / status</th><th>Paper</th><th>Venue</th><th>Role</th><th>Stream</th></tr></thead>\n        <tbody>'+_rows+'</tbody>\n      </table>'
nav   = re.search(r'<header class="nav">.*?</header>', PUB, re.S).group(0)
foot  = re.search(r'<footer class="footer">.*?</footer>', PUB, re.S).group(0)

# wrap each table so it scrolls horizontally on narrow screens instead of overflowing the page
talks = talks.replace('<table>', '<div class="tbl-wrap"><table>', 1).replace('</table>', '</table></div>', 1)
pubs  = pubs.replace('<table>', '<div class="tbl-wrap"><table>', 1).replace('</table>', '</table></div>', 1)

# ---- Invited talks & seminars (hand-curated; folds in the Rutgers & Gordon talks) ----
# (year, host/group, institution or series, format)
INVITED=[
 ('2026','Gordon Research Seminar','Neurobiology of Cognition','person'),
 ('2026','Steinmetz Lab','University of Washington','person'),
 ('2026','Sainsbury Wellcome Centre','University College London','person'),
 ('2026','Rutishauser Lab','Caltech &amp; Cedars-Sinai','virtual'),
 ('2024','Center for Molecular &amp; Behavioral Neuroscience','Rutgers University','person'),
 ('2024','Varol Lab','New York University','virtual'),
 ('2021','Shadmehr Lab','Johns Hopkins University','virtual'),
 ('2021','Svoboda Lab','Janelia Research Campus','virtual'),
 ('2021','Valiante Lab','University of Toronto','virtual'),
 ('2021','Brain Observatory Group','Allen Institute for Brain Science','virtual'),
]
def _fmt(f):
    return {'person':'<span class="fmt fmt-person">In person</span>',
            'virtual':'<span class="fmt fmt-virtual">Virtual</span>',
            'upcoming':'<span class="fmt fmt-soon">Upcoming</span>'}.get(f,'<span class="host-sub">&mdash;</span>')
_inv_rows=''.join('<tr><td class="yr"><span class="stat yr%s">%s</span></td><td><strong>%s</strong><div class="host-sub">%s</div></td><td>%s</td></tr>'%(y,y,host,inst,_fmt(f)) for (y,host,inst,f) in INVITED)
invited='<h2>Invited talks &amp; seminars</h2>\n      <div class="tbl-wrap"><table>\n        <thead><tr><th>Year</th><th>Host</th><th>Format</th></tr></thead>\n        <tbody>'+_inv_rows+'</tbody>\n      </table></div>'
talks = invited+'\n          '+talks

# dark-mode toggle button in the nav + FOUC-preventing theme init
NAV_BTN = ('<button class="theme-toggle" type="button" aria-label="Toggle dark mode" title="Toggle dark mode" aria-pressed="false">\n'
'          <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>\n'
'          <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>\n'
'        </button>')
nav = re.sub(r'\s*<button class="theme-toggle".*?</button>', '', nav, flags=re.S)  # strip any already-injected toggle (idempotent)
nav = nav.replace('</nav>', '</nav>\n        '+NAV_BTN, 1)
FOUC = "<script>(function(){try{var t=localStorage.getItem('theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>"

# ---- horizontal svg (desktop): strip the "hover a point for details" hint, tag it ----
svg_h = re.sub(r'<text[^>]*>hover a point for details</text>\s*', '', svg_raw)
# drop the "In prep / upcoming" legend entry (its meaning is clear from the far-right "in pipeline" band)
svg_h = re.sub(r'<polygon points="415,22[^>]*>\s*<text[^>]*>In prep / upcoming</text>\s*', '', svg_h)
svg_h = svg_h.replace('<svg ', '<svg class="traj-horiz" ', 1)
svg_h = svg_h.replace('Cell-type methods', 'Cell types &amp; methods')
# colour-code each year: tint the axis label and add a short colour tick beneath the axis
YEAR_X={int(m.group(2)):float(m.group(1)) for m in re.finditer(r'<text class="lm" x="([\d.]+)" y="437"[^>]*>(\d{4})</text>', svg_h)}
def _coloryr(m):
    c=YEAR_COLORS.get(int(m.group(2)),'#8a887f')
    return '%s style="fill:%s;font-weight:600">%s</text>'%(m.group(1),c,m.group(2))
svg_h = re.sub(r'(<text class="lm" x="[\d.]+" y="437"[^>]*)>(\d{4})</text>', _coloryr, svg_h)
_ticks=''.join('<line x1="%.1f" y1="444" x2="%.1f" y2="444" stroke="%s" stroke-width="2.6" stroke-linecap="round"/>'%(x-9,x+9,YEAR_COLORS.get(y,'#8a887f')) for y,x in YEAR_X.items())
svg_h = svg_h.replace('</svg>', _ticks+'</svg>')

# ---- vertical svg (mobile): transpose every marker (years->y down, streams->columns) ----
def star(cx, cy, ro=7.0, ri=2.9):
    pts=[]
    for k in range(10):
        ang=-math.pi/2+k*math.pi/5; r=ro if k%2==0 else ri
        pts.append("%.1f,%.1f"%(cx+r*math.cos(ang), cy+r*math.sin(ang)))
    return " ".join(pts)

markers=[]
for m in re.finditer(r'<circle\s+cx="([\d.]+)"\s+cy="([\d.]+)"\s+r="([\d.]+)"\s+fill="([^"]+)"(?:\s+fill-opacity="([\d.]+)")?(?:\s+stroke="([^"]+)")?(?:\s+stroke-width="([\d.]+)")?\s*><title>(.*?)</title></circle>', svg_raw, re.S):
    cx,cy,r,fill,fo,stroke,sw,title=m.groups()
    markers.append(dict(kind='circle',cx=float(cx),cy=float(cy),r=r,fill=fill,fo=fo,stroke=stroke or 'none',sw=sw or '1',title=title))
for m in re.finditer(r'<polygon\s+points="([^"]+)"\s+fill="([^"]+)"(?:\s+fill-opacity="([\d.]+)")?\s+stroke="([^"]+)"\s+stroke-width="([\d.]+)"\s*><title>(.*?)</title></polygon>', svg_raw, re.S):
    p,fill,fo,stroke,sw,title=m.groups(); xs=[];ys=[]
    for pr in p.split():
        x,y=pr.split(','); xs.append(float(x)); ys.append(float(y))
    markers.append(dict(kind='star',cx=(min(xs)+max(xs))/2,cy=(min(ys)+max(ys))/2,fill=fill,fo=fo,stroke=stroke,sw=sw,title=title))

def stream_of(cy):
    return 'cell' if cy<150 else 'primate' if cy<215 else 'mouse' if cy<300 else 'early' if cy<360 else 'talks'
centers={'cell':118,'primate':190,'mouse':262,'early':332,'talks':392}
colx={'cell':92,'primate':158,'mouse':230,'early':292,'talks':340}
def yeary(y): return 121+(y-2016)*43
SUB=15; band_top=626; band_step=30
for mk in markers:
    mk['stream']=stream_of(mk['cy']); mk['pipeline']=mk['cx']>=574
    mk['year']=2016+round((mk['cx']-155)/40.5)
    d=mk['cy']-centers[mk['stream']]; mk['sub']=-1 if d<-4 else (1 if d>4 else 0)
from collections import defaultdict
pgp=defaultdict(list)
for mk in sorted([m for m in markers if m['pipeline']], key=lambda m:m['cx']): pgp[mk['stream']].append(mk)
for st,lst in pgp.items():
    for i,mk in enumerate(lst): mk['vx']=colx[st]; mk['vy']=band_top+i*band_step
for mk in markers:
    if not mk['pipeline']: mk['vx']=colx[mk['stream']]+mk['sub']*SUB; mk['vy']=yeary(mk['year'])

V=['<svg class="traj-vert" viewBox="0 0 370 752" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Vertical timeline of publications and talks, 2016 to 2026. Filled markers are first-author papers and invited talks; open markers are co-authored work and contributed talks.">']
# marker-encoding legend (filled = first author / invited talk; open = co-author / contributed)
V.append('<polygon points="%s" fill="#888780" stroke="#5F5E5A" stroke-width="1"/>'%star(72,16,6,2.5))
V.append('<text x="83" y="20" font-size="10.5" class="lm">First author</text>')
V.append('<circle cx="205" cy="16" r="5" fill="#888780" fill-opacity="0.22" stroke="#5F5E5A" stroke-width="1.4"/>')
V.append('<text x="216" y="20" font-size="10.5" class="lm">Co-author</text>')
V.append('<circle cx="72" cy="37" r="5" fill="#888780" stroke="#5F5E5A" stroke-width="1"/>')
V.append('<text x="83" y="41" font-size="10.5" class="lm">Invited talk</text>')
V.append('<circle cx="205" cy="37" r="5" fill="none" stroke="#5F5E5A" stroke-width="1.6"/>')
V.append('<text x="216" y="41" font-size="10.5" class="lm">Contributed</text>')
V.append('<rect x="58" y="588" width="304" height="152" rx="10" fill="#888780" fill-opacity="0.06"/>')
V.append('<text x="362" y="612" font-size="10" text-anchor="end" font-style="italic" class="lm">in pipeline</text>')
for y in range(2016,2027):
    yy=yeary(y); yc=YEAR_COLORS.get(y,'#888780')
    V.append('<line x1="58" y1="%d" x2="362" y2="%d" stroke="%s" stroke-opacity="0.32" stroke-width="1"/>'%(yy,yy,yc))
    V.append('<text x="46" y="%.1f" font-size="11" text-anchor="end" class="lm" style="fill:%s;font-weight:600">%d</text>'%(yy+3.5,yc,y))
for st,lbl,col in [('cell','Cell types','#7F77DD'),('primate','Primate','#1D9E75'),('mouse','Mouse VC','#378ADD'),('early','Early','#888780'),('talks','Talks','#5F5E5A')]:
    x=colx[st]
    V.append('<rect x="%.1f" y="60" width="10" height="10" rx="2" fill="%s"/>'%(x-5,col))
    V.append('<text x="%.1f" y="86" font-size="10" text-anchor="middle" font-weight="600" class="lt">%s</text>'%(x,lbl))
for mk in markers:
    fo=' fill-opacity="%s"'%mk['fo'] if mk['fo'] else ''; t='<title>%s</title>'%mk['title']
    if mk['kind']=='circle':
        V.append('<circle cx="%.1f" cy="%.1f" r="%s" fill="%s"%s stroke="%s" stroke-width="%s">%s</circle>'%(mk['vx'],mk['vy'],mk['r'],mk['fill'],fo,mk['stroke'],mk['sw'],t))
    else:
        V.append('<polygon points="%s" fill="%s"%s stroke="%s" stroke-width="%s">%s</polygon>'%(star(mk['vx'],mk['vy']),mk['fill'],fo,mk['stroke'],mk['sw'],t))
V.append('</svg>')
svg_v='\n            '.join(V)

CSS = r'''
    .traj{max-width:940px;margin:0 auto}
    .traj-fig{background:#fff;border:1px solid var(--faint);border-radius:16px;padding:20px 20px 16px;box-shadow:var(--shadow)}
    .traj-fig svg{width:100%;height:auto;display:block}
    .traj-fig svg text{font-family:var(--sans)}
    .traj-fig .lt{fill:var(--ink)} .traj-fig .lm{fill:#8a887f}
    .traj-fig .mk{cursor:pointer}
    .traj-fig .mk:focus{outline:none}
    .traj-fig .mk.sel{stroke-width:2.8;filter:drop-shadow(0 0 3px var(--accent)) drop-shadow(0 0 6px var(--accent))}
    .traj-fig svg.traj-horiz{display:block} .traj-fig svg.traj-vert{display:none;max-width:380px;margin:0 auto}
    @media (max-width:640px){ .traj-fig svg.traj-horiz{display:none} .traj-fig svg.traj-vert{display:block} }
    .traj-detail{background:#fff;border:1px solid var(--faint);border-radius:16px;padding:18px 22px;box-shadow:var(--shadow);margin-top:16px;min-height:112px;display:flex;flex-direction:column;justify-content:center;transition:border-color .15s ease}
    .traj-detail.empty{display:none}
    .traj-detail.active{border-color:var(--accent)}
    .traj-detail h3{margin:0 0 6px;font-family:var(--sans);font-size:1.06rem;line-height:1.4;color:var(--ink);font-weight:650}
    .traj-detail .meta{color:var(--muted);font-size:.9rem;line-height:1.5}
    .traj-detail .tr-auth{color:var(--muted);font-size:.84rem;line-height:1.45;margin:2px 0 0}
    .traj-detail .tr-auth b{color:var(--ink);font-weight:650}
    .traj-detail .tr-abs{color:var(--ink);font-size:.9rem;line-height:1.55;margin-top:11px;opacity:.9}
    .traj-badge{display:inline-block;font-size:.68rem;font-weight:700;letter-spacing:.03em;padding:3px 10px;border-radius:20px;margin-bottom:9px;text-transform:uppercase}
    .traj-badge.b-prep,.traj-badge.b-up{background:#eeedfe;color:#3C3489}
    .traj-badge.b-pre,.traj-badge.b-inv{background:#faeeda;color:#854F0B}
    .traj-badge.b-con{background:#f1efe8;color:#5F5E5A}
    .traj-badge.b-pub{background:#e1f5ee;color:#0F6E56}
    .traj-detail .links{margin-top:13px;display:flex;gap:9px;flex-wrap:wrap}
    .traj-detail .links a{font-size:.82rem;font-weight:600;color:var(--accent-deep);border:1px solid var(--faint);border-radius:999px;padding:5px 13px;background:#fff}
    .traj-detail .links a:hover{border-color:var(--accent);text-decoration:none}
    .traj-card{background:#fff;border:1px solid var(--faint);border-radius:16px;padding:18px 20px 8px;box-shadow:var(--shadow);margin-top:22px}
    .traj-card h2{font-family:var(--sans);font-size:.95rem;font-weight:700;margin:0 0 10px;color:var(--ink)}
    .traj .tbl-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
    .pub-head{padding-bottom:14px}
    .traj table{width:100%;border-collapse:collapse;font-size:.85rem}
    .traj th,.traj td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--faint);vertical-align:top}
    .traj tbody tr:last-child td{border-bottom:0}
    .traj td.yr{color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums}
    .traj th{color:var(--muted);font-weight:600;font-size:.7rem;text-transform:uppercase;letter-spacing:.4px}
    .traj .role{display:inline-block;font-size:.7rem;padding:2px 9px;border-radius:20px;white-space:nowrap;font-weight:600}
    .traj .role.r1{background:#efedfe;color:#3C3489} .traj .role.r2,.traj .role.r3{background:#f1efe8;color:#444441}
    .traj .stream{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:7px;vertical-align:-1px}
    .traj .stream.stream-split,.traj .stream.stream-split-cm{width:11px;height:11px;vertical-align:-2px}
    .traj .stream.stream-split{background:linear-gradient(135deg,#7F77DD 0 44%,#fff 44% 56%,#1D9E75 56% 100%)}
    .traj .stream.stream-split-cm{background:linear-gradient(135deg,#7F77DD 0 44%,#fff 44% 56%,#378ADD 56% 100%)}
    .traj .stat{display:inline-block;font-size:.68rem;padding:2px 8px;border-radius:6px;white-space:nowrap;font-weight:600}
    .traj .stat.sPub{background:#e1f5ee;color:#0F6E56} .traj .stat.sPre{background:#faeeda;color:#854F0B} .traj .stat.sPrep{background:#eeedfe;color:#3C3489}
    .traj .stat.tInv{background:#faeeda;color:#854F0B} .traj .stat.tCon{background:#f1efe8;color:#5F5E5A} .traj .stat.tUp{background:#eeedfe;color:#3C3489}
    @media (max-width:600px){ .traj th:nth-child(5),.traj td:nth-child(5){display:none} .traj th,.traj td{padding:8px 7px} .traj .tbl-wrap table{min-width:470px} }
    html[data-theme="dark"] .traj-fig, html[data-theme="dark"] .traj-detail, html[data-theme="dark"] .traj-card{background:var(--paper-2)}
    html[data-theme="dark"] .traj-fig .lm{fill:#9aa3b1}
    html[data-theme="dark"] .traj-detail .links a{background:transparent}
    html[data-theme="dark"] .traj-badge.b-prep,html[data-theme="dark"] .traj-badge.b-up{background:#26215C;color:#CECBF6}
    html[data-theme="dark"] .traj-badge.b-pre,html[data-theme="dark"] .traj-badge.b-inv{background:#412402;color:#EF9F27}
    html[data-theme="dark"] .traj-badge.b-con{background:#2C2C2A;color:#D3D1C7}
    html[data-theme="dark"] .traj-badge.b-pub{background:#04342C;color:#5DCAA5}
    html[data-theme="dark"] .traj .role.r1{background:#26215C;color:#CECBF6}
    html[data-theme="dark"] .traj .role.r2,html[data-theme="dark"] .traj .role.r3{background:#2C2C2A;color:#D3D1C7}
    html[data-theme="dark"] .traj .stat.sPub{background:#04342C;color:#5DCAA5}
    html[data-theme="dark"] .traj .stat.sPre{background:#412402;color:#EF9F27}
    html[data-theme="dark"] .traj .stat.sPrep{background:#26215C;color:#CECBF6}
    html[data-theme="dark"] .traj .stat.tInv{background:#412402;color:#EF9F27}
    html[data-theme="dark"] .traj .stat.tCon{background:#2C2C2A;color:#B4B2A9}
    html[data-theme="dark"] .traj .stat.tUp{background:#26215C;color:#CECBF6}
'''

# per-year tinted pills for the Year columns (echoes the plot's year gradient), light + dark variants
def _hx(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
def _mix(a,b,t): x=_hx(a); y=_hx(b); return '#%02X%02X%02X'%tuple(round(x[i]+(y[i]-x[i])*t) for i in range(3))
_year_css='\n    '.join('.traj .stat.yr%d{background:%s;color:%s} html[data-theme="dark"] .traj .stat.yr%d{background:%s;color:%s}'%(
    y,_mix(YEAR_COLORS[y],"#ffffff",0.86),YEAR_COLORS[y],
    y,_mix(YEAR_COLORS[y],"#0f1216",0.80),_mix(YEAR_COLORS[y],"#ffffff",0.38)) for y in YEARS)
_fmt_css = ('.traj .host-sub{color:var(--muted);font-size:.78rem;margin-top:2px}\n'
'    .traj .fmt{display:inline-block;font-size:.68rem;padding:2px 8px;border-radius:6px;white-space:nowrap;font-weight:600}\n'
'    .traj .fmt-person{background:#eef1f4;color:#48515e}\n'
'    .traj .fmt-virtual{background:#e7f0fb;color:#1d4ed8}\n'
'    .traj .fmt-soon{background:#eeedfe;color:#3C3489}\n'
'    html[data-theme="dark"] .traj .fmt-person{background:#2a2f37;color:#c2ccd8}\n'
'    html[data-theme="dark"] .traj .fmt-virtual{background:#12294d;color:#9dbcff}\n'
'    html[data-theme="dark"] .traj .fmt-soon{background:#26215C;color:#CECBF6}\n')
CSS = CSS + '\n    ' + _year_css + '\n    ' + _fmt_css + '\n'

JS = r'''
  (function(){
    var panel = document.getElementById('pub-detail');
    if(!panel) return;
    var LINKS = {
      'WaveMAP — cell type diversity': [['Paper','https://elifesciences.org/articles/67490'],['Code','https://github.com/EricKenjiLee/WaveMAP_Paper']],
      'WaveMAP for identifying putative cell types from extracellular': [['Paper','https://pubmed.ncbi.nlm.nih.gov/37220000/']],
      'PhysMAP': [['Preprint','https://www.biorxiv.org/content/10.1101/2025.07.24.666654v1'],['Code','https://github.com/EricKenjiLee/PhysMAP_Manuscript']]
    };
    var EXTRA = {
      'cell type diversity via nonlinear':{a:'Lee, E.K., Balasubramanian, H., Tsolias, A., Anakwe, S.U., Medalla, M., et al.',s:'Applies nonlinear dimensionality reduction (UMAP) and graph-based clustering to extracellular spike waveforms, revealing more putative cell-type classes in primate premotor cortex than the classic narrow/broad split.'},
      'for identifying putative cell types from extracellular':{a:'Lee, E.K., Carr, N., Perliss, A., & Chandrasekaran, C.',s:'A step-by-step protocol for running WaveMAP end-to-end to identify putative cell types from in vivo extracellular electrophysiology.'},
      'multimodal contrastive learning':{a:'Yu, H., Lyu, H., Xu, E.Y., Windolf, C., Lee, E.K., Yang, F., Shelton, A.M., Olsen, S., et al.',s:'Uses multimodal contrastive learning to classify neuronal cell types and brain regions directly from in vivo electrophysiology.'},
      'PhysMAP':{a:'Lee, E.K., Gül, A.E., Heller, G., Lakunina, A., Yu, H., Shelton, A., Olsen, S., et al.',s:'Fuses several electrophysiological modalities (waveform, autocorrelogram, and more) into one embedding to visualize and identify cell types in vivo, improving on single-feature methods.'},
      'pan-inhibitory enhancers':{a:'Medalla, M., Boucher, P., …, Lee, E.K., et al.',s:'Characterizes viral enhancer tools for labeling and assessing the function of inhibitory neurons in the macaque cortex.'},
      'cortical information bottleneck':{a:'Kleinman, M., Wang, T., Xiao, D., Feghhi, E., Lee, E.K., Carr, N., Li, Y., Hadidi, N., et al.',s:'Finds that prefrontal population activity compresses sensory information into a low-dimensional bottleneck aligned with the upcoming decision.'},
      'laminar microcircuit organization':{a:'Carr, N., Zhu, S., Chen, X., Lee, E.K., Perliss, A., Moore, T., & Chandrasekaran, C.',s:'Uses Neuropixels recordings to map the laminar microcircuit organization of primary visual cortex in the behaving monkey.'},
      'prefrontal and premotor cortex underlie':{a:'Wang, T., Lee, E.K., Carr, N., Li, Y., & Chandrasekaran, C.',s:'Contrasts how prefrontal and premotor cortex represent and transform sensory evidence during flexible perceptual decisions.'},
      'computational geometry of flexible':{a:'Lee, E.K.*, Wang, T.*, Carr, N., Boucher, P., Wang, M., & Chandrasekaran, C.',s:'Shows how dorsolateral prefrontal cortex (DLPFC) encodes the same task variables in orthogonal subspaces across multiple related tasks.'},
      'abstract perceptual decisions':{a:'Lee, E.K.*, Umaguing, M.*, Wang, T., Carr, N., & Chandrasekaran, C.',s:'Studies how prefrontal cortex computes abstract perceptual decisions, composed of perceptual evidence accumulation and holding that information in working memory, divorced from specific actions.'},
      'mnemonic working memory are structured':{a:'Lee, E.K., Wang, T., & Chandrasekaran, C.',s:'Links prefrontal working-memory population dynamics to the activity of a single inhibitory cell type.'},
      'Aberrant cortical activity in GCaMP6':{a:'Steinmetz, N.A., Buetfering, C., Lecoq, J., … Lee, E.K. … et al.',s:'Documents epileptiform cortical activity in several widely used GCaMP6 transgenic mouse lines, a caution for calcium-imaging studies.'},
      'sizes, shapes and locations of visual cortical':{a:'Waters, J., Lee, E.K., Gaudreault, N., Griffin, F., Lecoq, J., Slaughterbeck, C., et al.',s:'Quantifies mouse-to-mouse variability in the size, shape, and location of visual cortical areas.'},
      'Allen Brain Observatory':{a:'de Vries, S.E.J., Lecoq, J.A., Buice, M.A., Groblewski, P.A., … Lee, E.K. … et al.',s:'The Allen Brain Observatory: a large-scale, standardized two-photon survey of visual responses across mouse cortical areas, layers, and Cre lines.'},
      'VIP interneurons enhance responses':{a:'Millman, D.J., Ocker, G.K., Caldejon, S., Larkin, J.D., Lee, E.K., Luviano, J., et al.',s:'Shows VIP interneurons selectively enhance mouse V1 responses to weak but specific visual stimuli.'},
      'standardized behavioral event equally impacts':{a:'Ramadan, M., Lee, E.K., de Vries, S., Caldejon, S., Roll, K., Griffin, F., et al.',s:'A stereotyped non-visual behavioral event is broadcast uniformly across mouse visual areas and layers without changing visual tuning.'},
      'neurophysiological differentiation':{a:'Mayner, W.G.P., Marshall, W., Billeh, Y.N., Gandhi, S.R., … Lee, E.K. … et al.',s:'Introduces and applies a measure of stimulus-evoked neural differentiation across populations in mouse visual cortex.'},
      'monosynaptic input connectome':{a:'Yao, S., Wang, Q., Hirokawa, K.E., Ouellette, B., … Lee, E.K. … et al.',s:'Maps brain-wide monosynaptic inputs onto defined neuron classes in mouse visual cortex using viral tracing.'},
      'apical dendrite responses in mouse V1 over days':{a:'Gillon, C.J., Lecoq, J.A., Pina, J.E., … Lee, E.K. … et al.',s:'A public two-photon dataset of pyramidal-cell somata and apical-dendrite responses tracked over multiple days.'},
      'Pattern-violating visual stimuli in somata':{a:'Gillon, C.J., Pina, J.E., Lecoq, J.A., … Lee, E.K. … et al.',s:'Finds that responses to unexpected (pattern-violating) stimuli evolve differently over days in somata versus distal apical dendrites.'},
      'Bisphenol A alters GnRH3':{a:'Inagaki, T., Smith, N., Lee, E.K., & Ramakrishnan, S.',s:'Low-dose Bisphenol A exposure disrupts GnRH3 neuron development and larval locomotor behavior in medaka fish (undergraduate work).'},
      'characteristics of the aged brain':{a:'Miller, J.A., Guillozet-Bongaarts, A., Gibbons, L.E., Postupna, N., … Lee, E.K. … et al.',s:'Relates neuropathology and transcriptomics to cognitive status in aged human brains (the Aging, Dementia & TBI study).'}
    };
    function esc(s){ var d=document.createElement('div'); d.textContent=s; return d.innerHTML; }
    function render(blurb){
      var kind='', bl=blurb;
      var m=/^(IN PREP(?: \((?:WRITING|ANALYSIS)\))?|IN SUBMISSION|PREPRINT|UPCOMING|INVITED(?: panel| talk)?|CONTRIBUTED(?: talk)?)\s*:?\s*/i.exec(blurb);
      if(m){ kind=m[1].toUpperCase(); bl=blurb.slice(m[0].length); }
      var title, meta, m2=/\.["'”]?\s+/.exec(bl);
      if(m2){ var q=(m2[0].match(/["'”]/)||[''])[0]; title=bl.slice(0,m2.index)+q; meta=bl.slice(m2.index+m2[0].length); }
      else { title=bl; meta=''; }
      var bt='',bc='';
      if(/IN PREP/.test(kind)||/in prep/i.test(meta)){bt=/WRITING/.test(kind)?'In prep (writing)':/ANALYSIS/.test(kind)?'In prep (analysis)':'In preparation';bc='b-prep';}
      else if(/IN SUBMISSION/.test(kind)||/in submission/i.test(meta)){bt='In submission';bc='b-pre';}
      else if(/PREPRINT/.test(kind)){bt='Preprint';bc='b-pre';}
      else if(/UPCOMING/.test(kind)){bt='Upcoming talk';bc='b-up';}
      else if(/INVITED/.test(kind)){bt='Invited talk';bc='b-inv';}
      else if(/CONTRIBUTED/.test(kind)){bt='Talk';bc='b-con';}
      else if(/Published/.test(meta)){bt='Published';bc='b-pub';}
      var links='';
      for(var key in LINKS){ if(blurb.indexOf(key)>=0){ links=LINKS[key].map(function(l){return '<a href="'+l[1]+'" target="_blank" rel="noopener">'+l[0]+'</a>';}).join(''); break; } }
      var extra=null;
      for(var ek in EXTRA){ if(blurb.indexOf(ek)>=0){ extra=EXTRA[ek]; break; } }
      var metaDisp = meta.replace(/\s+$/,'').replace(/\.$/,'').replace(/(\w{2,}|\))\.\s+/g,'$1 · ');
      if(bt){ metaDisp = metaDisp.replace(new RegExp('\\s*·?\\s*'+bt+'\\s*$','i'),''); }
      var auth = (extra&&extra.a) ? '<div class="tr-auth">'+esc(extra.a).replace(/Lee, E\.K\./g,'<b>Lee, E.K.</b>')+'</div>' : '';
      var abst = (extra&&extra.s) ? '<div class="tr-abs">'+esc(extra.s)+'</div>' : '';
      panel.classList.remove('empty'); panel.classList.add('active');
      panel.innerHTML = (bt?'<span class="traj-badge '+bc+'">'+bt+'</span>':'')
        + '<h3>'+esc((extra&&extra.t)||title)+'</h3>'
        + auth
        + (metaDisp?'<div class="meta">'+esc(metaDisp)+'</div>':'')
        + abst
        + (links?'<div class="links">'+links+'</div>':'');
    }
    var markers=[];
    [].forEach.call(document.querySelectorAll('.traj-fig svg'), function(svg){
      [].forEach.call(svg.querySelectorAll('circle, polygon'), function(el){ if(el.querySelector('title')) markers.push(el); });
    });
    if(!markers.length) return;
    markers.forEach(function(el){
      var t=el.querySelector('title');
      var blurb=t.textContent.replace(/\s+/g,' ').trim();
      el.removeChild(t);                    /* suppress native browser tooltip */
      el.classList.add('mk'); el.setAttribute('tabindex','0'); el.setAttribute('role','button'); el.setAttribute('aria-label', blurb);
      var show=function(e){ if(e){e.preventDefault();} render(blurb); };
      el.addEventListener('mouseenter', show);
      el.addEventListener('focus', show);
    });
    // generous tap target: a click/tap anywhere in a plot selects the nearest marker
    [].forEach.call(document.querySelectorAll('.traj-fig svg'), function(svg){
      svg.addEventListener('click', function(e){
        var best=null, bd=28*28;
        [].forEach.call(svg.querySelectorAll('.mk'), function(el){
          var r=el.getBoundingClientRect(); if(!r.width) return;
          var dx=e.clientX-(r.left+r.width/2), dy=e.clientY-(r.top+r.height/2), d=dx*dx+dy*dy;
          if(d<bd){ bd=d; best=el; }
        });
        if(best){
          [].forEach.call(document.querySelectorAll('.traj-fig .mk.sel'), function(m){ m.classList.remove('sel'); });
          best.classList.add('sel');
          render(best.getAttribute('aria-label'));
        }
      });
    });
  })();
'''
# inject the actual paper titles into each EXTRA entry (detail card shows the real title)
_TITLES={
 'cell type diversity via nonlinear':'Non-linear dimensionality reduction on extracellular waveforms reveals cell type diversity in premotor cortex.',
 'for identifying putative cell types from extracellular':'WaveMAP for identifying putative cell types from in vivo electrophysiology.',
 'multimodal contrastive learning':'In vivo cell-type and brain region classification via multimodal contrastive learning.',
 'PhysMAP':'A multimodal approach for visualizing and identifying electrophysiological cell types in vivo.',
 'pan-inhibitory enhancers':'Multimodal characterization of pan-inhibitory enhancers for assessing inhibitory neuron function in macaque monkeys.',
 'cortical information bottleneck':'A cortical information bottleneck during decision-making.',
 'laminar microcircuit organization':'Neuropixels reveal laminar microcircuit organization in monkey V1 in vivo.',
 'prefrontal and premotor cortex underlie':'Distinct neural dynamics in prefrontal and premotor cortex during flexible perceptual decisions.',
 'computational geometry of flexible':'The computational geometry of flexible decision-making in prefrontal cortex.',
 'abstract perceptual decisions':'Prefrontal neural dynamics underlying abstract perceptual decisions.',
 'mnemonic working memory are structured':'Population dynamics during mnemonic working memory are structured by a single inhibitory cell type.',
 'Aberrant cortical activity in GCaMP6':'Aberrant cortical activity in multiple GCaMP6-expressing transgenic mouse lines.',
 'sizes, shapes and locations of visual cortical':'Biological variation in the sizes, shapes and locations of visual cortical areas in the mouse.',
 'Allen Brain Observatory':'A large-scale standardized physiological survey reveals functional organization of the mouse visual cortex.',
 'VIP interneurons enhance responses':'VIP interneurons in mouse primary visual cortex selectively enhance responses to weak but specific stimuli.',
 'standardized behavioral event equally impacts':'A standardized nonvisual behavioral event is broadcasted homogeneously across cortical visual areas without modulating visual responses.',
 'neurophysiological differentiation':'Measuring stimulus-evoked neurophysiological differentiation in distinct populations of neurons in mouse visual cortex.',
 'monosynaptic input connectome':'A whole-brain monosynaptic input connectome to neuron classes in mouse visual cortex.',
 'apical dendrite responses in mouse V1 over days':'Responses of pyramidal cell somata and apical dendrites in mouse visual cortex over multiple days.',
 'Pattern-violating visual stimuli in somata':'Responses to pattern-violating visual stimuli evolve differently over days in somata and distal apical dendrites.',
 'Bisphenol A alters GnRH3':'Low-dose exposure to Bisphenol A alters development of gonadotropin-releasing hormone 3 neurons and larval locomotor behavior in Japanese Medaka.',
 'characteristics of the aged brain':'Neuropathological and transcriptomic characteristics of the aged brain.',
}
for _k,_t in _TITLES.items():
    JS = JS.replace("'"+_k+"':{a:", "'"+_k+"':{t:'"+_t.replace("'","\\'")+"',a:", 1)
JS = JS.replace('more putative cell-type classes in','more putative cell types in')

HEADER_SECTION = '''    <section class="section pub-head">
      <div class="container">
        <p class="section-label">Publications</p>
        <h1>Papers, talks &amp; trajectory</h1>
        <p class="lead prose">A timeline of my scholarly output, 2016&ndash;2026, grouped into research streams:
          stars are first-author work, dots are co-authored papers and talks. Full lists follow below.</p>
        <p><a class="btn btn-outline" href="https://scholar.google.com/citations?user=9IEHT7wAAAAJ&amp;hl=en">View everything on Google&nbsp;Scholar &rarr;</a></p>
      </div>
    </section>'''

HONORS_SECTION = '''    <section class="section">
      <div class="container prose">
        <div class="pub-group">
          <h2 class="pub-year">Honors</h2>
          <ul class="olist">
            <li><div><span class="role">NIH NINDS F31 NRSA</span> <span class="org">&mdash; awarded at the 8th percentile</span></div></li>
            <li><div><span class="role">Computational Properties of Prefrontal Cortex (CPPC) Conference Travel Award</span></div></li>
            <li><div><span class="role">ETC Excellence in Mentorship Award</span></div></li>
            <li><div><span class="role">Puget Sound Research Travel Grant</span></div></li>
          </ul>
        </div>
      </div>
    </section>'''

OUT = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Publications — Eric Kenji Lee</title>
  <meta name="description" content="Publications, talks, and research trajectory of Eric Kenji Lee, 2016–2026.">
  <link rel="icon" href="assets/img/brain.ico">
  <link href="assets/css/site.css" rel="stylesheet">
  <style>%s  </style>
  %s
</head>
<body>

  %s

  <main>
%s

    <section class="section">
      <div class="container">
        <div class="traj">
          <div class="traj-fig">
            %s
            %s
          </div>
          <div class="traj-detail empty" id="pub-detail"></div>

          <div class="traj-card">
            %s
          </div>
          <div class="traj-card">
            %s
          </div>
        </div>
      </div>
    </section>

%s
  </main>

  %s

  <script src="assets/js/site.js"></script>
  <script>
%s
  </script>
</body>
</html>
''' % (CSS, FOUC, nav, HEADER_SECTION, svg_h, svg_v, pubs, talks, HONORS_SECTION, foot, JS)

open(os.path.join(ROOT, 'publications.html'),'w',encoding='utf-8').write(OUT)
print('wrote publications.html:', len(OUT), 'bytes | horiz svg:', len(svg_h), '| vert svg:', len(svg_v), '| markers:', len(markers))

#!/usr/bin/env python3
"""Render an original, self-contained animated GitHub profile from public data."""
import argparse, collections, datetime, html, json, math, pathlib, re, urllib.request
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
USER = 'ayushkapure26'

def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'AyushProfileRenderer/1.0'})
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read().decode('utf-8')

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__(); self.days = {}; self.tip = None; self.text = ''
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'data-date' in a:
            self.days[a['id']] = {'date': a['data-date'], 'level': int(a['data-level'])}
        if tag == 'tool-tip': self.tip = a.get('for'); self.text = ''
    def handle_data(self, data):
        if self.tip: self.text += data
    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.tip:
            if self.tip in self.days:
                m = re.search(r'([\d,]+) contributions? on', self.text)
                self.days[self.tip]['count'] = int(m.group(1).replace(',', '')) if m else 0
            self.tip = None

def text(x,y,s,size=16,color='#a8b5d6',weight=400,extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" {extra}>{html.escape(str(s))}</text>'
def rect(x,y,w,h,fill='#141b35',stroke='#303d64',r=14,extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" {extra}/>'
def label(x,y,s): return text(x,y,s,11,'#73e0ed',600,'letter-spacing="2"')
def title(x,y,s,size=26): return text(x,y,s,size,'#f0f3ff',700)
def panel(y,h): return rect(24,y,952,h,'url(#panel)')
def chip(x,y,s,c='#8cb9ff',w=100):
    return rect(x,y,w,28,'#111c35','#36466f',7)+text(x+12,y+19,s,11,c,600)

def character(x,y,scale=1,mode='wave'):
    # An original vector mascot; it is not presented as a photographic likeness.
    arm = '<g class="wave"><path d="M63 93 Q94 69 90 37" fill="none" stroke="#b286ff" stroke-width="18" stroke-linecap="round"/><path d="M90 38L86 20M91 35L96 17M95 36L105 24" stroke="#dbac92" stroke-width="7" stroke-linecap="round"/></g>'
    if mode=='point': arm='<path d="M63 95Q95 98 113 77L140 77" fill="none" stroke="#b286ff" stroke-width="18" stroke-linecap="round"/><path d="M134 77L157 74" stroke="#dbac92" stroke-width="8" stroke-linecap="round"/>'
    return f'<g transform="translate({x} {y}) scale({scale})"><g class="bob"><ellipse cx="35" cy="206" rx="62" ry="9" fill="#070d21"/><path d="M17 134L10 186L-2 198" fill="none" stroke="#3c4c76" stroke-width="21" stroke-linecap="round"/><path d="M48 135L54 190L71 196" fill="none" stroke="#293b62" stroke-width="21" stroke-linecap="round"/><path d="M-6 202H16M52 201H77" stroke="#dcdded" stroke-width="10" stroke-linecap="round"/><path d="M4 75Q31 64 60 76L70 141Q32 154-5 141Z" fill="url(#hoodie)" stroke="#cab3ff" stroke-width="1.5"/>{arm}<path d="M4 90Q-24 113-11 134L8 141" fill="none" stroke="#8964d5" stroke-width="18" stroke-linecap="round"/><rect x="20" y="58" width="24" height="20" rx="8" fill="#ce977e"/><ellipse cx="33" cy="39" rx="28" ry="32" fill="#dbac92"/><path d="M4 38Q-3 2 26 1Q61-7 66 25L57 44L50 21Q29 31 14 20L11 43Z" fill="#172039"/><path d="M17 40H23M41 40H47" stroke="#20263a" stroke-width="3.5" stroke-linecap="round"/><path d="M28 55Q35 60 42 53" fill="none" stroke="#754c49" stroke-width="2" stroke-linecap="round"/><path d="M15 79L32 97L51 77M25 93V114M41 92V112" fill="none" stroke="#d1baff" stroke-width="2"/><rect x="-9" y="112" width="60" height="34" rx="3" fill="#111b35" stroke="#6fdbe9"/><path d="M15 123L9 128L15 133M29 123L35 128L29 133" fill="none" stroke="#a8b3ff" stroke-width="2"/></g></g>'

def render(user,repos,calendar):
    p=Calendar();p.feed(calendar); days=sorted(p.days.values(),key=lambda d:d['date'])
    if len(days)<350 or any('count' not in d for d in days): raise ValueError('Incomplete contribution data; keeping previous artwork')
    total=sum(d['count'] for d in days); active=sum(d['count']>0 for d in days)
    languages=collections.Counter(r['language'] for r in repos if not r['fork'] and r['language'])
    if not languages: raise ValueError('No public repository languages')
    today=datetime.datetime.now(datetime.timezone.utc).strftime('%d %b %Y')
    s=['''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="2260" viewBox="0 0 1000 2260" role="img" aria-labelledby="name desc">
<title id="name">Ayush Kapure — animated developer portfolio</title><desc id="desc">Original animated character, rotating toolkit, project illustrations, swinging ID, public GitHub statistics and a contribution city derived from GitHub activity.</desc>
<defs>
<linearGradient id="panel" x2="1" y2="1"><stop stop-color="#171c3a"/><stop offset="1" stop-color="#0c152b"/></linearGradient>
<linearGradient id="neon"><stop stop-color="#52e0ef"/><stop offset=".5" stop-color="#986cff"/><stop offset="1" stop-color="#ee83c7"/></linearGradient>
<linearGradient id="hoodie" x2="1" y2="1"><stop stop-color="#cf9eff"/><stop offset="1" stop-color="#7851c8"/></linearGradient>
<radialGradient id="glow"><stop stop-color="#d3a1ff"/><stop offset=".3" stop-color="#8542e4"/><stop offset="1" stop-color="#101b37" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#a0c5ff" stroke-opacity=".035"/></pattern>
<clipPath id="roles"><rect x="55" y="181" width="550" height="36"/></clipPath>
<clipPath id="carousel"><rect x="530" y="403" width="417" height="164" rx="12"/></clipPath>
</defs>
<style>
text{font-family:DejaVu Sans,Arial,sans-serif} .wave{transform-origin:63px 93px;animation:wave 2.8s ease-in-out infinite}.bob{animation:bob 5s ease-in-out infinite}.orbit{transform-origin:0px 0px;animation:orbit 26s linear infinite}.counter{animation:reverse-orbit 26s linear infinite}.badge{transform-origin:177px 1000px;animation:swing 6s ease-in-out infinite}.roles{animation:roles 12s infinite}.slides{animation:slides 15s infinite}.pulse{animation:pulse 3s ease-in-out infinite}.shine{animation:shine 5s ease-in-out infinite}.city{animation:city 3s ease-out both}.story{animation:story 5s linear infinite}
@keyframes wave{0%,45%,100%{transform:rotate(0deg)}15%,30%{transform:rotate(16deg)}22%,37%{transform:rotate(-8deg)}}@keyframes bob{50%{transform:translateY(-5px)}}@keyframes orbit{to{transform:rotate(360deg)}}@keyframes reverse-orbit{to{transform:rotate(-360deg)}}@keyframes swing{0%,100%{transform:rotate(-3deg)}50%{transform:rotate(3deg)}}@keyframes roles{0%,28%{transform:translateY(0)}34%,61%{transform:translateY(-42px)}67%,94%{transform:translateY(-84px)}100%{transform:translateY(0)}}@keyframes slides{0%,28%{transform:translateX(0)}34%,61%{transform:translateX(-417px)}67%,94%{transform:translateX(-834px)}100%{transform:translateX(0)}}@keyframes pulse{50%{opacity:.4}}@keyframes shine{50%{opacity:.55}}@keyframes city{from{opacity:.1;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}@keyframes story{from{stroke-dashoffset:390}to{stroke-dashoffset:0}}
@media(prefers-reduced-motion:reduce){.wave,.bob,.orbit,.counter,.badge,.roles,.slides,.pulse,.shine,.city,.story{animation:none!important}}
</style>
<rect width="1000" height="2260" rx="20" fill="#080e1c"/><rect width="1000" height="2260" fill="url(#grid)"/>
''']
    s += [label(28,35,'AYUSHKAPURE26 / THE DEVELOPER EDITION'),text(782,35,'BUILD. LEARN. REPEAT.',10,'#8c9fc3'),panel(55,266)]
    s += ['<circle cx="780" cy="186" r="150" fill="url(#glow)" opacity=".7"/>',label(55,96,'HELLO WORLD, I AM'),title(55,157,'Ayush Kapure',48),'<g clip-path="url(#roles)"><g class="roles">',text(55,207,'Android developer',22,'#72e0ec',600),text(55,249,'Computer Engineering student',22,'#c09cff',600),text(55,291,'Building tools for real life',22,'#f396cc',600),'</g></g>',text(55,245,'Turning everyday problems into useful software.',16),chip(55,271,'KOTLIN',w=84),chip(149,271,'COMPOSE',w=95),chip(254,271,'OPEN TO LEARNING',w=164),character(773,85,.94),'<path d="M680 81H661V101M936 81H955V101M680 294H661V274M936 294H955V274" fill="none" stroke="#67759d"/>',label(835,303,'SAY HELLO')]
    s += [rect(24,340,467,310,'url(#panel)'),rect(509,340,467,310,'url(#panel)'),label(46,374,'01 / WHAT I BUILD'),title(46,404,'Useful apps. Clear interfaces.',22)]
    # An original app illustration, not a captured product screenshot.
    s += [rect(47,426,421,158,'#111d36','#3a4978',10),'<circle cx="179" cy="505" r="75" fill="url(#glow)"/>',rect(78,444,167,123,'#202d4c','#779aca',9),text(91,466,'CNG MITRA',11,'#70dbe5',700),text(91,499,'Refill. Track. Understand.',9),rect(92,513,58,40,'#263b54','#3b5375',5),rect(158,513,70,40,'#26304f','#3b5375',5),text(99,531,'FUEL',8,'#78e4d5'),text(165,531,'MILEAGE',8,'#c5a6ff'),'<path d="M103 544L115 539L125 545L139 536M169 545L180 540L192 542L211 533" stroke="#69dccd" fill="none"/>',rect(287,437,78,137,'#0a1426','#79a1d0',10),rect(294,451,64,98,'#172f42','#172f42',4),text(302,475,'CNG',13,'#78e4d5',700),'<circle cx="326" cy="505" r="18" fill="none" stroke="#64dec4" stroke-width="5"/><path d="M316 505L323 512L337 495" stroke="#b5fff0" fill="none" stroke-width="3"/>',text(47,610,'Offline records · Mileage · Fuel spending',13),text(47,633,'CNG Mitra / Android project',10,'#8194b9')]
    s += [label(532,374,'02 / BEYOND THE EDITOR'),title(532,404,'Always something to explore.',22),'<g clip-path="url(#carousel)"><g class="slides">']
    for i,(name,caption) in enumerate([('Interface design','Making useful information easier to read.'),('Data & insights','Finding the story behind everyday numbers.'),('Learning by building','Small experiments. Practical improvements.')]):
        x=530+i*417
        s += [rect(x,420,417,147,'#192445','#344570',10),'<g transform="translate(%s 0)">'%x]
        if i==0:
            s += [rect(35,443,182,101,'#111c34','#8ca4d2',8),rect(45,454,162,18,'#8262c8','#8262c8',3),rect(46,482,48,51,'#3b6684','#3b6684',4),rect(103,482,104,12,'#455279','#455279',3),rect(103,502,83,8,'#3c4769','#3c4769',3),rect(103,521,59,8,'#6c5a9b','#6c5a9b',3)]
        elif i==1:
            for j,h in enumerate([24,51,41,79,62]):s += [rect(43+j*30,540-h,18,h,['#6b6ee1','#9682ec','#5acccc'][j%3],'none',3)]
            s += ['<path d="M38 485L72 477L104 481L135 451L176 441" stroke="#f390c8" stroke-width="3" fill="none"/>']
        else:
            s += [rect(42,446,160,101,'#121e36','#7f9dcc',7),text(60,473,'> build --learn',12,'#6ae4dc'),text(60,497,'[pass] improve',12,'#c9a0ff'),text(60,521,'[next] repeat',12,'#e5add0')]
        s += [character(278,430,.56),'</g>']
    s += ['</g></g>',text(532,603,'Design · Data · Learning through projects',13),'<path d="M533 625H945" stroke="#2d3d61" stroke-width="4"/><path class="story" d="M533 625H923" stroke="url(#neon)" stroke-width="4" stroke-dasharray="390"/>']
    # Toolkit orbit, with recognizable compact vector marks.
    s += [panel(669,288),label(47,705,'03 / TOOLS I BUILD WITH'),title(408,751,'A toolkit that keeps growing.',25),text(408,782,'From the screen to storage and the build pipeline.',14)]
    s += ['<g transform="translate(208 825)"><circle r="98" fill="none" stroke="#2c3c65"/><ellipse rx="134" ry="64" fill="none" stroke="#2c3c65" transform="rotate(-22)"/><circle r="71" fill="none" stroke="#35466d" stroke-dasharray="3 8"/><circle r="70" fill="url(#glow)" class="shine"/><circle r="34" fill="#402b76" stroke="#bd86ed"/>',text(-17,6,'AK',19,'#fff',700),'<g class="orbit">']
    icons=[('K','#b97cff'),('C','#73dcbc'),('R','#64b5f6'),('G','#ef836c'),('Py','#f2ca64'),('JS','#f4d968'),('</>','#ea8fce'),('CI','#83abea')]
    for i,(name,c) in enumerate(icons):
        a=i*math.pi/4;x=90*math.cos(a);y=90*math.sin(a)
        s += [f'<g transform="translate({x:.2f} {y:.2f})"><g class="counter"><circle r="20" fill="#132039" stroke="{c}" stroke-opacity=".65"/>']
        if name=='K':s += ['<path d="M-9-10H10L0 0L10 10H-9Z" fill="url(#neon)"/>']
        elif name=='G':s += ['<path d="M0-12L12 0L0 12L-12 0Z" fill="#e97563"/><path d="M-4-5L5 4M0-1V6" stroke="#172139" stroke-width="2"/><circle cx="-4" cy="-5" r="2" fill="#172139"/><circle cx="5" cy="4" r="2" fill="#172139"/>']
        else:s += [text(0,5,name,12,c,700,'text-anchor="middle"')]
        s += ['</g></g>']
    s += ['</g></g>']
    for i,(n,c) in enumerate([('Kotlin','#c6a5ff'),('Jetpack Compose','#80e6c4'),('Room','#82c7ed'),('Coroutines','#c6a5ff'),('Git','#f2937b'),('GitHub Actions','#8eb6f7')]):s += [chip(408+(i%3)*169,805+(i//3)*40,n,c,156)]
    s += [text(408,917,'Integrations: Firebase · Google Maps · Gemini',12)]
    # Swinging original ID, with live public data.
    s += [panel(976,308),label(47,1012,'04 / PROFILE AT A GLANCE'),'<g class="badge"><path d="M177 1000V1040" stroke="url(#neon)" stroke-width="16"/><rect x="162" y="1031" width="30" height="14" rx="4" fill="#7587ae"/>',rect(82,1042,191,211,'#14223e','#8368c5',11),rect(90,1050,175,195,'none','#344e78',8),label(103,1074,'DEVELOPER / 026'),character(154,1072,.48),text(177,1200,'Ayush Kapure',16,'#f4efff',700,'text-anchor="middle"'),text(177,1220,'COMPUTER ENGINEERING',8,'#8fc6ed',500,'text-anchor="middle"'),'</g>',title(317,1056,'The work, in numbers.',25)]
    stats=[(user['public_repos'],'PUBLIC REPOS'),(user['followers'],'FOLLOWERS'),(total,'CONTRIBUTIONS'),(active,'ACTIVE DAYS')]
    for i,(n,l) in enumerate(stats):
        x=317+i*153;s += [rect(x,1074,140,83,'#111c33','#2c3d60',8),title(x+15,1112,n,29),text(x+15,1140,l,9,'#94a7c9',600)]
    s += [text(317,1182,'Contribution period: '+days[0]['date']+' → '+days[-1]['date'],11),text(317,1208,'Focus: offline usability, build reliability, useful data.',13),text(317,1238,'PUBLIC GITHUB SNAPSHOT / '+today.upper(),10,'#77cfcf',500),'<circle cx="938" cy="1008" r="4" fill="#72e3c5" class="pulse"/>']
    s += [panel(1303,174),label(47,1339,'05 / FEATURED BUILDS'),'<path d="M47 1354H952M47 1407H952" stroke="#2d3f61"/>',title(47,1386,'CNG Mitra',16),text(303,1386,'Refill history, mileage and fuel expenses',14),chip(817,1366,'ANDROID',w=111),title(47,1439,'Data Check',16),text(303,1439,'Data tooling project · Explore the source',14),chip(817,1419,'JAVASCRIPT',w=111)]
    # Isometric contribution city; each building is one real GitHub day.
    s += [panel(1496,407),label(47,1533,'06 / A YEAR OF BUILDING'),title(47,1570,'Every day becomes part of the city.',26),text(47,1597,'One building per day. Height follows GitHub contribution intensity.',13)]
    start=datetime.date.fromisoformat(days[0]['date'])
    colors=['#172b4b','#224d86','#326bd0','#6555e0','#ad77ef']
    for d in days:
        dt=datetime.date.fromisoformat(d['date']);delta=(dt-start).days;week=delta//7;day=delta%7
        x=113+week*13.6-day*8.4;y=1645+week*2.7+day*6.4;h=2+d['level']*12
        a=f'{x:.1f},{y-h:.1f} {x+12:.1f},{y+2.4-h:.1f} {x+4.6:.1f},{y+8-h:.1f} {x-7.4:.1f},{y+5.6-h:.1f}'
        s += [f'<g class="city"><title>{d["date"]}: {d["count"]} contributions</title><path d="M{x-7.4:.1f} {y+5.6-h:.1f}l12 2.4v{h}l-12-2.4Z" fill="{colors[d["level"]]}"/><path d="M{x+4.6:.1f} {y+8-h:.1f}l7.4-5.6v{h}l-7.4 5.6Z" fill="#183763"/><polygon points="{a}" fill="{colors[d["level"]]}" stroke="#7ca9e6" stroke-opacity=".2" stroke-width=".5"/></g>']
    s += [text(47,1866,str(total)+' contributions',14,'#b6abfa',600),text(287,1866,str(active)+' active days',14,'#77dfdd',600),text(596,1866,'LESS',9)]
    for i in range(5):s += [rect(636+i*24,1854,16,13,colors[i],'none',2)]
    s += [text(762,1866,'MORE',9),text(830,1866,'DAILY REFRESH',9,'#9aabc9')]
    # Exact language distribution by public non-fork repository primary language.
    s += [rect(24,1922,365,156,'url(#panel)'),label(47,1957,'PUBLIC REPOSITORY LANGUAGES')]
    counts=sum(languages.values());offset=0;colors2=['#9d7aff','#67d9d5','#ed91c5','#e9cb79']
    s += ['<g transform="translate(93 2015) rotate(-90)">']
    for i,(lang,n) in enumerate(languages.most_common()):
        length=n/counts*251.327;s += [f'<circle r="40" fill="none" stroke="{colors2[i%4]}" stroke-width="12" stroke-dasharray="{length:.3f} {251.327-length:.3f}" stroke-dashoffset="{-offset:.3f}"/>'];offset+=length
    s += ['</g>',text(93,2021,counts,18,'#edf0ff',700,'text-anchor="middle"')]
    for i,(lang,n) in enumerate(languages.most_common()):s += [f'<circle cx="160" cy="{1989+i*24}" r="4" fill="{colors2[i%4]}"/>',text(173,1994+i*24,f'{lang} · {n} repos',11)]
    s += [rect(407,1922,569,156,'url(#panel)'),label(431,1957,'07 / LET’S BUILD SOMETHING USEFUL'),title(431,1992,'Say hello. Share an idea.',24),text(431,2021,'GitHub · LinkedIn · Email',14),text(431,2053,'ayushkapure26@gmail.com',13,'#73dce7'),character(861,1932,.56,'point')]
    s += [text(500,2122,'Useful projects. Clear code. Steady learning.',16,'#b7c4e0',500,'text-anchor="middle"'),text(500,2152,'ANDROID DEVELOPMENT / COMPUTER ENGINEERING / ALWAYS LEARNING',10,'#7890b6',400,'text-anchor="middle"'),'<path d="M345 2180H655" stroke="url(#neon)" stroke-width="2"/>',text(500,2215,'AYUSH KAPURE',11,'#8a9cbe',600,'text-anchor="middle" letter-spacing="5"'),'</svg>']
    return ''.join(s),{'updated_at':today,'contributions':total,'active_days':active,'days':len(days),'public_repos':user['public_repos'],'followers':user['followers'],'languages_by_repo':dict(languages),'period':[days[0]['date'],days[-1]['date']]}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cached',action='store_true');args=parser.parse_args()
    if args.cached:
        user=json.loads((ROOT/'user.json').read_text());repos=json.loads((ROOT/'repos.json').read_text());calendar=(ROOT/'contributions.html').read_text()
    else:
        user=json.loads(fetch(f'https://api.github.com/users/{USER}'))
        repos=[];page=1
        while True:
            batch=json.loads(fetch(f'https://api.github.com/users/{USER}/repos?per_page=100&page={page}'));repos.extend(batch)
            if len(batch)<100:break
            page+=1
        calendar=fetch(f'https://github.com/users/{USER}/contributions')
    svg,stats=render(user,repos,calendar)
    import xml.etree.ElementTree as ET
    ET.fromstring(svg)
    (ROOT/'assets').mkdir(exist_ok=True)
    (ROOT/'assets'/'animated-profile.svg').write_text(svg)
    (ROOT/'assets'/'profile-data.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats))
if __name__=='__main__':main()

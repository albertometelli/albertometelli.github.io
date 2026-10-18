#!/usr/bin/env python3
"""Canonical BibTeX -> incremental DBLP/source enrichment -> static site + clean downloads.

The annotated bibliography/*.bib files (not DBLP JSON) are the source of truth.
Editorial fields/keys are stable and never overwritten by remote enrichment.
Run online with --sync; run offline (no guessing of rating data) by default.
"""
from __future__ import annotations
import argparse
from collections import OrderedDict, Counter, defaultdict
from datetime import date
import html
import json
import re
import sys
import time
import unicodedata
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote, urlencode
import urllib.request
import xml.etree.ElementTree as ET

from bibtex_utils import parse_entries, fmt, normalize_title
from update_publications import DEFAULT_PID, download_xml, plain_text, record_to_json

ROOT=Path(__file__).resolve().parents[1]
BIB=ROOT/'bibliography'
SECTIONS={'a':'Abstracts','b':'Book chapters','bb':'Books','c':'Conferences','j':'Journals','r':'Technical reports','t':'Theses','u':'Under review','w':'Workshops'}
PRIVATE={'rankcore','rankggs','ranksjr','acceptance','alphabetic','alphabetical','note','poster','slides','presentation','video','dblp','dblpkey','core_source_url','sjr_source_url','acceptance_source_url','sjrcategory','distinction','equalauthors','abstract','keywords','html','type','source','rating_provider','award'}
CITATION_FIELDS=('author','editor','title','booktitle','journal','year','volume','number','pages','publisher','series','organization','school','edition','chapter','address','month','doi','url','isbn','issn')
SPECIAL_LINKS=('slides','poster','presentation','video','arxiv','code')
MONTHS={name.lower():index for index,name in enumerate(
    ('January','February','March','April','May','June','July','August','September','October','November','December'),1)}
# Approximate annual occurrence order used only when a BibTeX record has no
# explicit month. Later events sort before earlier events within the same year.
VENUE_MONTHS=(
    (r'neurips|neural information processing',12),
    (r'corl|robot learning',11),
    (r'ewrl|european workshop on reinforcement learning',10),
    (r'ecml|principles and practice of knowledge discovery',9),
    (r'rlc|reinforcement learning conference',8),
    (r'ijcai|international joint conference on artificial intelligence',8),
    (r'uncertainty in artificial intelligence|\buai\b',8),
    (r'icml|international conference on machine learning',7),
    (r'robotics: science and systems|\brss\b',7),
    (r'ijcnn|international joint conference on neural networks',7),
    (r'colt|conference on learning theory',6),
    (r'american control conference|\bacc\b',6),
    (r'aistats|artificial intelligence and statistics',5),
    (r'iclr|learning representations',5),
    (r'aaai',2),
)

LATEX_ACCENTS={
    "a`":"à", "e`":"è", "i`":"ì", "o`":"ò", "u`":"ù",
    "a'":"á", "e'":"é", "i'":"í", "o'":"ó", "u'":"ú", "y'":"ý",
    'a"':'ä', 'e"':'ë', 'i"':'ï', 'o"':'ö', 'u"':'ü',
    'a^':'â', 'e^':'ê', 'i^':'î', 'o^':'ô', 'u^':'û',
    'a~':'ã', 'n~':'ñ', 'o~':'õ', 'c,':'ç',
}

def latex_text(value):
    """Make BibTeX display text without losing brace-protected capitals.

    The canonical BibTeX remains untouched; this conversion is only for JSON/HTML.
    It also makes the handful of inline formulae readable without emitting raw LaTeX.
    """
    text=html.unescape(str(value or '')).replace('\n',' ')
    text=text.replace(r'{\textbackslash}', '\\').replace(r'\textbackslash', '\\')
    text=text.replace(r'\$', '$').replace(r'\{','{').replace(r'\}','}')
    for command,replacement in {
        r'\textquoteright':'’',r'\quotes':'',r'\&':'&',r'\%':'%',
        r'\epsilon':'ε',r'\varepsilon':'ε',r'\widetilde':'',r'\tilde':'',
    }.items(): text=text.replace(command,replacement)
    text=re.sub(r'\\mathcal\s*\{\s*O\s*\}','𝒪',text)
    text=re.sub(r'\\sqrt\s*\{([^{}]+)\}',r'√\1',text)
    for mark in ("'",'`','"','^','~',','):
        pattern=r"\\"+re.escape(mark)+r"\s*\{?([A-Za-z])\}?"
        def accented(match,mark=mark):
            letter=match.group(1);converted=LATEX_ACCENTS.get(letter.lower()+mark,letter)
            return converted.upper() if letter.isupper() else converted
        text=re.sub(pattern,accented,text)
    # Formatting/protection braces affect BibTeX, not the displayed string.
    text=re.sub(r'\\(?:textbf|emph|textit|mathrm|mathbf)\s*\{([^{}]*)\}',r'\1',text)
    text=text.replace('{','').replace('}','').replace('$','')
    return re.sub(r'\s+',' ',text).strip()

def author_list(value):
    authors=[]
    for raw in re.split(r'\s+and\s+',str(value or '')):
        name=latex_text(raw)
        if not name:continue
        if ',' in name:
            family,given=(part.strip() for part in name.split(',',1))
            name=f'{given} {family}'.strip()
        authors.append(name)
    return authors


def norm(value):
    return normalize_title(re.sub(r'\\(?:textbf|emph|textit)\s*\{([^{}]*)\}',r'\1',str(value or '')))

def sjr_norm(value):
    value=unicodedata.normalize('NFKD',str(value or ''))
    return re.sub('[^a-z0-9]','', ''.join(c for c in value if not unicodedata.combining(c)).lower())

def getyear(e):
    match=re.search(r'(?:19|20)\d{2}',e['fields'].get('year',''))
    return int(match.group()) if match else 0

def occurrence_month(venue, explicit=''):
    raw=str(explicit or '').strip().lower().rstrip('.')
    if raw in MONTHS:return MONTHS[raw]
    if raw.isdigit() and 1<=int(raw)<=12:return int(raw)
    for pattern,month in VENUE_MONTHS:
        if re.search(pattern,str(venue or ''),re.I):return month
    return 0

def entry_sort_key(entry):
    fields=entry['fields']
    venue=fields.get('booktitle') or fields.get('journal') or fields.get('school') or fields.get('publisher') or ''
    to_appear=bool(re.search(r'\bto appear\b',fields.get('note',''),re.I))
    return (-getyear(entry),-int(to_appear),-occurrence_month(venue,fields.get('month','')),norm(fields.get('title','')))

def publication_sort_key(publication):
    to_appear=str(publication.get('status','')).casefold()=='to appear'
    return (-int(publication.get('year') or 0),-int(to_appear),-occurrence_month(publication.get('venue','')),norm(publication.get('title','')))

def getdoi(e):
    fs=e['fields'];doi=fs.get('doi','')
    if not doi:
        match=re.search(r'(?:doi\.org/|dx\.doi\.org/)(10\.\d{4,9}/[^\s}?#]+)',fs.get('url',''),re.I)
        if match:doi=match.group(1)
    return doi.replace('https://doi.org/','').strip().lower().rstrip('.,')

def signature(e):
    return 'title:'+norm(e['fields'].get('title',''))

def group_of(pub):
    category=pub.get('category','other')
    return {'conferences':'c','journals':'j','workshops':'w','chapters':'b','books':'bb','theses':'t','preprints':'u','other':'a'}.get(category,'a')

def metadata_from_fields(e):
    f=e['fields'];t=e['type']
    group=e.get('group','a')
    venue=f.get('journal') if t=='article' else f.get('booktitle') or f.get('school') or f.get('institution') or f.get('howpublished') or f.get('publisher') or ('Manuscript' if t=='unpublished' else '')
    return {'title':latex_text(f.get('title','')),
            'authors':author_list(f.get('author','')),
            'year':str(getyear(e)) if getyear(e) else '',
            'venue':latex_text(venue),
            'category':{'a':'abstracts','c':'conferences','j':'journals','w':'workshops','b':'chapters','bb':'books','r':'reports','t':'theses','u':'under-review'}.get(group,'abstracts'),
            'paper_url':f.get('url') or ('https://doi.org/'+f['doi'] if f.get('doi') else ''),
            'doi':getdoi(e),'key':e['key']}

def rate_text(raw):
    return re.sub(r'\\textbf\{([^{}]+)\}',r'\1',raw or '').replace(r'\%','%').strip()

def load_entries(basedir=BIB):
    bins={g:[] for g in SECTIONS}; issues=[];top=[];key_index={};seen={}
    for group in (*SECTIONS,'top'):
        path=basedir/f'biblio_{group}.bib'
        if not path.exists():continue
        source=path.read_text(encoding='utf-8-sig')
        entries=parse_entries(source)
        for e in entries:
            f=e['fields'];title=norm(f.get('title',''))
            if not title:continue
            if group=='top':top.append(e);continue
            if e['type']=='incollection' and group in ('c','w'):e['type']='inproceedings'
            e['group']=group
            # The curated archive may intentionally contain distinct versions of a
            # work (for example a thesis and the resulting book). Deduplicate only
            # accidental repetitions inside the same collection.
            collection_key=(group,title)
            if collection_key in seen:
                old=seen[collection_key]
                for k,v in f.items():old['fields'].setdefault(k,v)
                issues.append('Duplicate record merged within '+group+': '+e['key']+' -> '+old['key'])
                continue
            if e['key'].casefold() in key_index and key_index[e['key'].casefold()]!=title:
                prior=e['key'];i=2
                while (e['key']+'_'+str(i)).casefold() in key_index:i+=1
                e['key']=prior+'_'+str(i)
                issues.append('Citation key conflict renamed: '+prior+' -> '+e['key'])
            key_index[e['key'].casefold()]=title
            seen[collection_key]=e;bins[group].append(e)
    return bins,top,issues

def newkey(pub,existing):
    surname='metelli';year=str(pub.get('year') or 'nd')
    terms=re.findall(r'[a-z0-9]+',pub.get('title','').lower());token=next((t for t in terms if t not in {'the','a','an','on','of','for','with','in','and'}),'paper')
    key=surname+year+token;i=2
    while key.casefold() in existing:key=surname+year+token+str(i);i+=1
    existing.add(key.casefold());return key

def xml_items(xml):
    root=ET.fromstring(xml)
    if root.tag!='dblpperson' or (root.get('pid') and root.get('pid')!=DEFAULT_PID):
        raise ValueError('DBLP author ID mismatch / invalid XML')
    for r in root.findall('r'):
        for node in r:
            pub=record_to_json(node)
            if not pub:continue
            for field in ('volume','pages','number','publisher','series','school','doi'):
                val=plain_text(node.find(field))
                if val:pub[field]=val
            pub['url']=pub.get('paper_url','')
            yield pub

def import_dblp(bins,xml):
    added=0;filled=0
    by_title={norm(e['fields'].get('title','')):e for group in bins for e in bins[group]}
    by_doi={getdoi(e):e for group in bins for e in bins[group] if getdoi(e)}
    keys={e['key'].casefold() for group in bins for e in bins[group]}
    for pub in xml_items(xml):
        title=norm(pub['title']);doi=str(pub.get('doi','') or '')
        if not doi:
            match=re.search(r'doi\.org/(10\.\d{4,9}/[^?#]+)',pub.get('paper_url',''),re.I)
            if match:doi=match.group(1)
        entry=by_doi.get(doi.lower()) or by_title.get(title)
        # A formerly under-review manuscript may acquire a peer-reviewed venue.
        # Keep its stable citation key and editorial notes; promote its category.
        if entry and entry.get('group')=='u' and group_of(pub) in ('c','j','w'):
            group=group_of(pub)
            bins['u'].remove(entry)
            entry['group']=group
            entry['type']='article' if group=='j' else 'inproceedings'
            venuefield='journal' if group=='j' else 'booktitle'
            entry['fields'][venuefield]=pub.get('venue','')
            if not entry['fields'].get('year'):entry['fields']['year']=str(pub['year'])
            bins[group].append(entry)
            filled+=1
        if not entry:
            group=group_of(pub)
            if group=='u' and title in by_title:continue
            f=OrderedDict(title=pub['title'],author=' and '.join(pub.get('authors',[])),year=str(pub['year']))
            kind='article' if group=='j' else 'inproceedings' if group in ('c','w') else 'incollection' if group=='b' else 'book' if group=='bb' else 'phdthesis' if group=='t' else 'misc'
            venuefield='journal' if kind=='article' else 'booktitle' if kind in ('inproceedings','incollection') else 'school' if kind=='phdthesis' else 'publisher'
            f[venuefield]=pub.get('venue','')
            entry={'type':kind,'key':newkey(pub,keys),'fields':f,'group':group}
            bins[group].append(entry);by_title[title]=entry;added+=1
        f=entry['fields']
        for key in ('volume','pages','number','publisher','series','doi','url'):
            val=doi if key=='doi' else pub.get(key,'')
            if val and not f.get(key):f[key]=val;filled+=1
        if pub.get('dblp_key') and not f.get('dblpkey'):f['dblpkey']=pub['dblp_key']
    return added,filled

def category_for_journal(venue):
    path=ROOT/'data/sjr_categories.json'
    try: return json.loads(path.read_text(encoding='utf8')).get(sjr_norm(venue),'Artificial Intelligence')
    except (ValueError,OSError):return 'Artificial Intelligence'

def enrich_crossref(bins,limit=30):
    """Complete missing DOIs/pages when a Crossref record matches exactly on title+year.

    Rate-limited, capped and conservative; editorial fields are never overwritten.
    """
    checked=0;enriched=0;notes=[]
    for group in ('c','j','b'):
        for entry in bins[group]:
            f=entry['fields'];year=getyear(entry)
            if not year or not f.get('title') or (getdoi(entry) and f.get('volume') and f.get('pages')):continue
            if checked>=limit:return checked,enriched,notes
            checked+=1
            params=urlencode({'query.title':re.sub(r'[{}]','',f['title']),'rows':3,'select':'title,DOI,published,volume,page,issue,URL'})
            url='https://api.crossref.org/works?'+params
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'AcademicBibliography/6.0 (contact: albertomaria.metelli@polimi.it)','Accept':'application/json'})
                with urllib.request.urlopen(req,timeout=14) as response:payload=json.load(response)
                for item in payload.get('message',{}).get('items',[]):
                    item_title=(item.get('title') or [''])[0]
                    if norm(item_title)!=norm(f['title']):continue
                    published=item.get('published',{}).get('date-parts',[[None]])[0][0]
                    if isinstance(published,int) and abs(published-year)>1:continue
                    for field,field_source in [('doi','DOI'),('volume','volume'),('pages','page'),('number','issue')]:
                        if not f.get(field) and item.get(field_source):
                            f[field]=str(item[field_source]);enriched+=1
                    if not f.get('url') and f.get('doi'):f['url']='https://doi.org/'+f['doi'];enriched+=1
                    break
            except (ValueError,TimeoutError,OSError) as exc:
                notes.append(f'{entry["key"]}: Crossref unavailable ({type(exc).__name__})')
            time.sleep(.15)
    return checked,enriched,notes

def export_model(bins,top):
    publications=[]
    for group,entries in bins.items():
        for e in entries:
            p=metadata_from_fields(e);f=e['fields']
            note=latex_text(rate_text(f.get('note','')))
            if re.fullmatch(r'(?:to appear|in press|under review(?: for .+)?|spotlight)',note,re.I):
                if note.casefold()=='spotlight':p['recognition']=note
                else:p['status']=note
                p['note']=''
            else:p['note']=note
            p['alphabetical_order']=bool(f.get('alphabetic') and f['alphabetic'].lower() in ('yes','true','1'))
            p['equal_contribution_authors']=author_list(f.get('equalauthors',''))
            if f.get('recognition') or f.get('distinction') or f.get('award'):
                p['recognition']=latex_text(f.get('recognition') or f.get('distinction') or f.get('award'))
            p['extra_links']={name:title for name in SPECIAL_LINKS if (title:=f.get(name,'')).startswith(('http://','https://'))}
            p['bibtex_download']='bibliography/downloads/entries/'+e['key']+'.bib'
            p['acceptance_rate']=rate_text(f.get('acceptance',''))
            p['acceptance']={'source_url':f.get('acceptance_source_url','')} if f.get('acceptance_source_url') else {}
            p['ratings']={}
            core=f.get('rankcore','')
            if core:
                m=re.search(r'(?<![A-Za-z])(A\*|A|B|C)(?![A-Za-z*])',rate_text(core))
                p['ratings']['core']={'value':m.group(1) if m else rate_text(core), 'source_year':int(re.search(r'20\d\d',core).group()) if re.search(r'20\d\d',core) else None,
                    'scheme':'ICORE' if re.search(r'\bICORE\b',core,re.I) else 'CORE',
                    'provider':'CORE/ICORE (annotated local bibliography)','source_url':f.get('core_source_url','')}
            sjr=f.get('ranksjr','')
            if sjr:
                quart=re.search(r'\bQ[1-4]\b',rate_text(sjr));cat=f.get('sjrcategory') or category_for_journal(f.get('journal',''))
                p['ratings']['sjr']={'value':quart.group() if quart else rate_text(sjr),'quartile':quart.group() if quart else '',
                    'category':cat,'source_year':int(re.search(r'20\d\d',sjr).group()) if re.search(r'20\d\d',sjr) else None,
                    'provider':'SCImago (annotated local bibliography)','source_url':f.get('sjr_source_url',''),
                    'chronologically_eligible':bool(re.search(r'20\d\d',sjr)) and (int(re.search(r'20\d\d',sjr).group())+1<=getyear(e))}
            if f.get('rankggs'):p['ratings']['ggs']={'value':rate_text(f['rankggs'])}
            publications.append(p)
    publications.sort(key=publication_sort_key)
    return publications

def merge_enrichment(bins,pubs):
    by_title={norm(p.get('title','')):p for p in pubs};changed=0
    for group,entries in bins.items():
        for e in entries:
            p=by_title.get(norm(e['fields'].get('title','')))
            if not p:continue
            f=e['fields']
            a=p.get('acceptance') or {}
            if a.get('source_url') and p.get('acceptance_rate'):
                value=p['acceptance_rate'].replace('%',r'\%')
                if f.get('acceptance')!=value:f['acceptance']=value;changed+=1
                f['acceptance_source_url']=a['source_url']
            for kind,col,src in [('core','rankcore','core_source_url'),('sjr','ranksjr','sjr_source_url')]:
                rec=(p.get('ratings') or {}).get(kind) or {}
                if not rec.get('source_url') or not rec.get('source_year'):continue
                if kind=='core':
                    value=f'CORE {rec["source_year"]}: \\textbf{{{rec["value"]}}}'
                else:
                    q=rec.get('quartile')
                    if not q or rec.get('category') is None:continue
                    value=f'SJR {rec["source_year"]}: \\textbf{{{q}}}'
                    f['sjrcategory']=rec['category']
                if f.get(col)!=value:changed+=1;f[col]=value
                f[src]=rec['source_url']
    return changed

def summary(pubs):
    conferences=[p for p in pubs if p['category']=='conferences']
    journals=[p for p in pubs if p['category']=='journals']
    a_star=sum(bool(re.match(r'^A\*(?:\s|$)',p.get('ratings',{}).get('core',{}).get('value',''))) for p in conferences)
    q1=sum(p.get('ratings',{}).get('sjr',{}).get('quartile')=='Q1' and p.get('ratings',{}).get('sjr',{}).get('chronologically_eligible',False) for p in journals)
    coverage_core=sum(bool(p.get('ratings',{}).get('core')) for p in conferences)
    coverage_sjr=sum(bool(p.get('ratings',{}).get('sjr',{}).get('chronologically_eligible',False)) for p in journals)
    # Offline snapshot of the ELLIS approved publication venues. Keep the
    # renderer deterministic; the authoritative list is linked from the page.
    ellis_conference_patterns={
        'AAAI':r'\bAAAI\b|AAAI Conference|Association for the Advancement of Artificial Intelligence',
        'AAMAS':r'\bAAMAS\b|Autonomous Agents and Multiagent Systems?',
        'ACL':r'\bACL\b|Association for Computational Linguistics',
        'ACM FAccT':r'\bFAccT\b|Fairness, Accountability, and Transparency',
        'ACM Multimedia':r'\bACM Multimedia\b|ACM International Conference on Multimedia',
        'AISTATS':r'\bAISTATS\b|Artificial Intelligence and Statistics',
        'COLT':r'\bCOLT\b|Conference on Learning Theory',
        'CoRL':r'\bCoRL\b|Conference on Robot Learning',
        'CVPR':r'\bCVPR\b|Computer Vision and Pattern Recognition',
        'ECCV':r'\bECCV\b|European Conference on Computer Vision',
        'EMNLP':r'\bEMNLP\b|Empirical Methods in Natural Language Processing',
        'ICCV':r'\bICCV\b|International Conference on Computer Vision',
        'ICLR':r'\bICLR\b|International Conference on Learning Representations',
        'ICML':r'\bICML\b|International Conference on Machine Learning',
        'IJCAI':r'\bIJCAI\b|International Joint Conference on Artificial Intelligence',
        'KDD':r'\bKDD\b|Knowledge Discovery and Data Mining',
        'MICCAI':r'\bMICCAI\b|Medical Image Computing and Computer.Assisted Intervention',
        'NeurIPS':r'\bNeurIPS\b|Neural Information Processing Systems',
        'RSS':r'\bRSS\b|Robotics: Science and Systems',
        'SIGIR':r'\bSIGIR\b',
        'SIGGRAPH':r'\bSIGGRAPH\b',
        'UAI':r'\bUAI\b|Uncertainty in Artificial Intelligence',
        'Web Conference':r'\bThe Web Conference\b|\bWWW\b',
        'WSDM':r'\bWSDM\b|Web Search and Data Mining',
    }
    ellis_journal_patterns={
        'IJCV':r'\bIJCV\b|International Journal of Computer Vision',
        'IJRR':r'\bIJRR\b|International Journal of Robotics Research',
        'JMLR':r'\bJMLR\b|Journal of Machine Learning Research',
        'PAMI':r'\bPAMI\b|Transactions on Pattern Analysis and Machine Intelligence',
        'Science Robotics':r'^Science Robotics$',
        'TACL':r'\bTACL\b|Transactions of the Association for Computational Linguistics',
        'TRO':r'\bT-?RO\b|Transactions on Robotics',
    }
    def selected_venue_counts(publications, patterns):
        names=Counter()
        for publication in publications:
            for venue,pattern in patterns.items():
                if re.search(pattern,publication.get('venue',''),re.I):
                    names[venue]+=1
                    break
        return dict(names)
    return {'total':len(conferences)+len(journals),'conferences':len(conferences),'journals':len(journals),
            'a_star_conference_papers':a_star,'q1_journal_articles':q1,
            'rated_conferences':coverage_core,'rated_journals':coverage_sjr,
            'selected_conferences':selected_venue_counts(conferences,ellis_conference_patterns),
            'selected_journals':selected_venue_counts(journals,ellis_journal_patterns)}

def minimal(e):
    return {'key':e['key'],'type':e['type'],'fields':OrderedDict((k,v) for k,v in e['fields'].items() if k in CITATION_FIELDS and v and not (k=='url' and v.lower().startswith('https://dblp.org/pid/')))}

def validate(bins):
    failures=[];incomplete=[];used=set();titles=set();total=0
    for group,entries in bins.items():
        for e in entries:
            total+=1;f=e['fields'];key=e['key'];title=norm(f.get('title',''))
            if key.casefold() in used:failures.append('duplicate citation key: '+key)
            used.add(key.casefold())
            title_key=(group,title)
            if title_key in titles:failures.append('duplicate title within '+group+': '+key)
            titles.add(title_key)
            required=('title','author','year','booktitle') if e['type']=='inproceedings' else ('title','author','year','journal') if e['type']=='article' else ('title','year')
            missing=[k for k in required if not f.get(k)]
            if missing:incomplete.append({'key':key,'missing':missing})
            if e['type']=='inproceedings' and group=='j':failures.append('conference misplaced into journal collection: '+key)
            if group=='c' and e['type']!='inproceedings':failures.append('conference not @inproceedings: '+key)
            # verify that the emitted output still parses as a valid entry
            if len(parse_entries(fmt(e)))!=1:failures.append('unparsable BibTeX: '+key)
    return failures,incomplete,total

def output_files(bins,top,report):
    failures,incomplete,count=validate(bins)
    report['coverage']={
        'missing_doi':sum(not getdoi(e) for entries in bins.values() for e in entries),
        'missing_paper_url':sum(not (e['fields'].get('url') or getdoi(e)) for entries in bins.values() for e in entries),
        'missing_acceptance_rate_for_conferences':sum(not e['fields'].get('acceptance') for e in bins['c']),
        'missing_core_rating_for_conferences':sum(not e['fields'].get('rankcore') for e in bins['c']),
        'missing_sjr_rating_for_journals':sum(not e['fields'].get('ranksjr') for e in bins['j']),
    }
    report['temporal_warnings']=[e['key']+': SJR edition may postdate publication year'
        for e in bins['j'] if re.search(r'20\d{2}',e['fields'].get('ranksjr','')) and
        int(re.search(r'20\d{2}',e['fields'].get('ranksjr','')).group())+1>getyear(e)]
    if failures:raise ValueError('BibTeX validation failed: '+'; '.join(failures[:10]))
    pubs=export_model(bins,top)
    selected={norm(e['fields'].get('title','')) for e in top}
    with TemporaryDirectory(prefix='bib-build-') as tmp:
        tmp=Path(tmp);newbib=tmp/'bibliography';newbib.mkdir();dl=newbib/'downloads';dl.mkdir();entriesdir=dl/'entries';entriesdir.mkdir()
        combined=[];report['counts']={'unique_publications':count,'missing_required_fields':len(incomplete)}
        report['missing_fields']=incomplete
        for group in SECTIONS:
            entries=sorted(bins[group],key=entry_sort_key)
            # annotated data, source of truth
            (newbib/f'biblio_{group}.bib').write_text('% Annotated canonical bibliography: manually curated fields persist.\n\n'+'\n'.join(fmt(e) for e in entries),encoding='utf8')
            (dl/f'biblio_{group}.bib').write_text('% Plain BibTeX citations: no rankings, acceptance statistics or materials.\n\n'+'\n'.join(fmt(minimal(e)) for e in entries),encoding='utf8')
            combined.extend(entries)
        combined.sort(key=entry_sort_key)
        top_entries=sorted((e for e in combined if norm(e['fields'].get('title','')) in selected),key=entry_sort_key)
        (newbib/'biblio_top.bib').write_text('% Selection (duplicates of the main category files).\n\n'+'\n'.join(fmt(e) for e in top_entries),encoding='utf8')
        (dl/'biblio_top.bib').write_text('% Selected publications.\n\n'+'\n'.join(fmt(minimal(e)) for e in top_entries),encoding='utf8')
        (newbib/'biblio_all.bib').write_text('% Generated view only. Edit biblio_*.bib excluding top.\n\n'+'\n'.join(fmt(e) for e in combined),encoding='utf8')
        (dl/'biblio_all.bib').write_text('% Plain BibTeX citations (no metadata extras).\n\n'+'\n'.join(fmt(minimal(e)) for e in combined),encoding='utf8')
        for e in combined:(entriesdir/(e['key']+'.bib')).write_text(fmt(minimal(e)),encoding='utf8')
        (tmp/'bibliography_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        # Publish only after complete validation and after all derived files were generated.
        for f in newbib.glob('biblio_*.bib'):f.replace(BIB/f.name)
        downloads=BIB/'downloads';downloads.mkdir(parents=True,exist_ok=True)
        for f in dl.glob('*.bib'):f.replace(downloads/f.name)
        itemdir=downloads/'entries';itemdir.mkdir(exist_ok=True)
        generated_names={f.name for f in entriesdir.glob('*.bib')}
        for stale in itemdir.glob('*.bib'):
            if stale.name not in generated_names:stale.unlink()
        for f in entriesdir.glob('*.bib'):f.replace(itemdir/f.name)
        (ROOT/'data/reports').mkdir(parents=True,exist_ok=True)
        (tmp/'bibliography_report.json').replace(ROOT/'data/reports/bibliography_report.json')
    return pubs

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sync-dblp',action='store_true',help='Pull DBLP records (network; default offline)')
    ap.add_argument('--enrich-online',action='store_true',help='Fetch venue rankings and acceptance rates from external sources')
    ap.add_argument('--crossref-limit',type=int,default=35,help='Max Crossref title checks per online run (0 disables)')
    ap.add_argument('--dblp-xml',type=Path,help='Use local DBLP XML fixture instead of network')
    args=ap.parse_args(argv)
    bins,top,issues=load_entries()
    report={'generated_at':date.today().isoformat(),'source':'bibliography/biblio_*.bib','notes':issues,
            'new_dblp_publications':0,'bibliographic_fields_filled':0,'external_fields_updated':0,
            'warnings':[]}
    if args.sync_dblp or args.dblp_xml:
        raw=args.dblp_xml.read_bytes() if args.dblp_xml else download_xml(DEFAULT_PID,25)
        report['new_dblp_publications'],report['bibliographic_fields_filled']=import_dblp(bins,raw)
    if args.enrich_online and args.crossref_limit>0:
        checked,filled,errors=enrich_crossref(bins,args.crossref_limit)
        report['crossref_checks']=checked
        report['crossref_fields_filled']=filled
        report['warnings'].extend(errors)
    pubs=export_model(bins,top)
    if args.enrich_online:
        # Re-use tested source adapters from v5 but commit the results to BibTeX, not to JSON.
        from update_ratings import (enrich as update_ratings, fetch_core, fetch, parse_sjr_csv,
                                    parse_sjr_profile, SJR_URL, SJR_ALIASES)
        from update_acceptance import (enrich as update_acceptance, fetch_json as fetch_acceptance,
                                       VENUES, BASE as ACCEPTANCE_BASE, venue_id)
        cores=[];sjr={};sources={}
        try:cores=fetch_core()
        except Exception as exc:report['warnings'].append('CORE: '+str(exc))
        years={int(p['year']) for p in pubs if p['category']=='journals' and p['year'].isdigit()}
        for year in sorted({min(y-1,2025) for y in years if y>2000}):
            try:sjr[year]=parse_sjr_csv(fetch(SJR_URL+'?year='+str(year)+'&out=xls'))
            except Exception as exc:report['warnings'].append('SJR '+str(year)+': '+str(exc))
        try:
            cats=json.loads((ROOT/'data/sjr_categories.json').read_text(encoding='utf8'))
            # v5 files may contain nested mappings; adapter accepts category_overrides.
            from update_ratings import norm as rating_norm
            categories=cats.get('category_overrides',cats) if isinstance(cats,dict) else {}
        except Exception:categories={}
        profiles={}
        ids={str(table.get(SJR_ALIASES.get(sjr_norm(p.get('venue','')),sjr_norm(p.get('venue',''))),{}).get('source_id',''))
             for table in sjr.values() for p in pubs if p.get('category')=='journals'}
        for sid in ids:
            if not re.fullmatch(r'\d+',sid):continue
            try:
                url='https://www.scimagojr.com/journalsearch.php?q='+sid+'&tip=sid'
                profiles[sid]=parse_sjr_profile(fetch(url))
            except Exception as exc:report['warnings'].append('SCImago category history '+sid+': '+str(exc))
        try:update_ratings(pubs,cores,sjr,profiles=profiles,category_overrides=categories)
        except Exception as exc:report['warnings'].append('Ratings: '+str(exc))
        for key in sorted({venue_id(p.get('venue','')) for p in pubs if p['category']=='conferences'} & VENUES.keys()):
            area,name=VENUES[key]
            try:sources[key]=fetch_acceptance(ACCEPTANCE_BASE+area+'/'+name+'.json')
            except Exception as exc:report['warnings'].append('Acceptance '+key+': '+str(exc))
        update_acceptance(pubs,sources)
        report['external_fields_updated']=merge_enrichment(bins,pubs)
    failures,incomplete,_=validate(bins)
    if failures:raise ValueError('; '.join(failures))
    result=output_files(bins,top,report)
    print(json.dumps({'total':len(result),'added':report['new_dblp_publications'],'enriched_fields':report['external_fields_updated'],
                      'incomplete':len(incomplete),'warnings':len(report['warnings'])}))
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:
        print('ERROR: bibliography not published: '+str(exc),file=sys.stderr);raise SystemExit(1)

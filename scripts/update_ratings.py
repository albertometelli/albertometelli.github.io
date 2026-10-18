#!/usr/bin/env python3
"""Enrich DBLP records directly from the ICORE/CORE portal and SCImago exports.

No CV/legacy rating fields are read. Missing, blocked or ambiguous entries are
omitted (or a previously verified source snapshot is preserved).

ICORE: https://portal.core.edu.au/conf-ranks/ (official paginated HTML).
SCImago: https://www.scimagojr.com/journalrank.php?year=YYYY&out=xls
SCImago's 'xls' export has commonly been semicolon-delimited CSV; when the
provider changes format or presents a bot challenge, fail safely.
"""
from __future__ import annotations
import csv
import io
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

CORE_URL='https://portal.core.edu.au/conf-ranks/'
SJR_URL='https://www.scimagojr.com/journalrank.php'
CORE_TYPES={'A*','A','B','C','Australasian B','Australasian C','National/Regional','Journal Published'}
ALIAS={
 'neurips':'NeurIPS','advancesinneuralinformationprocessingsystems':'NeurIPS',
 'neuralinformationprocessingsystems':'NeurIPS','nips':'NeurIPS',
 'internationalconferenceonmachinelearning':'ICML','icml':'ICML',
 'associationfortheadvancementofartificialintelligence':'AAAI','aaaiconferenceonartificialintelligence':'AAAI','aaai':'AAAI',
 'internationaljointconferenceonartificialintelligence':'IJCAI','ijcai':'IJCAI',
 'internationalconferenceonartificialintelligenceandstatistics':'AISTATS',
 'internationalconferenceonartificialintelligenceandstatistic':'AISTATS',
 'artificialintelligenceandstatistics':'AISTATS','aistats':'AISTATS',
 'conferenceonlearningtheory':'COLT','colt':'COLT',
 'uncertaintyinartificialintelligence':'UAI','uai':'UAI',
 'internationalconferenceonlearningrepresentations':'ICLR','iclr':'ICLR',
}
SJR_ALIASES={
 'jmlr':'journalofmachinelearningresearch',
 'jmachlearnres':'journalofmachinelearningresearch',
 'mlj':'machinelearning',
 'jair':'journalofartificialintelligenceresearch',
 'ieeetransactionsonneuralnetworksandlearningsystems':'ieeetransactionsonneuralnetworksandlearningsystems',
}

def norm(t):
    t=unicodedata.normalize('NFKD',str(t))
    return re.sub('[^a-z0-9]','', ''.join(c for c in t if not unicodedata.combining(c)).lower())

def core_key(venue):
    plain=norm(venue)
    if plain in ALIAS:return ALIAS[plain]
    # Only recognizable standalone conference acronyms; no fuzzy containment.
    for candidate in ('ICML','NeurIPS','AAAI','IJCAI','AISTATS','COLT','UAI','ICLR'):
        if re.search(r'(?<![a-zA-Z])'+re.escape(candidate)+r'(?![a-zA-Z])',venue,re.I):return candidate
    return ''

def fetch(url,timeout=40):
    request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; MetelliSiteRatings/1.0)',
                                                'Accept':'text/html,text/csv,application/octet-stream'})
    with urllib.request.urlopen(request,timeout=timeout) as response:
        raw=response.read(15_000_000+1)
    if len(raw)>15_000_000:raise ValueError('Source export exceeds size limit')
    return raw

def parse_core_page(raw):
    doc=BeautifulSoup(raw,'html.parser')
    table=next((t for t in doc.find_all('table') if 'acronym' in t.get_text(' ',strip=True).lower()
                and 'rank' in t.get_text(' ',strip=True).lower()),None)
    if table is None:raise ValueError('ICORE rankings table not found (layout or authorization changed)')
    rows=[]
    for tr in table.select('tr'):
        cells=tr.find_all('td',recursive=False)
        if len(cells)<4:continue
        title,acronym,source,rank=[c.get_text(' ',strip=True) for c in cells[:4]]
        yearmatch=re.search(r'(20\d{2})',source)
        if not yearmatch or rank not in CORE_TYPES:continue
        rows.append({'title':title,'acronym':acronym,'source':source,
                     'release_year':int(yearmatch.group(1)),'rank':rank})
    return rows

def fetch_core(max_pages=60):
    result=[]
    for page in range(1,max_pages+1):
        url=CORE_URL+'?'+urllib.parse.urlencode({'by':'all','page':page,'sort':'dfor1','source':'all'})
        raw=fetch(url)
        text=raw.decode('utf-8','replace')
        found=re.search(r'Showing results\s+(\d+)\s*[-–]\s*(\d+)\s+of\s+(\d+)',
                         BeautifulSoup(raw,'html.parser').get_text(' ',strip=True),re.I)
        rows=parse_core_page(raw)
        if not rows and not result:raise ValueError('ICORE portal returned no ranked records')
        result.extend(rows)
        if found and int(found.group(2))>=int(found.group(3)):return result
        if not found and len(rows)<50:return result
        if page>=max_pages:raise RuntimeError('ICORE pagination exceeded safety limit')
        time.sleep(.12)
    return result

def parse_sjr_csv(raw):
    decoded=None
    for codec in ('utf-8-sig','utf-8','latin-1'):
        try:decoded=raw.decode(codec);break
        except UnicodeDecodeError:pass
    if decoded is None:raise ValueError('Cannot decode SCImago data')
    if decoded.startswith('PK\x03\x04') or '<html' in decoded[:500].lower():
        raise ValueError('SCImago did not return the public CSV export')
    first=decoded.splitlines()[0] if decoded.splitlines() else ''
    separator=';' if first.count(';')>=first.count(',') else ','
    reader=csv.DictReader(io.StringIO(decoded),delimiter=separator)
    headers=reader.fieldnames or []
    namecol=next((h for h in headers if norm(h)=='title'),None)
    rankcol=next((h for h in headers if norm(h) in ('bestquartile','sjrbestquartile')),None)
    scorecol=next((h for h in headers if norm(h)=='sjr'),None)
    sourcecol=next((h for h in headers if norm(h) in ('sourceid','scimagosourceid')),None)
    if not namecol or not (rankcol or scorecol):
        raise ValueError('SCImago fields Title/SJR/Best Quartile missing; source format changed')
    results={}
    for row in reader:
        title=(row.get(namecol) or '').strip()
        if not title:continue
        rank=(row.get(rankcol) or '').strip().upper() if rankcol else ''
        if rank not in ('Q1','Q2','Q3','Q4'):rank=''
        score=(row.get(scorecol) or '').strip().replace(',','.') if scorecol else ''
        if score and not re.fullmatch(r'\d+(\.\d+)?',score):score=''
        if not (rank or score):continue
        results[norm(title)]={'best_quartile':rank,'score':score,'title':title,'source_id':(row.get(sourcecol) or '').strip() if sourcecol else ''}
    if not results:raise ValueError('Empty SCImago export')
    return results

def pick_core(venue,year,rows):
    acronym=core_key(venue)
    if not acronym:return None
    candidates=[r for r in rows if r['release_year']<=year and norm(r['acronym'])==norm(acronym)]
    # Reject equal-year multiple conflicting ranks rather than choosing arbitrarily.
    if not candidates:return None
    latest=max(r['release_year'] for r in candidates)
    current=[r for r in candidates if r['release_year']==latest]
    ranks={r['rank'] for r in current}
    if len(ranks)!=1:return None
    source=sorted(current,key=lambda r:('ICORE' not in r['source'],r['source']))[0]
    return {'value':f'{source["rank"]} ({source["source"]})',
            'source_url':CORE_URL,'source_year':latest,'provider':'ICORE / CORE'}

def parse_sjr_profile(raw):
    """Extract SCImago *subject-category* quartiles per year from a journal page.

    An exported 'SJR Best Quartile' is NOT interchangeable with the Artificial
    Intelligence quartile, and must never be used as a fallback.
    """
    soup=BeautifulSoup(raw,'html.parser')
    result={}
    for tr in soup.select('tr'):
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'],recursive=False)]
        if len(cells)>=3 and re.fullmatch(r'(?:19|20)\d{2}',cells[1]) and re.fullmatch('Q[1-4]',cells[2],re.I):
            result[(cells[0].casefold(),int(cells[1]))]=cells[2].upper()
    if not result:
        # SCImago sometimes renders this table without <tr> tags.
        text=soup.get_text(' ',strip=True)
        match=re.search(r'Category\s+Year\s+Quartile(.*?)\bSJR\b',text,re.I|re.S)
        if match:
            for line in re.finditer(r'([A-Za-z][A-Za-z&() ,/\-]{2,55}?)\s+((?:19|20)\d{2})\s+(Q[1-4])\b',match.group(1)):
                result[(line.group(1).strip().casefold(),int(line.group(2)))]=line.group(3)
    if not result:raise ValueError('SCImago category / year / quartile table not found')
    return result

def pick_sjr(venue, year, data, profiles=None, category_overrides=None):
    """Select AI category, unless another named category is configured or unique."""
    key=SJR_ALIASES.get(norm(venue),norm(venue))
    entry=data.get(key)
    if not entry:return None
    profiles=profiles or {}
    category_overrides=category_overrides or {}
    source_id=str(entry.get('source_id',''))
    catalog=profiles.get(source_id, {})
    year_rows={category:quartile for (category,edition),quartile in catalog.items() if edition==year}
    preferred=category_overrides.get(norm(venue),'Artificial Intelligence').casefold()
    if preferred in year_rows: category=preferred
    elif 'artificial intelligence' in year_rows and norm(venue) not in category_overrides:category='artificial intelligence'
    elif norm(venue) not in category_overrides and len(year_rows)==1:category=next(iter(year_rows))
    else:return None  # Don't mislabel 'Best Quartile' as AI Q1.
    rank=year_rows[category]
    score=entry.get('score','')
    page_url=SJR_URL+f'?year={year}'
    if source_id and re.fullmatch(r'\d+',source_id):
        page_url='https://www.scimagojr.com/journalsearch.php?'+urllib.parse.urlencode({'q':source_id,'tip':'sid'})
    display_category='Artificial Intelligence' if category=='artificial intelligence' else next((k.title() for k in year_rows if k==category),category.title())
    return {'value':f'{rank} · {display_category} ({year})',
            'quartile':rank,'category':display_category,
            'score':score, 'source_url':page_url,'source_year':year,
            'provider':'SCImago — journal subject-category history',
            'category_source':'official-journal-profile'}

def enrich(pubs,core_rows,sjr_data_by_year,profiles=None,category_overrides=None):
    count=0
    for pub in pubs:
        year=int(pub.get('year') or 0)
        # Strip all legacy/CV-derived ratings (GGS is unsupported by these sources).
        for field in ('core','ggs','sjr'):
            pub.pop(field,None)
        previous=pub.get('ratings',{}) if pub.get('rating_provider')=='official-sources' else {}
        fresh={}
        if pub.get('category')=='conferences' and core_rows is not None:
            rating=pick_core(pub.get('venue',''),year,core_rows)
            if rating:fresh['core']=rating
        if pub.get('category')=='journals':
            # SCImago year Y is released in Y+1: do not use data published after
            # the publication year. Exact month of publication is not available.
            eligible=[y for y in sjr_data_by_year if y+1<=year]
            for snapshot in sorted(eligible,reverse=True):
                rating=pick_sjr(pub.get('venue',''),snapshot,sjr_data_by_year[snapshot],profiles,category_overrides)
                if rating:
                    fresh['sjr']=rating
                    break
        # Keep only verified direct-source cached ratings and only if source
        # edition cannot postdate the paper.
        for kind,record in previous.items():
            if kind not in ('core','sjr') or not isinstance(record,dict):continue
            age=int(record.get('source_year') or 0)
            if kind=='core' and age>year:continue
            if kind=='sjr' and (age+1>year or record.get('category_source')!='official-journal-profile'):continue
            if kind not in fresh and record.get('source_url') and record.get('value'):
                fresh[kind]=record
        if fresh:
            pub['ratings']=fresh
            pub['rating_provider']='official-sources'
            count+=1
        else:
            pub.pop('ratings',None)
            pub.pop('rating_provider',None)
        # metadata_source can still refer to author order and acceptance rate.
    return count


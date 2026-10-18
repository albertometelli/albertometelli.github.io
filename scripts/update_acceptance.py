#!/usr/bin/env python3
"""Read venue-year main-track acceptance statistics from OpenAccept's public data.

The metadata repository contains source URLs when available; we retain them
alongside the OpenAccept record. No acceptance rate is inferred from DBLP paper
counts. A downloaded rate always replaces an inherited/older rate for that
venue-year. Unknown venues are left unmodified.
"""
from __future__ import annotations
from datetime import date
import json
import re
import urllib.request
from update_ratings import core_key

BASE='https://raw.githubusercontent.com/OpenAccept/openaccept-metadata/master/'
# Strict, explicit mapping prevents confusing workshops/tracks with main conferences.
VENUES={'NeurIPS':('ai','NeurIPS'), 'ICML':('ai','ICML'), 'AAAI':('ai','AAAI'),
        'IJCAI':('ai','IJCAI'), 'AISTATS':('ai','AISTATS'), 'ICLR':('ai','ICLR'),
        'COLT':('ai','COLT'), 'UAI':('ai','UAI'), 'ACL':('ai','ACL'),
        'ECAI':('ai','ECAI')}
OFFICIAL_FACTS={
    ('NeurIPS',2024):('https://media.neurips.cc/Conferences/NeurIPS2024/NeurIPS2024-Fact_Sheet.pdf',4037,15671),
    ('NeurIPS',2025):('https://media.neurips.cc/Conferences/NeurIPS2025/press/NeurIPS2025-Fact_Sheet.pdf',5290,21575),
}

def venue_id(value):
    key=core_key(value)
    if key in VENUES:return key
    for key in VENUES:
        if re.search(r'(?<![a-z])'+re.escape(key)+r'(?![a-z])',value,re.I):return key
    return ''

def fetch_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'AcademicWebsite/5.0 (public conference statistics)','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=25) as res:
        return json.load(res)

def rate_for_year(payload,year,venue,record_url):
    if str(payload.get('name','')).casefold()!=venue.casefold():
        raise ValueError('Conference acronym mismatch')
    candidates=[r for r in payload.get('yearly_data',[]) if str(r.get('year'))==str(year)]
    if len(candidates)!=1:return None
    item=candidates[0]
    a,s=item.get('accepted'),item.get('submitted')
    if any(isinstance(v,bool) or not isinstance(v,int) for v in (a,s)) or not (0<a<=s):
        return None
    source=item.get('source')
    if not (isinstance(source,str) and source.startswith('https://')):source=record_url
    provider='OpenAccept metadata (public compilation)'
    # Conference-authored facts have precedence for the years documented above.
    if (venue,year) in OFFICIAL_FACTS:
        link,a,s=OFFICIAL_FACTS[(venue,year)]
        source=link
        provider='Conference official fact sheet (supersedes conflicting secondary totals)'
    return {'acceptance_rate':f'Acceptance rate: {a}/{s} ({a/s*100:.1f}%)',
            'acceptance':{'accepted':a,'submitted':s,'rate_percent':round(100*a/s,2),
                'venue':venue,'year':year,'track':'Main research track',
                'source_url':source,'record_url':record_url,'provider':provider,
                'retrieved_at':date.today().isoformat()}}

def enrich(pubs,source_by_venue):
    updated=0
    for p in pubs:
        if p.get('category')!='conferences':continue
        if re.search(r'workshop|tutorial|symposium|demo|poster session',p.get('venue',''),re.I):continue
        v=venue_id(p.get('venue',''))
        if not v or v not in source_by_venue:continue
        try:y=int(p.get('year'))
        except (ValueError,TypeError):continue
        area,name=VENUES[v]
        url=f'https://github.com/OpenAccept/openaccept-metadata/blob/master/{area}/{name}.json'
        result=rate_for_year(source_by_venue[v],y,v,url)
        if result:
            p.update(result)
            updated+=1
    return updated


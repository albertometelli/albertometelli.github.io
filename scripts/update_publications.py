#!/usr/bin/env python3
"""DBLP parsing and download helpers used by the canonical BibTeX pipeline."""
from __future__ import annotations

import html
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

DEFAULT_PID = '209/4941'
ALLOWED_TYPES = {'article', 'inproceedings', 'incollection', 'book', 'phdthesis', 'mastersthesis', 'proceedings', 'data', 'informal'}


def plain_text(node: ET.Element | None) -> str:
    if node is None:
        return ''
    return re.sub(r'\s+', ' ', html.unescape(''.join(node.itertext()))).strip().rstrip(' .')


def classify(record_type: str, record: ET.Element) -> str:
    journal = plain_text(record.find('journal')).lower()
    if record_type == 'article':
        if journal in ('corr', 'arxiv', 'arxiv preprint') or journal.startswith('arxiv'):
            return 'preprints'
        return 'journals'
    if record_type == 'inproceedings':
        return 'conferences'
    if record_type == 'book':
        return 'books'
    if record_type == 'incollection':
        return 'chapters'
    if record_type in ('phdthesis', 'mastersthesis'):
        return 'theses'
    return 'other'


def publication_venue(record_type: str, record: ET.Element) -> str:
    fields = {
        'article': ('journal', 'booktitle'),
        'inproceedings': ('booktitle', 'journal'),
        'incollection': ('booktitle', 'publisher'),
        'book': ('publisher', 'series'),
        'phdthesis': ('school',),
        'mastersthesis': ('school',),
    }.get(record_type, ('booktitle', 'journal', 'publisher', 'school'))
    for field in fields:
        name = plain_text(record.find(field))
        if name:
            return name
    return 'DBLP bibliography'


def sort_key(pub: dict) -> tuple:
    priority = {'conferences': 0, 'journals': 1, 'books': 2, 'chapters': 3, 'preprints': 4, 'theses': 5, 'other': 6}
    year = int(pub['year']) if pub['year'].isdigit() else 0
    return (-year, priority.get(pub['category'], 99), pub['title'].casefold())


def prefer_ee(links: list[str]) -> str | None:
    # DBLP can expose several electronic editions. Prefer openly accessible venues.
    def rank(link: str) -> tuple[int, int]:
        link_l = link.lower()
        domains = ('proceedings.mlr.press', 'jmlr.org', 'papers.neurips.cc', 'proceedings.neurips.cc', 'openreview.net', 'arxiv.org', 'doi.org')
        return next((i for i, domain in enumerate(domains) if domain in link_l), len(domains)), len(link)
    choices = [link for link in links if link.startswith(('https://', 'http://'))]
    return min(choices, key=rank) if choices else None


def record_to_json(element: ET.Element) -> dict | None:
    record_type = element.tag.removeprefix('{http://dblp.org/rdf/schema#}')
    if record_type not in ALLOWED_TYPES:
        return None
    title = plain_text(element.find('title'))
    year = plain_text(element.find('year'))
    if not title or not year:
        return None
    authors = [plain_text(node) for node in element.findall('author')]
    if not authors:
        authors = [plain_text(node) for node in element.findall('editor')]
    authors = [a for a in authors if a]
    key = element.get('key', '')
    ee = [plain_text(child) for child in element.findall('ee')]
    dblp = f'https://dblp.org/rec/{key}' if key else ''
    pub = {
        'title': title,
        'authors': authors,
        'year': year,
        'venue': publication_venue(record_type, element),
        'category': classify(record_type, element),
        'dblp_key': key,
        'dblp_url': dblp,
        'bibtex_url': f'{dblp}.bib' if dblp else '',
    }
    primary = prefer_ee(ee)
    if primary:
        pub['paper_url'] = primary
    return pub


def parse_dblp_xml(source: bytes, pid: str = DEFAULT_PID, overrides: dict | None = None) -> list[dict]:
    try:
        root = ET.fromstring(source)
    except ET.ParseError as exc:
        raise ValueError(f'Invalid XML returned by DBLP: {exc}') from exc
    if root.tag != 'dblpperson':
        raise ValueError(f'Expected <dblpperson> XML, got <{root.tag}>')
    returned_pid = root.get('pid', '')
    if returned_pid and returned_pid != pid:
        raise ValueError(f'DBLP author mismatch: expected {pid}, got {returned_pid}')
    overrides = overrides or {}
    pubs: list[dict] = []
    seen_keys: set[str] = set()
    for wrapper in root.findall('r'):
        for node in wrapper:
            pub = record_to_json(node)
            if not pub:
                continue
            key = pub.get('dblp_key', '')
            if key in seen_keys:
                continue
            seen_keys.add(key)
            custom = overrides.get(key) or overrides.get(pub['title']) or {}
            if custom:
                # Preserve DBLP's bibliographic fields; only supplement links.
                if isinstance(custom.get('extra_links'), dict):
                    pub['extra_links'] = custom['extra_links']
                if isinstance(custom.get('paper_url'), str):
                    pub['paper_url'] = custom['paper_url']
                # Manually reviewed exceptions take precedence, and are kept
                # in a separate file so automated refreshes never erase them.
                for field in ('acceptance_rate','alphabetical_order',
                              'equal_contribution_authors','distinction','category','note'):
                    if field in custom: pub[field] = custom[field]
            pubs.append(pub)
    # Suppress CoRR-only copies if a formal publication with the same title exists.
    formal_titles = {
        normalize_title(p['title']) for p in pubs if p['category'] != 'preprints'
    }
    pubs = [p for p in pubs if p['category'] != 'preprints' or normalize_title(p['title']) not in formal_titles]
    pubs.sort(key=sort_key)
    if not pubs:
        raise ValueError('DBLP returned zero bibliographic entries; refusing to overwrite the existing archive.')
    return pubs


def normalize_title(value: str) -> str:
    import unicodedata
    chars=unicodedata.normalize('NFKD',value)
    chars=''.join(c for c in chars if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '', chars.lower())


def download_xml(pid: str, timeout: float, retries: int = 3) -> bytes:
    url = f'https://dblp.org/pid/{pid}.xml'
    for attempt in range(retries):
        request = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'MetelliAcademicWebsite/1.0 (static bibliography updater)',
                'Accept': 'application/xml, text/xml;q=0.9',
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read()
            if not payload:
                raise ValueError('Received an empty file from DBLP')
            return payload
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            if attempt == retries - 1:
                raise RuntimeError(f'DBLP request failed after {retries} attempts: {exc}') from exc
            wait = 2 ** attempt
            print(f'DBLP request failed ({exc}); retrying in {wait}s...', file=sys.stderr)
            time.sleep(wait)
    raise AssertionError('unreachable')


if __name__ == '__main__':
    # Keep the historical command useful without restoring the removed JSON flow.
    from bib_pipeline import main as canonical_sync
    raise SystemExit(canonical_sync(['--sync-dblp']))

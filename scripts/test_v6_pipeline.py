#!/usr/bin/env python3
"""Offline, deterministic regression checks for the canonical BibTeX pipeline."""
import copy
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).parent))
from bib_pipeline import (ROOT, BIB, load_entries, validate, export_model, minimal,
                          metadata_from_fields, import_dblp, norm, summary,
                          category_for_journal, entry_sort_key)
from bibtex_utils import fmt, parse_entries

class CanonicalBibTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bins,cls.top,cls.issues=load_entries()
        cls.pubs=export_model(cls.bins,cls.top)

    def test_archive_deduplicated_and_valid(self):
        problems,incomplete,count=validate(self.bins)
        self.assertFalse(problems)
        self.assertGreaterEqual(count,120)
        self.assertEqual(len({(p['category'],norm(p['title'])) for p in self.pubs}),count)

    def test_conferences_inproceedings(self):
        self.assertTrue(self.bins['c'])
        self.assertTrue(all(e['type']=='inproceedings' for e in self.bins['c']))

    def test_canonical_files_are_sorted_by_recency_and_occurrence(self):
        for entries in self.bins.values():
            self.assertEqual(entries,sorted(entries,key=entry_sort_key))
        current=max(int(p['year']) for p in self.pubs if p['category']=='conferences')
        current_conferences=[p for p in self.pubs if p['category']=='conferences' and int(p['year'])==current]
        statuses=[p.get('status')=='To Appear' for p in current_conferences]
        self.assertEqual(statuses,sorted(statuses,reverse=True))

    def test_private_fields_never_exported(self):
        checked=0
        for entries in self.bins.values():
            for e in entries:
                full=e['fields'];public=fmt(minimal(e)).lower()
                self.assertNotIn('rankcore =',public)
                self.assertNotIn('ranksjr =',public)
                self.assertNotIn('acceptance =',public)
                self.assertNotIn('poster =',public)
                self.assertNotIn('slides =',public)
                self.assertNotIn('note =',public)
                self.assertEqual(len(parse_entries(fmt(minimal(e)))),1)
                checked+=1
        self.assertGreaterEqual(checked,120)

    def test_downloads_are_exactly_clean_canonical_entries(self):
        for entries in self.bins.values():
            for e in entries:
                downloaded=BIB/'downloads/entries'/f'{e["key"]}.bib'
                self.assertTrue(downloaded.exists(),str(downloaded))
                self.assertEqual(parse_entries(downloaded.read_text())[0]['fields'],minimal(e)['fields'])

    def test_ai_default_and_explicit_sjr_exception(self):
        self.assertEqual(category_for_journal('Artificial Intelligence'),'Artificial Intelligence')
        self.assertEqual(category_for_journal('iScience'),'Multidisciplinary')

    def test_scimago_future_editions_excluded_from_q1(self):
        pubs=copy.deepcopy(self.pubs)
        p=next(p for p in pubs if p['category']=='journals')
        p['ratings']['sjr']={'quartile':'Q1','chronologically_eligible':False}
        counts=summary([p])
        self.assertEqual(counts['q1_journal_articles'],0)

    def test_incremental_dblp_updates_fields_but_preserves_manual_notes_and_keys(self):
        record='''<dblpperson pid="209/4941"><r><inproceedings key="conf/test/Metelli26">
        <author>Alberto Maria Metelli</author><title>Conservative Learning for A Test</title>
        <year>2026</year><booktitle>International Conference on Machine Learning (ICML)</booktitle>
        <volume>325</volume><pages>12-23</pages><ee>https://doi.org/10.1234/unique-test-record</ee>
        </inproceedings></r></dblpperson>'''
        bins=copy.deepcopy(self.bins)
        bins['c'].append({'key':'mycanonical2026','type':'inproceedings','group':'c','fields':{
            'title':'Conservative Learning for A Test','author':'Alberto Maria Metelli','booktitle':'ICML',
            'year':'2026','note':'User authored note','slides':'https://example.org/slides.pdf'}})
        added,filled=import_dblp(bins,record.encode())
        self.assertEqual(added,0)
        item=next(e for e in bins['c'] if e['key']=='mycanonical2026')
        self.assertEqual(item['fields']['volume'],'325')
        self.assertEqual(item['fields']['note'],'User authored note')
        self.assertEqual(item['fields']['slides'],'https://example.org/slides.pdf')
        self.assertIn('10.1234/',item['fields']['doi'])
        self.assertGreater(filled,0)

    def test_website_routes_and_static_map(self):
        pages=['index.html','research.html','teaching.html','positions.html','contacts.html','publications.html']
        for name in pages:
            doc=BeautifulSoup((ROOT/name).read_text(), 'html.parser')
            self.assertEqual(len(doc.find_all('h1')),1)
            self.assertTrue(doc.find('main'))
        about=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
        for ident in ('0000-0002-3424-5212','57195947711','2074428'):
            self.assertIn(ident,str(about))
        self.assertNotIn('RESEARCH · REINFORCEMENT LEARNING · ONLINE LEARNING',str(about))
        contact=BeautifulSoup((ROOT/'contacts.html').read_text(),'html.parser')
        self.assertEqual(len(contact.select('main>section')),1)
        map_frame=contact.select_one('.map-area iframe')
        self.assertIsNotNone(map_frame)
        self.assertIn('maps?q=',map_frame.get('src') or map_frame.get('data-src',''))
        self.assertFalse(map_frame.has_attr('src'))
        self.assertFalse(map_frame.has_attr('onload'))
        site_script=(ROOT/'assets/js/site.js').read_text()
        self.assertIn("frame.addEventListener('load'",site_script)
        self.assertIn("mapFrame.classList.add('is-loaded')",site_script)
        self.assertEqual(len(BeautifulSoup((ROOT/'positions.html').read_text(),'html.parser').select('main>section')),1)
        self.assertFalse(BeautifulSoup((ROOT/'research.html').read_text(),'html.parser').select('.project-logo'))
        team=BeautifulSoup((ROOT/'team.html').read_text(),'html.parser')
        team_links={link.get('href') for link in team.select('.person a[href]')}
        expected_team_links={
            'https://scholar.google.com/citations?user=CugD-ogAAAAJ&hl=it&oi=ao',
            'https://montenegroalessandro.github.io/',
            'https://scholar.google.com/citations?user=TMHon60AAAAJ&hl=it&oi=ao',
            'https://www.linkedin.com/in/drago-simone',
            'https://scholar.google.com/citations?user=jsxnVbUAAAAJ&hl=it&oi=ao',
            'https://www.linkedin.com/in/federico-corso-1109311aa/',
            'https://scholar.google.com/citations?user=GwD8QoQAAAAJ&hl=it&oi=ao',
            'https://www.linkedin.com/in/migwings/',
            'https://github.com/m1gwings',
            'https://scholar.google.com/citations?user=pXsVWq4AAAAJ&hl=it&oi=ao',
            'https://github.com/RVenturelli01',
            'https://www.linkedin.com/in/riccardoventurelli/',
            'https://www.linkedin.com/in/maria-cristina-centorame',
            'https://www.linkedin.com/in/motticaterina/',
            'https://mttcrn.github.io/',
        }
        self.assertLessEqual(expected_team_links,team_links)
        assistants=team.select_one('h2:-soup-contains("Research assistants")').find_parent('section').select('.person')
        self.assertEqual([person.select_one('h3').get_text(' ',strip=True).removesuffix(' ↗') for person in assistants],
                         ['Riccardo Venturelli','Maria Cristina Centorame','Caterina Motti'])
        self.assertEqual([person.select_one('.person-avatar img').get('src') for person in assistants],
                         ['assets/team/riccardo-venturelli.webp','assets/team/maria-cristina-centorame.webp','assets/team/caterina-motti.webp'])
        self.assertTrue(all(person.select_one('p').get_text(strip=True)=='Research Assistant' for person in assistants))
        team_model=json.loads((ROOT/'data/team.json').read_text())
        manifest_members=[member for section in team_model['sections'] for member in section['members']]
        self.assertEqual(len(team.select('.person')),len(manifest_members))
        self.assertTrue(all(image.get('width')=='128' and image.get('height')=='128'
                            for image in team.select('.person-avatar img')))
        self.assertTrue(all((ROOT/member['photo']).exists() and member['photo'].endswith('.webp')
                            for member in manifest_members))

    def test_shared_accessibility_metadata_and_assets(self):
        pages=['index.html','research.html','publications.html','teaching.html','team.html',
               'positions.html','contacts.html','privacy.html']
        for name in pages:
            source=(ROOT/name).read_text()
            doc=BeautifulSoup(source,'html.parser')
            self.assertEqual(doc.select_one('link[rel="stylesheet"]').get('href'),'assets/css/style.css?v=20261018')
            self.assertEqual(doc.select_one('script[src]').get('src'),'assets/js/site.js?v=20261018')
            self.assertIsNotNone(doc.select_one('#site-status[aria-live="polite"]'))
            self.assertTrue(doc.select_one('.theme-toggle').has_attr('aria-pressed'))
        privacy=(ROOT/'privacy.html').read_text()
        self.assertIn('content="Privacy &amp; cookies — Alberto Maria Metelli"',privacy)
        contact=BeautifulSoup((ROOT/'contacts.html').read_text(),'html.parser')
        self.assertIn('Office 039',contact.get_text(' ',strip=True))
        script=(ROOT/'assets/js/site.js').read_text()
        self.assertIn("event.key === 'Escape'",script)
        self.assertIn('Try loading map again',script)
        self.assertIn("announce('Citation copied to the clipboard.')",script)

    def test_summary_values_without_inventing_missing_ratings(self):
        counts=summary(self.pubs)
        self.assertEqual(counts['total'],counts['conferences']+counts['journals'])
        self.assertLess(counts['total'],len(self.pubs))
        self.assertLessEqual(counts['a_star_conference_papers'],counts['rated_conferences'])
        self.assertLessEqual(counts['q1_journal_articles'],counts['rated_journals'])

    def test_publications_are_prerendered_without_runtime_data_fetch(self):
        self.assertFalse((ROOT/'data/publications.json').exists())
        page=BeautifulSoup((ROOT/'publications.html').read_text(), 'html.parser')
        visible=[p for p in self.pubs if p['category']!='under-review']
        self.assertEqual(len(page.select('.pub-item')),len(visible))
        self.assertFalse(page.select('[data-category="under-review"]'))
        self.assertFalse(page.select('[data-filter="under-review"]'))
        self.assertFalse(page.select('#pub-topic'))
        self.assertFalse(page.select('#pub-share'))
        self.assertFalse(page.select('.pub-intro-meta'))
        self.assertEqual(len(page.select('.metric-grid .metric')),5)
        self.assertEqual(page.select_one('#pub-summary-title').get_text(' ',strip=True),'Scientific productivity')
        breakdowns=[node.get_text(' ',strip=True) for node in page.select('.metric-breakdown')]
        self.assertEqual(len(breakdowns),2)
        self.assertTrue(breakdowns[0].startswith('Selected conferences:'))
        self.assertTrue(breakdowns[1].startswith('Selected journals:'))
        self.assertNotIn('Publication counts and classifications are generated at build time',(ROOT/'publications.html').read_text())
        self.assertFalse(page.select('.metric-source'))
        venue_links={link.get_text(' ',strip=True):link.get('href') for link in page.select('.pub-legend a')}
        self.assertEqual(venue_links.get('CORE/ICORE'),'https://portal.core.edu.au/conf-ranks/')
        self.assertEqual(venue_links.get('SCImago SJR'),'https://www.scimagojr.com/')
        self.assertTrue(page.select('.recognition-tag'))
        self.assertFalse(page.select('.recognition-tag > span'))
        self.assertTrue(all(status.parent.get('class')==['pub-metadata'] for status in page.select('.pub-status')))
        for links in page.select('.pub-links'):
            labels=[node.get_text(' ',strip=True) for node in links.find_all(recursive=False)]
            self.assertEqual(labels[-2:],['BibTeX ↓','Copy citation'])
        self.assertEqual(len(page.select('.home-pub')),0)
        self.assertTrue(all(item.get('data-category') for item in page.select('.pub-item')))
        script=(ROOT/'assets/js/site.js').read_text()
        self.assertNotIn("fetch('data/publications.json'",script)
        self.assertNotIn("fetch('data/metrics.json'",script)
        home=BeautifulSoup((ROOT/'index.html').read_text(), 'html.parser')
        self.assertEqual(len(home.select('#home-publications .home-pub')),5)
        source=(ROOT/'publications.html').read_text()
        article_lines=[line for line in source.splitlines() if line.startswith('<article class="pub-item"')]
        self.assertEqual(len(article_lines),len(visible))
        self.assertIn('</article>\n\n<article class="pub-item"',source)

if __name__=='__main__':unittest.main()

#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from update_ratings import parse_sjr_csv,parse_sjr_profile,pick_sjr,enrich
from update_acceptance import rate_for_year,enrich as enrich_acceptance
from bib_pipeline import summary
from bibtex_utils import parse_entries,fmt

class AcceptanceTests(unittest.TestCase):
    def test_verified_conference_year(self):
        src={'name':'NeurIPS','yearly_data':[{'year':2025,'submitted':21575,'accepted':5290}]}
        p=rate_for_year(src,2025,'NeurIPS','https://example.org/origin.json')
        self.assertEqual(p['acceptance']['accepted'],5290)
        self.assertEqual(p['acceptance']['track'],'Main research track')
        self.assertAlmostEqual(p['acceptance']['rate_percent'],24.52)
        self.assertIn('2025-Fact_Sheet.pdf',p['acceptance']['source_url'])
        self.assertIsNone(rate_for_year(src,2024,'NeurIPS','https://x'))
    def test_no_rates_for_workshops(self):
        pub={'category':'conferences','venue':'NeurIPS Workshop','year':'2025'}
        self.assertEqual(enrich_acceptance([pub],{'NeurIPS':{'name':'NeurIPS','yearly_data':[{'year':2025,'accepted':5290,'submitted':21575}]}}),0)
        self.assertNotIn('acceptance',pub)

class ScimagoCategoryTests(unittest.TestCase):
    RAW=b'Sourceid;Title;SJR;SJR Best Quartile\n123;Test Journal;3.00;Q1\n456;Second Journal;1.00;Q1\n'
    PROFILE=b'''<html><table><tr><th>Category</th><th>Year</th><th>Quartile</th></tr>
    <tr><td>Artificial Intelligence</td><td>2024</td><td>Q2</td></tr>
    <tr><td>Computer Science Applications</td><td>2024</td><td>Q1</td></tr>
    <tr><td>Artificial Intelligence</td><td>2023</td><td>Q1</td></tr></table></html>'''
    def test_not_best_quartile(self):
        data=parse_sjr_csv(self.RAW)
        self.assertIsNone(pick_sjr('Test Journal',2024,data))
        got=pick_sjr('Test Journal',2024,data,{'123':parse_sjr_profile(self.PROFILE)})
        self.assertEqual(got['quartile'],'Q2')
        self.assertEqual(got['category'],'Artificial Intelligence')
        self.assertEqual(got['category_source'],'official-journal-profile')
    def test_overridden_category(self):
        data=parse_sjr_csv(self.RAW)
        profiles={'123':parse_sjr_profile(self.PROFILE)}
        got=pick_sjr('Test Journal',2024,data,profiles,{'testjournal':'Computer Science Applications'})
        self.assertEqual(got['quartile'],'Q1')
        self.assertEqual(got['category'],'Computer Science Applications')
    def test_time_consistency_and_count(self):
        data=parse_sjr_csv(self.RAW)
        p={'title':'X','venue':'Test Journal','year':'2025','category':'journals'}
        enrich([p],None,{2024:data},{'123':parse_sjr_profile(self.PROFILE)})
        self.assertEqual(p['ratings']['sjr']['quartile'],'Q2')
        a={'category':'conferences','ratings':{'core':{'value':'A* (CORE2023)','source_url':'https://www.core.edu.au/'}}}
        self.assertEqual(summary([p,a])['a_star_conference_papers'],1)
        self.assertEqual(summary([p,a])['q1_journal_articles'],0)

class BibTests(unittest.TestCase):
    def test_nested_and_accented_bibtex(self):
        x='@inproceedings{demo, title={A {POMDP} and model}, author={Fran\\c{c}ois and Alberto Maria Metelli}, year={2025}, acceptance={Accepted 500/2000 (25\\%)}}'
        entries=parse_entries(x)
        self.assertEqual(len(entries),1)
        self.assertIn('POMDP',entries[0]['fields']['title'])
        self.assertEqual(parse_entries(fmt(entries[0]))[0]['fields'],entries[0]['fields'])
if __name__=='__main__':unittest.main()

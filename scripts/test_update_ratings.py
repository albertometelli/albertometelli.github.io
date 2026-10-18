#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from update_ratings import parse_core_page,parse_sjr_csv,parse_sjr_profile,pick_core,pick_sjr,enrich

class TestOfficialRatings(unittest.TestCase):
    @staticmethod
    def portal():
        return b'''<html><table><tr><th>Title</th><th>Acronym</th><th>Source</th><th>Rank</th></tr>
        <tr><td>International Conference on Machine Learning</td><td>ICML</td><td>CORE2023</td><td>A*</td></tr>
        <tr><td>Neural Information Processing Systems</td><td>NeurIPS</td><td>ICORE2026</td><td>A*</td></tr></table></html>'''
    def test_core_not_after_pub_year(self):
        rows=parse_core_page(self.portal())
        self.assertEqual(pick_core('ICML',2024,rows)['source_year'],2023)
        self.assertIsNone(pick_core('ICML',2022,rows))
        self.assertIsNone(pick_core('NeurIPS',2025,rows))
    def test_sjr_exact_title_category_required(self):
        raw=b'Sourceid;Title;SJR;SJR Best Quartile\n12;Journal of Machine Learning Research;1.5;Q1\n'
        table=parse_sjr_csv(raw)
        self.assertIsNone(pick_sjr('Journal of Machine Learning Research',2024,table))
        profile=parse_sjr_profile(b'<table><tr><td>Artificial Intelligence</td><td>2024</td><td>Q2</td></tr></table>')
        rating=pick_sjr('Journal of Machine Learning Research',2024,table,{'12':profile})
        self.assertIn('Q2',rating['value'])
        self.assertIsNone(pick_sjr('Made Up Venue',2024,table))
    def test_no_cv_rating_reuse(self):
        pubs=[{'title':'A','venue':'ICML','year':'2024','category':'conferences',
               'core':'CORE 2020: A','ggs':'GGS 2021: A++','sjr':'Q1'}]
        enrich(pubs,parse_core_page(self.portal()),{})
        self.assertEqual(pubs[0]['ratings']['core']['source_year'],2023)
        self.assertTrue(all(k not in pubs[0] for k in ('core','ggs','sjr')))
    def test_sjr_year_not_after_publication(self):
        rows={'journalofmachinelearningresearch':{'source_id':'12','best_quartile':'Q1','score':'1.0'}}
        prof={'12':parse_sjr_profile(b'<table><tr><td>Artificial Intelligence</td><td>2023</td><td>Q1</td></tr></table>')}
        pubs=[{'title':'A','venue':'Journal of Machine Learning Research','year':'2024','category':'journals'}]
        enrich(pubs,None,{2024:rows},prof)
        self.assertNotIn('ratings',pubs[0])
        enrich(pubs,None,{2023:rows},prof)
        self.assertEqual(pubs[0]['ratings']['sjr']['source_year'],2023)

if __name__=='__main__':unittest.main()

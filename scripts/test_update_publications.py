#!/usr/bin/env python3
"""Offline tests: python -m unittest discover -s scripts -p 'test_*.py'"""
import unittest
from update_publications import parse_dblp_xml, classify, prefer_ee

EXAMPLE=b'''<?xml version="1.0" encoding="UTF-8"?>
<dblpperson pid="209/4941" name="Alberto Maria Metelli">
  <r><inproceedings key="conf/icml/example26"><author pid="209/4941">Alberto Maria Metelli</author><author>Marco Mussi</author><title>Learning from Preference Feedback.</title><year>2026</year><booktitle>ICML</booktitle><ee>https://doi.org/10.1234/test</ee><ee>https://proceedings.mlr.press/v999/test.html</ee></inproceedings></r>
  <r><article key="journals/corr/abs-example"><author>Alberto Maria Metelli</author><title>Learning from Preference Feedback.</title><year>2025</year><journal>CoRR</journal><ee>https://arxiv.org/abs/2510.12345</ee></article></r>
  <r><article key="journals/ml/example"><author>Alberto Maria Metelli</author><title>Different Journal Article.</title><year>2024</year><journal>Machine Learning</journal></article></r>
  <r><www key="homepages/209/4941"><title>Alberto Maria Metelli</title></www></r>
</dblpperson>'''

class ImportTests(unittest.TestCase):
    def test_import_types_and_dedup_preprint(self):
        pubs = parse_dblp_xml(EXAMPLE)
        self.assertEqual(len(pubs),2)
        self.assertEqual(pubs[0]['category'],'conferences')
        self.assertEqual(pubs[0]['year'],'2026')
        self.assertEqual(pubs[0]['paper_url'],'https://proceedings.mlr.press/v999/test.html')
        self.assertEqual(pubs[0]['bibtex_url'],'https://dblp.org/rec/conf/icml/example26.bib')
        self.assertEqual(pubs[0]['authors'],['Alberto Maria Metelli','Marco Mussi'])
        self.assertEqual(pubs[1]['category'],'journals')
    def test_manual_extra_links(self):
        pubs = parse_dblp_xml(EXAMPLE, overrides={'conf/icml/example26': {'extra_links': {'Poster':'https://example.com/poster.pdf'}}})
        self.assertEqual(pubs[0]['extra_links']['Poster'],'https://example.com/poster.pdf')
    def test_mismatch_pid_rejected(self):
        with self.assertRaisesRegex(ValueError,'mismatch'):
            parse_dblp_xml(EXAMPLE,pid='000/000')
    def test_empty_rejected(self):
        with self.assertRaisesRegex(ValueError,'zero bibliographic'):
            parse_dblp_xml(b'<dblpperson pid="209/4941" />')

if __name__=='__main__':
    unittest.main()

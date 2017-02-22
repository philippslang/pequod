from django.test import TestCase
import unittest

import interpret

from django.test.runner import DiscoverRunner


class NoDbTestRunner(DiscoverRunner):
    """ A test runner to test without database creation/deletion """

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass
        

class InterpreterTestCase(TestCase):
    def setUp(self):
        pass

    def test_sentence(self):
        options = ['cell count', 'error count', 'oil in place']
        sentence = 'error count mistake mistakes'
        expected = 'count'
        self.assertEqual(interpret.match(sentence, options), expected)
        
    def test_nlp_nouns(self):
        sentence = 'errors error were are'
        expected = ['error']
        #self.assertEqual(interpret.nouns(sentence), expected)
        #self.assertEqual(1,1)
        
    def test_convertbasic(self):
        sentence = 'errors error finish finished'
        expected = ['error', 'error','finish', 'finish']
        self.assertEqual(interpret.convertbasic(sentence), expected)
        
    def test_removestopwords(self):
        sentence = 'What is The Number of errors in the simulation '
        expected = ['number', 'errors']
        self.assertEqual(interpret.rmvstopwords(sentence), expected)     

    def test_autocorrect(self):
        sentence = ['plays', 'bus','rate','guess']
        expected = ['place', 'gas','rate','gas']
        self.assertEqual(interpret.autocorrect(sentence), expected) 
        
    def test_keyword(self):
        query_list=['error count','cell count','oil place','gas place','water place','oil recovery factor','gas recovery factor','water recovery factor','production rate','pressure','gas oil ratio','error','finish','rate','plot','show']
        sent_tokens = ['error']
        expected = 'error count'
        self.assertEqual(interpret.keywordmatch(query_list,sent_tokens), expected) 
    

                   


if __name__ == '__main__':
    unittest.main()

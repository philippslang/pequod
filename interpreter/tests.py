from django.test import TestCase
import unittest

import interpret

from django.test.runner import DiscoverRunner

import mysite.dispatch as internal_requests

class NoDbTestRunner(DiscoverRunner):
    """ A test runner to test without database creation/deletion """

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass
        

class InterpreterTestCase(TestCase):
    def setUp(self):
        pass


    def test_wrapper(self):
        query_list=['error count','cell count','oil place','gas','gas rate','gas place','water place','oil recovery factor','gas recovery factor','water recovery factor','production rate','pressure','gas oil ratio','error','finished normally','rate','plot','show']
       
        sentence = 'what is the cell count'
        expected = 'cell count'
        self.assertEqual(interpret.matchquery(query_list, sentence),expected)
        sentence = 'what is the average pressure'
        expected = 'pressure'
        self.assertEqual(interpret.matchquery(query_list, sentence),expected)
        sentence = 'has the run finished'
        expected = 'finished normally'
        self.assertEqual(interpret.matchquery(query_list, sentence),expected)
        sentence = 'bla bla'
        expected = internal_requests.BAD_VALUE
        self.assertEqual(interpret.matchquery(query_list, sentence),expected)
        sentence = ''
        expected = internal_requests.BAD_VALUE
        self.assertEqual(interpret.matchquery(query_list, sentence),expected)
        sentence = 'bus'
        expected = 'gas'
        self.assertEqual(interpret.matchquery(query_list, sentence),expected) 
        sentence = 'bus'
        expected = 'gas'
        self.assertEqual(interpret.matchquery(query_list, sentence),expected)
        sentence = 'island place'
        expected = 'oil place'
        self.assertEqual(interpret.matchquery(query_list, sentence),expected)
        sentence = 'hydrocarbons in place '
        expected = 'oil place'
        self.assertEqual(interpret.matchquery(query_list, sentence),expected)
  

"""
    def test_keyword(self):
        #query_list=['error count','cell count','oil place','gas place','water place','oil recovery factor','gas recovery factor','water recovery factor','production rate','pressure','gas oil ratio','error','finish','rate','plot','show']
        query_list=['error','error count']
        sent_tokens = ['error', 'count']
        expected = 'error count'
        #self.assertEqual(interpret.keywordmatch(query_list,sent_tokens), expected) 
        query_list=['error','error count']
        sent_tokens = ['error', 'count']
        expected = 'error count'
        self.assertEqual(interpret.keywordmatch(query_list,sent_tokens), expected)
        sent_tokens = ['mistake', 'count']
        expected = 'error count'
        self.assertEqual(interpret.keywordmatch(query_list,sent_tokens), expected)



    def test_autocorrect(self):
        #sentence = ['what', 'is', 'the', 'castrate']
        #expected = ['what' ,'is', 'the', 'gas', 'rate']
        sentence = ['castrate']
        expected = ['gas','rate']
        self.assertEqual(interpret.autocorrect(sentence), expected) 
        sentence = ['bus']
        expected = ['gas']
        self.assertEqual(interpret.autocorrect(sentence), expected) 
        sentence = ['island']
        expected = ['oil', 'in']
        self.assertEqual(interpret.autocorrect(sentence), expected) 


    def test_convertbasic(self):
        sentence = 'finished had the run completed'
        expected = ['finished', 'have', 'the','run', 'complete']
        self.assertEqual(interpret.convertbasic(sentence), expected)        

   

    def test_sentence(self):
        options = ['cell count', 'error count', 'oil in place']
        sentence = 'error count mistake mistakes'
        expected = 'error count'
        #self.assertEqual(interpret.match(sentence, options), expected)

    def test_nlp_nouns(self):
        sentence = 'finished'
        expected = 'finish'
        #self.assertEqual(interpret.nouns(sentence), expected)
        #self.assertEqual(1,1)
        
        
      

        
    def test_removestopwords(self):
        sentence = 'What is The Number of errors in the simulation '
        expected = ['number', 'errors']
        self.assertEqual(interpret.rmvstopwords(sentence), expected)     

 
        
"""

      

                   
if __name__ == '__main__':
    unittest.main()

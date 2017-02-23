
import itertools

# Some expected reservoir enginerring/simulation terms
re_terms = [
    'gas',
    'oil',
    'water',
    'fluid', 
    'rock',
    'water cut',
    'gas oil ratio',
    'production rate',
    'simulation',
    'in place',
    'show plot',
    'show graph',
    'reservoir',
    'injection rate',
    'cumulative',
    'field',
]

def get_speech_hints(supported_queries):    
    """
    Suggested words to help the speech recognition
    """

    supported = list(itertools.chain(*supported_queries_words(supported_queries)))
    return list(set(re_terms + supported))



def supported_queries_words(supported_queries):
    """
    In here we depend on the convention that query commands have
    underscore delimeters. Also depends on analyzer GET object.
    Returns a nested list with all words for each supported query.
    """

    return [query['query'].split('_') for query in supported_queries]



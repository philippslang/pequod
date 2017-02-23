import itertools

# Some expected reservoir engineering terms
re_terms = [
    'show plot',
    'number of',
    'in place',
    'fluid',
    'water cut',
    'gas oil ratio',
    'production rate',
    'oil',
    'gas',
    'water',
    'error',
    'warning',
    'simulation',
]

def get_suggested_words(supported_queries):
    '''
    Will return a list of probable words given the supported queries
    '''
    supported_words = list(itertools.chain(*supported_queries_words(supported_queries)))
    supported_words = supported_words + re_terms
    supported_words = list(set(supported_words))
    return supported_words

def supported_queries_words(supported_queries):
    """
    In here we depend on the convention that query commands have
    underscore delimeters. Also depends on analyzer GET object.
    Returns a nested list with all words for each supported query.
    """

    return [query['query'].split('_') for query in supported_queries]
    
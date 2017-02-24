
import itertools

# something is wrong with the app engine support here, calls unavailable subprocess
#from google.cloud import speech as google_speech

from googleapiclient import discovery
import httplib2, sys, json
from oauth2client.client import GoogleCredentials

import mysite.dispatch as internal_requests
import googleapiclient.discovery
from autocorrectdict import context_correct_dict
from syndict import synonym_dict

from hints import get_speech_hints

# [START authenticating]
DISCOVERY_URL = ('https://{api}.googleapis.com/$discovery/rest?'
                 'version={apiVersion}')


# Application default credentials provided by env variable
# GOOGLE_APPLICATION_CREDENTIALS
def get_speech_service():
    credentials = GoogleCredentials.get_application_default().create_scoped(
        ['https://www.googleapis.com/auth/cloud-platform'])
    http = httplib2.Http()
    credentials.authorize(http)

    return discovery.build('speech', 'v1beta1', http=http, discoveryServiceUrl=DISCOVERY_URL)
# [END authenticating]


def get_native_encoding_type():
    """Returns the encoding type that matches Python's native strings."""
    if sys.maxunicode == 65535:
        return 'UTF16'
    else:
        return 'UTF32'
        
def trivial_singulars(words):
    """
    Finds plural words by looking at last index == 's'
    and removes these to make them singular in naive way.
    """

    return [word if word[-1] != 's' else word[:-1] for word in words]


def google_speech_json_response_pcm(base64_audio, hints, max_alternatives=1):
    # TODO we can also use raw here, see https://goo.gl/KPZn97    
    #print 'google_speech_json_response_flac got ', base64_audio
    google_speech = get_speech_service()

    speech_request = google_speech.speech().syncrecognize(
        body={
            # https://cloud.google.com/speech/reference/rest/v1beta1/RecognitionConfig
            'config': {
                'encoding': 'LINEAR16',  
                'sampleRate': 16000,  # Hz
                'maxAlternatives': max_alternatives,  
                # See http://g.co/cloud/speech/docs/languages for a list of
                # supported languages.
                'languageCode': 'en-US',
                'speech_context': {
                    'phrases': hints
                }
            },
            # https://cloud.google.com/speech/reference/rest/v1beta1/RecognitionAudio
            'audio': {
                'content': base64_audio,
                }
            })
            
    return speech_request.execute()


def queries_json_to_lists(supported_queries):
    clean_list, raw_list = [], []
    for query in supported_queries:
        clean_list += [query['query'].replace('_', ' ')]
        raw_list += [query['query']]
    return clean_list, raw_list
        
        
def interpret(base64_audio, supported_queries):
    hints = get_speech_hints(supported_queries)    

    interpretation = {'matched query':internal_requests.BAD_VALUE, 'transcript':internal_requests.BAD_VALUE}
    
    if base64_audio:
        print 'INTERPRETER::interpret::interpret: Speech base64 length ', len(base64_audio)
        speech_response = google_speech_json_response_pcm(base64_audio, hints)
        print 'INTERPRETER::interpret::interpret: Google Speech response ', speech_response
        
        if speech_response == {}:
            print 'INTERPRETER::interpret::interpret: Got no speech resonse from Google, defaulting to ', interpretation        
            return interpretation
        
        # effectively, we just take the first alternative
        if speech_response:
            for result in speech_response.get('results', []):
                for alternative in result['alternatives']:
                    interpretation['transcript'] = alternative['transcript']                    
                 
        if interpretation['transcript'] == internal_requests.BAD_VALUE:
            print 'INTERPRETER::interpret::interpret: Got no interpretation, defaulting to ', interpretation        
            return interpretation
        
        clean_list, raw_list = queries_json_to_lists(supported_queries)
        matched_query = matchquery(clean_list, interpretation['transcript'].lower())
        if matched_query != internal_requests.BAD_VALUE:
            interpretation['matched query'] = raw_list[clean_list.index(matched_query)]
        'INTERPRETER::interpret::interpret: Successfully interpreted ', interpretation 
                        

    'INTERPRETER::interpret::interpret: Got empty audio, defaulting to ', interpretation        
    return interpretation


def matchquery(query_list, sentence):
    if not sentence:
        return internal_requests.BAD_VALUE
    else: 
        tokens_basic_form=convertbasic(sentence)
        tokens_nostop=autocorrect(tokens_basic_form)
        tokens_autocorrect=rmvstopwords2(tokens_nostop)
        output_match=keywordmatch(query_list,tokens_autocorrect)
        return output_match


def keywordmatch(query_list,tokens):
    
    """
    >>>keywordmatch3(['oil in place','recovery','oil','place'])
    """
    debug=0
    maxlen=0
    best_ix=-1
    for ii,stand_query in enumerate(query_list):
        querytoken=stand_query.split(" ")
        if len(set(tokens).intersection(querytoken))>maxlen:
            best_ix=ii
            maxlen=len(set(tokens).intersection(querytoken))
            
   
    
    #No match up to now, so look in all synonyms
    if best_ix == -1 :
        alltokens=tokens
        for tokens in alltokens:
            if (debug==1) :print(tokens)
            if debug==1 : print best_ix
            for ii,stand_query in enumerate(query_list):
                querytoken=stand_query
                if querytoken in synonym_dict.keys() :
                    for synonyms in synonym_dict[querytoken]:
                        if tokens==synonyms:
                            best_ix=ii
                            maxlen=len(set(tokens).intersection(synonyms))
                            if debug==1 : print synonyms, str(tokens),len(set(tokens).intersection(synonyms))

    if best_ix==-1:
        return internal_requests.BAD_VALUE
    else:
        return query_list[best_ix]



def autocorrect(list_words):
    """
    >>autocorrect(['face'])
    phase
    """
    new_list=[]
    for ii,word in enumerate(list_words):
        if word in context_correct_dict.keys():
            replacementvals=context_correct_dict[word].split(" ")
            for jj in range(len(replacementvals)):
                new_list.append(replacementvals[jj])
        else:
            new_list.append(word)                     
    return new_list

    
def rmvstopwords(sentence2):
    """
    >>rmvstopwords('This is a test with an error')
    ['error']
    """
    sentence=sentence2.lower()
    mystopwords=[u'all', u'just', u'being', u'over', u'both', u'through', u'yourselves', u'its', u'before', u'o', u'hadn', u'herself', u'll', u'had', u'should', u'to', u'only', u'won', u'under', u'ours', u'has', u'do', u'them', u'his', u'very', u'they', u'not', u'during',
 u'now', u'him', u'nor', u'd', u'did', u'didn', u'this', u'she', u'each', u'further', u'where', u'few', u'because', u'doing', u'some', u'hasn', u'are', u'our', u'ourselves', u'out', u'what', u'for', u'while', u're', u'does', u'above', u'between', u'mustn', u't', u'be', u'we', u'who', u'were', u'here', u'shouldn', u'hers', u'by', u'on', u'about', u'couldn', u'of', u'against', u's', u'isn', u'or', u'own', u'into', u'yourself', u'down', u'mightn', u'wasn', u'your', u'from', u'her', u'their', u'aren', u'there', u'been', u'whom', u'too', u'wouldn', u'themselves', u'weren', u'was', u'until', u'more', u'himself', u'that', u'but', u'don', u'with', u'than', u'those', u'he', u'me', u'myself', u'ma', u'these', u'up', u'will', u'below', u'ain', u'can', u'theirs', u'my', u'and', u've', u'then', u'is', u'am', u'it', u'doesn', u'an', u'as', u'itself', u'at', u'have', u'in', u'any', u'if', u'again', u'no', u'when', u'same', u'how', u'other', u'which', u'you', u'shan', u'needn', u'haven', u'after', u'most', u'such', u'why', u'a', u'off', u'i', u'm', u'yours', u'so', u'y', u'the', u'having', u'once']
 
    redundantwds=['simulation','code','file','test']
    interrogativewords=['did','how','when','which','why','where']
    
    tokens=sentence.split()

    filtered_words = [word for word in tokens if word not in (mystopwords+redundantwds+interrogativewords)]
    return filtered_words

def rmvstopwords2(tokens):
    """
    >>rmvstopwords('This is a test with an error')
    ['error']
    """
   
    mystopwords=[u'all', u'just', u'being', u'over', u'both', u'through', u'yourselves', u'its', u'before', u'o', u'hadn', u'herself', u'll', u'had', u'should', u'to', u'only', u'won', u'under', u'ours', u'has', u'do', u'them', u'his', u'very', u'they', u'not', u'during',
 u'now', u'him', u'nor', u'd', u'did', u'didn', u'this', u'she', u'each', u'further', u'where', u'few', u'because', u'doing', u'some', u'hasn', u'are', u'our', u'ourselves', u'out', u'what', u'for', u'while', u're', u'does', u'above', u'between', u'mustn', u't', u'be', u'we', u'who', u'were', u'here', u'shouldn', u'hers', u'by', u'on', u'about', u'couldn', u'of', u'against', u's', u'isn', u'or', u'own', u'into', u'yourself', u'down', u'mightn', u'wasn', u'your', u'from', u'her', u'their', u'aren', u'there', u'been', u'whom', u'too', u'wouldn', u'themselves', u'weren', u'was', u'until', u'more', u'himself', u'that', u'but', u'don', u'with', u'than', u'those', u'he', u'me', u'myself', u'ma', u'these', u'up', u'will', u'below', u'ain', u'can', u'theirs', u'my', u'and', u've', u'then', u'is', u'am', u'it', u'doesn', u'an', u'as', u'itself', u'at', u'have', u'in', u'any', u'if', u'again', u'no', u'when', u'same', u'how', u'other', u'which', u'you', u'shan', u'needn', u'haven', u'after', u'most', u'such', u'why', u'a', u'off', u'i', u'm', u'yours', u'so', u'y', u'the', u'having', u'once']
 
    redundantwds=['simulation','code','file','test']
    interrogativewords=['did','how','when','which','why','where']
    
   
    filtered_words = [word for word in tokens if word not in (mystopwords+redundantwds+interrogativewords)]
    return filtered_words

def match(sentence, options):
    """
    Use like
    >>> match('is there an error', ['cell count', 'error count', 'oil in place'])
    """
    for option in options:
        intersection = set(sentence.split()).intersection(option.split())
        if intersection: #stops at first non null
            return next(iter(intersection))
    return internal_requests.BAD_VALUE

def match2(sentence, options):
    """
    Use like
    >>> match('is there an error', ['cell count', 'error count', 'oil in place'])
    """
    allmatches=[]
    lenmatched=[]
    ngrammax=0
    for option in options:
        intersection = set(sentence.split()).intersection(option.split())
        if intersection: #stops at first non null
            if len(intersection)>ngrammax: 
                allmatches=intersection
                ngrammax= len(intersection)
            #return option
    print allmatches
    print lenmatched
    if not allmatches:
        return internal_requests.BAD_VALUE
    else:
        return allmatches
        
        
        
def convertbasic(sentence):
    """
    >>> convert_basic('were there any errors')
    ['are, is, any, error']    
    """
    body = {
        'document': {
            'type': 'PLAIN_TEXT',
            'content': sentence,
        },
        'encoding_type': get_native_encoding_type(),
    }
    service = googleapiclient.discovery.build('language', 'v1')

    request = service.documents().analyzeSyntax(body=body)
    response = request.execute()
    tokens_basic=[str(response['tokens'][ii]['lemma']) for ii in range(len(sentence.split()))   ]   
    return tokens_basic
    
    
def nouns(sentence):
    """
    >>> nouns('is there an error')
    ['error']
    """
    body = {
        'document': {
            'type': 'PLAIN_TEXT',
            'content': sentence,
        },
        'encoding_type': get_native_encoding_type(),
    }

    service = googleapiclient.discovery.build('language', 'v1')

    request = service.documents().analyzeSyntax(body=body)
    response = request.execute()
    #parsed = json.loads(response)
    #for ii in range(4):
    #    print response['tokens'][ii]['lemma']
    #print len(response['tokens'][0])#['lemma']
    #print json.dumps(response, indent=4, sort_keys=True)
    
    return sentence[0]

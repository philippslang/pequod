
import itertools

# something is wrong with the app engine support here, calls unavailable subprocess
#from google.cloud import speech as google_speech

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials


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


def supported_queries_words(supported_queries):
    """
    In here we depend on the convention that query commands have
    underscore delimeters. Also depends on analyzer GET object.
    Returns a nested list with all words for each supported query.
    """

    return [query['query'].split('_') for query in supported_queries]


def supported_queries_words_flattened(supported_queries):    
    """
    Flattened list of all words occuring in the supported queries.
    """

    return list(itertools.chain(*supported_queries_words(supported_queries)))


def trivial_singulars(words):
    """
    Finds plural words by looking at last index == 's'
    and removes these to make them singular in naive way.
    """

    return [word if word[-1] != 's' else word[:-1] for word in words]


def google_speech_json_response_flac(url_audio, hints):
    # TODO we can also use raw here, see https://goo.gl/KPZn97
    google_speech = get_speech_service()
    speech_request = google_speech.speech().syncrecognize(
        body={
            # https://cloud.google.com/speech/reference/rest/v1beta1/RecognitionConfig
            'config': {
                'encoding': 'FLAC',  
                'sampleRate': 16000,  # Hz
                # See http://g.co/cloud/speech/docs/languages for a list of
                # supported languages.
                'languageCode': 'en-US',  
                'speechContext': {
                    'phrases': hints
                  },
            },
            # https://cloud.google.com/speech/reference/rest/v1beta1/RecognitionAudio
            'audio': {
                'uri': url_audio,
                }
            })
    
    return speech_request.execute()


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
                'languageCode': 'en-US'
            },
            # https://cloud.google.com/speech/reference/rest/v1beta1/RecognitionAudio
            'audio': {
                'content': base64_audio,
                }
            })
            
    return speech_request.execute()

def interpret(base64_audio, supported_queries):
    print supported_queries
    hints = supported_queries_words_flattened(supported_queries)    

    interpretation = {'matched query':'cell_count', 'transcript':'no transcript 0'}

    if base64_audio:
        speech_response = google_speech_json_response_pcm(base64_audio, hints)
        print speech_response
        if speech_response:
            for result in speech_response.get('results', []):
                for alternative in result['alternatives']:
                    interpretation['transcript'] = alternative['transcript']
                    print alternative['transcript']
	'''
        for query in supported_queries:
            for result in speech_response.get('results', []):
                for alternative in result['alternatives']:
                    intersection = set(trivial_singulars(alternative['transcript'].split())).intersection(query['query'].split('_'))            
                    if intersection:
                        return {'matched query':query['query'], 'transcript':alternative['transcript']}
	'''
    return interpretation


# TODO rework for base64
def interpret_impl(base64_audio, supported_queries):
    # TODO extract these two approaches tnto their own functions


    # TODO extract to get_hints function
    hints = supported_queries_words_flattened(supported_queries)

    # if we don't get flac, we could use the raw approach outlined in some example (LINEAR and stream in from mic)
    # https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/speech/api-client/transcribe.py


    #speech_response = google_speech_json_response_flac(url_audio, hints):

    '''
    for result in response.get('results', []):
        print('Result:')
        for alternative in result['alternatives']:
            print(u'  Alternative: {}'.format(alternative['transcript']))
    '''

    # TODO extract to supported_query_match

    # dummy here to get things started: we compare all words of the all utterances 
    # against the words in each query - first match wins
    for query in supported_queries:
        for result in speech_response.get('results', []):
            for alternative in result['alternatives']:
                intersection = set(trivial_singulars(alternative['transcript'].split())).intersection(query['query'].split('_'))            
                if intersection:
                    return {'matched query':'error_count', 'transcript':alternative['transcript']}

    
    # TODO the default should be something that can be handled at a higher level
    return {'matched query':'cell_count', 'transcript':'no transcript 2'}


import itertools
from .hints import get_suggested_words

# something is wrong with the app engine support here, calls unavailable subprocess
#from google.cloud import speech as google_speech

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials

import mysite.dispatch as internal_requests

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


def interpret(base64_audio, supported_queries):
    hints = get_suggested_words(supported_queries)

    interpretation = {'matched query':internal_requests.BAD_VALUE, 'transcript':internal_requests.BAD_VALUE}
    
    if base64_audio:
        print 'INTERPRETER::interpret::interpret: Speech base64 length ', len(base64_audio)
        speech_response = google_speech_json_response_pcm(base64_audio, hints)
        print 'INTERPRETER::interpret::interpret: Google Speech response ', speech_response
        if speech_response:
            for result in speech_response.get('results', []):
                for alternative in result['alternatives']:
                    interpretation['transcript'] = alternative['transcript']                    
                    
	
        for query in supported_queries:
            for result in speech_response.get('results', []):
                for alternative in result['alternatives']:
                    intersection = set(trivial_singulars(alternative['transcript'].split())).intersection(query['query'].split('_'))            
                    if intersection:
                        print 'INTERPRETER::interpret::interpret: Matched query ', query['query']
                        return {'matched query':query['query'], 'transcript':alternative['transcript']}
                        

    print 'INTERPRETER::interpret::interpret: Got empty audio, defaulting to ', interpretation        
    return interpretation

# -*- coding: utf-8 -*-
 
import io
import sys
import os
import json
from six.moves import urllib
from alexa_client import AlexaClient
from google.cloud import speech
 
#오디오파일을 한글 텍스트로 번환
def transcribe_file_kor(speech_file):
    
    speech_client = speech.Client()
 
    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()
        audio_sample = speech_client.sample(
            content=content,
            source_uri=None,
            encoding='LINEAR16',
            sample_rate_hertz=16000)
 
    alternatives = audio_sample.recognize('ko-KR')
    for alternative in alternatives:
        return alternative.transcript
        
#오디오 파일을 영어 텍스트로 번환
def transcribe_file_eng(speech_file):
    
    speech_client = speech.Client()
 
    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()
        audio_sample = speech_client.sample(
            content=content,
            source_uri=None,
            encoding='LINEAR16',
            sample_rate_hertz=16000)
 
    alternatives = audio_sample.recognize('en-US')
    for alternative in alternatives:
        return alternative.transcript
        
#한글에서 영어로 변환
def translateKorToEng(korean_string):
    client_id = "1TEdPB_2_D3MzrdGYk01"
    client_secret = "2F7k4y47yJ"
    encText = urllib.parse.quote(korean_string.encode("utf-8"))
    data = "source=ko&target=en&text=" + encText
    url = "https://openapi.naver.com/v1/language/translate"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = json.loads(response.read().decode('utf-8'))
        translated_eng_str = response_body["message"]["result"]["translatedText"]
        return translated_eng_str
    else:
        print("Error Code:" + rescode)
        
#영어에서 한글로 변환
def translateEngToKor(english_string):
    client_id = "1TEdPB_2_D3MzrdGYk01"
    client_secret = "2F7k4y47yJ"
    encText = urllib.parse.quote(english_string.encode("utf-8"))
    data = "source=en&target=ko&text=" + encText
    url = "https://openapi.naver.com/v1/language/translate"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = json.loads(response.read().decode('utf-8'))
        translated_kor_str = response_body["message"]["result"]["translatedText"]
        return translated_kor_str
    else:
        print("Error Code:" + rescode)
    
#한글로 된 파일을 음성으로 읽어줌
def koreanTextToSpeech(korean_string):
    client_id = "1TEdPB_2_D3MzrdGYk01"
    client_secret = "2F7k4y47yJ"
    encText = urllib.parse.quote(korean_string.encode("utf-8"))
    data = "speaker=mijin&speed=0&text=" + encText;
    url = "https://openapi.naver.com/v1/voice/tts.bin"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request, data=data.encode('utf-8'))
    rescode = response.getcode()
    if(rescode==200):
        print("TTS mp3")
        response_body = response.read()
        with open('korean_alexa.mp3', 'wb') as f:
            f.write(response_body)
    else:
        print("Error Code:" + rescode)
    
    
"""This test will send a pre-generated audio file in the `tests` directory
to AVS, and saves it as `/tmp/test1.mp3`."""
def askToAlexa():
    alexa = AlexaClient()
    input = 'after_srate_conv.wav'  #'{}/1.wav'.format(TESTS_PATH)
    save_to = 'response_alexa.mp3'
    alexa.ask(input, save_to=save_to)
    print "Response from Alexa saved to {}".format(save_to)
 
 
if __name__ == '__main__':
 
    # 환경 변수 설정
    os.system("export GOOGLE_APPLICATION_CREDENTIALS=\MyProject-64acde2fc803.json")
    
    # 인코딩 설정
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    # 녹음
    os.system("arecord -D plughw:1,0 -f S16_LE -c1 -r16000 -d 3 input.wav")
    
    # STT 한글
    input_kor_str = transcribe_file_kor('input.wav')
    
    # 한글을 영어로 번역
    input_eng_str = translateKorToEng(unicode(input_kor_str))
    
    # 영어 TTS
    os.system("espeak -w before_srate_conv.wav \""+input_eng_str+"\"")
    os.system("sox before_srate_conv.wav -r 16000 after_srate_conv.wav")
    
    # alexa
    askToAlexa()
    
    # 영어음성 STT
    os.system("sox response_alexa.mp3 -r 16000 response_alexa_converted.wav")
    output_eng_str = transcribe_file_eng('response_alexa_converted.wav')
    print(output_eng_str)
    
    # 영어문장을 한글로 번역
    output_kor_str = translateEngToKor(output_eng_str).encode("utf-8")
    print(output_kor_str)
    
    # 한글 TTS
    koreanTextToSpeech(unicode(output_kor_str))
    
    # 한글 음성 출력
    os.system("mpg321 korean_alexa.mp3")

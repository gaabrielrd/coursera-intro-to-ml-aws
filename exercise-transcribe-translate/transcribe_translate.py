import json
import re
import boto3
import time
from random import choice
from s3_upload import upload_file

# --------------------
# Transcribe
# --------------------

re_sentence = """(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"""

# Generate clients
transcribeClient = boto3.client('transcribe')
s3Client = boto3.client('s3')


# Upload the file to s30
with open('Raf01_320.mp4', 'rb') as file:
    upload_file('Raf01_320.mp4', 'rodadev-test', 'transcribe/source.mp4')

# Initiate transcribe job
response = transcribeClient.start_transcription_job(
    TranscriptionJobName='Transcribe-op-coursera-01',
    Media={'MediaFileUri': 'https://rodadev-test.s3.amazonaws.com/transcribe/source.mp4'},
    MediaFormat='mp4',
    LanguageCode='pt-BR'
)

print(response)

# Wait for the job to complete
while True:
    response = transcribeClient.get_transcription_job(
        TranscriptionJobName='Transcribe-op-coursera-01'
    )
    status = response.get('TranscriptionJob')['TranscriptionJobStatus']
    if status == 'COMPLETED':
        break
    print("Not ready yet...")
    time.sleep(5)

# Get the job result location
transcriptFileUri = response.get('TranscriptionJob')[
    'Transcript']['TranscriptFileUri']

print(f'TranscriptFileUri: {transcriptFileUri}')

# Write the result into transcribe.json
with open('transcribe.json', 'wb') as f:
    # Load the file
    import urllib.request
    contents = urllib.request.urlopen(transcriptFileUri).read()

    print(f'get contents: {contents}')

    f.write(contents)


# ---------------
# -- Translate --
# ---------------

with open("transcribe.json") as file:
    transcribe = json.load(file)

# build array of start times
times = [item["start_time"]
         for item in transcribe["results"]["items"] if "start_time" in item]

translate = boto3.client('translate')

transcript = transcribe["results"]["transcripts"][0]["transcript"]
sentences = re.split(re_sentence, transcript)
word_ptr = 0
translated_arr = []

for sentence in sentences:
    translated_text = translate.translate_text(
        Text=sentence,
        SourceLanguageCode='pt-BR',
        TargetLanguageCode='en-US',
    ).get("TranslatedText")

    translated_arr.append(
        {"start_time": times[word_ptr], "translated": translated_text})
    word_count = len(re.findall(r'\w+', sentence))
    word_ptr += word_count

print(json.dumps(translated_arr, indent=2))

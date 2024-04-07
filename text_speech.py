from unicodedata import name
from urllib import response
from google.cloud import texttospeech
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'text-to-speech/animated-zenith-417817-ca2e9a2b5085.json'

def text_to_speech(text, base_name, txt_file=None):
    client = texttospeech.TextToSpeechClient()

    # Read the content of the text file
    if txt_file:
        with open(txt_file, 'r') as file:
            text = file.read()

    synthesis_input = texttospeech.SynthesisInput(ssml=text)
    voice1 = texttospeech.VoiceSelectionParams(
        name='en-GB-Standard-B',
        language_code='en-GB'
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.15,
        pitch=0.2
    )

    response1 = client.synthesize_speech(
        input=synthesis_input,
        voice=voice1,
        audio_config=audio_config
    )

    # Get the base name of the text file (without the extension)
    # base_name = os.path.splitext(txt_file)[0]
    mp3_file = f"audio/{base_name}.mp3"

    with open(mp3_file, 'wb') as output:
        output.write(response1.audio_content)

    print(f"Audio file '{mp3_file}' generated successfully.")

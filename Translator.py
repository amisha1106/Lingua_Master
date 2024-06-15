import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os

def translate_text(text, target_language):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language)
    return translated_text.text

def text_to_speech(text, language):
    tts = gTTS(text=text, lang=language)
    tts.save("translated_text.mp3")

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Say something to translate: ")
    
    recognizer.adjust_for_ambient_noise(source) 
    
    audio = recognizer.listen(source)

try:
    print("Recognizing...")
    text_to_translate = recognizer.recognize_google(audio)
    print("You said:", text_to_translate)
except sr.UnknownValueError:
    print("Sorry, I couldn't understand what you said.")
    text_to_translate = ""
except sr.RequestError:
    print("Sorry, the speech recognition service is unavailable.")
    text_to_translate = ""

if text_to_translate:
    target_language = input("Enter the target language code (e.g., fr for French): ")

    translated_text = translate_text(text_to_translate, target_language)
    print("Translated text:", translated_text)

    text_to_speech(translated_text, target_language)

    os.system("start translated_text.mp3")
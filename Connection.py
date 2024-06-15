from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from googletrans import Translator
from gtts import gTTS
import os
import speech_recognition as sr
from playsound import playsound

app = Flask(__name__)
app.config["SECRET_KEY"] = 'secret_key'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///translatorwebsite.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Contacts(db.Model):
    Slno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    msg = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/", methods=["GET", "POST"])
def home():
    output = None
    if request.method == "POST":
        if 'speech' in request.form:
            return redirect("/speech")
        else:
            t_sentence = request.form["sentence"]
            language = request.form['inputvalue']
            output = translate_text(t_sentence, language)
            text_to_speech(output, language)
    return render_template('Translator.html', output=output)

@app.route('/contact', methods=["POST"])
def contact_details_page():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        entry = Contacts(name=name, email=email, subject=subject, msg=message)

        db.session.add(entry)
        db.session.commit()

    return redirect("/")

@app.route("/admin", methods=["GET"])
def admin_post():
    posts = Contacts.query.all()
    return render_template('admin.html', posts=posts)

@app.route("/admin/delete/<int:Slno>")
def admin_post_delete(Slno):
    post = Contacts.query.filter_by(Slno=Slno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect('/admin')

@app.route("/speech", methods=["GET", "POST"])
def speech_to_text():
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
        target_language = request.form['target_language']

        translated_text = translate_text(text_to_translate, target_language)
        print("Translated text:", translated_text)

        text_to_speech(translated_text, target_language)

    return redirect("/")

def translate_text(text, target_language):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language)
    return translated_text.text

def text_to_speech(text, language):
    tts = gTTS(text=text, lang=language)
    tts.save("translated_text.mp3")
    playsound("translated_text.mp3")
    
@app.route("/voice_to_text")
def voice_to_text():
    return render_template("Voice_t_speech.html")

if __name__ == '__main__':
    app.run(debug=True)

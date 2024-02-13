import speech_recognition as sr
from pydub import AudioSegment

r = sr.Recognizer()

def convert_to_wav(path):
    sound = AudioSegment.from_file(path)
    sound.export(path, format="wav")

def transcribe_audio_file(path):
    print(path)
    with sr.AudioFile(path) as source:
        audio_text = r.listen(source)
        try:
            return r.recognize_google(audio_text)
        except:
            return "Sorry, an error occurred"

def main():
    path = r"C:\Users\senor\Downloads\harvard.wav"
    print(transcribe_audio_file(path))

if __name__ == '__main__':
    main()
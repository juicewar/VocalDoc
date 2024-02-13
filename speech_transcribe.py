import speech_recognition as sr
from pydub import AudioSegment

r = sr.Recognizer()

def convert_to_wav(path):
    sound = AudioSegment.from_file(path)
    sound.export(path, format="wav")

def transcribe_audio_file(path):
    with sr.AudioFile(path) as source:
        audio_text = r.listen(source)
        try:
            return r.recognize_sphinx(audio_text)
        except sr.UnknownValueError:
            return "i have no idea what you just tried to say"

def main():
    path = r"C:\Users\senor\Downloads\harvard.wav"
    print(transcribe_audio_file(path))

if __name__ == '__main__':
    main()
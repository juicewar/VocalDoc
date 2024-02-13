from flask import Flask, request, render_template, send_file
import os
from speech_transcribe import transcribe_audio_file, convert_to_wav

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/')
def upload_file():
    return render_template('index.html')

@app.route('/uploader', methods=['POST'])
def uploader():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    # Valid file
    if file:
        filename = "temp" + os.path.splitext(file.filename)[1]

        # Save the file locally
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_path)

        try:
            convert_to_wav(saved_path)

            # Process the file
            transcribed_speech = transcribe_audio_file(saved_path)
        except:
            return "Sorry there was an error with your file..."

        # Let the user see the transcribed speech
        return transcribed_speech

if __name__ == '__main__':
    app.run(debug=True)
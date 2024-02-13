from flask import Flask, request, render_template, send_file, jsonify, flash
import os
from flask_cors import CORS
from speech_transcribe import transcribe_audio_file, convert_to_wav

app = Flask(__name__)
CORS(app)

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
        filename = "temp.wav"

        # Save the file locally
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_path)
        convert_to_wav(saved_path)

        # Process the file
        # transcribed_speech = transcribe_audio_file(saved_path)
        # transcribed_speech = "yuhh"


        # Let the user see the transcribed speech
        # response = jsonify({'message': transcribed_speech})
        # return response
        return jsonify({'message': "file successful!"})



if __name__ == '__main__':
    app.run(debug=True)
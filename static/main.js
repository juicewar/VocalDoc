function processAudioRecording(){
    console.log(audioRecording);
}

function displayTranscribedSpeech(text){
    let textTag = document.getElementById("transcribedSpeech");
    textTag.innerHTML = text;
    parseMessage(text);
}

// When parsing the spoken text, the fields are converted into single digit tokens for easy parsing
// This function checks that the current data is a token or not 
function isNumberToken(s){
    return /^\d$/.test(s);
}

function parseMessage(text){
    let patient = {
        "patient number": null,
        "name": null,
        "date": null,
        "symptoms": null,
        "diagnosis": null,
        "prescription": null,
        "dosage": null,
        "notes": null
    }

    let patientFields = Object.keys(patient);

    // Pre process message to be parsed
    for (let i=0; i<patientFields.length; i++){
        text = text.replace(patientFields[i], i);
    }
    
    words = text.split(' ');
    let fieldNumber = null;
    let data = [];

    // dont forget to check edge case when the first word is not a field number

    while (words.length > 0){
        if (fieldNumber == null){
            fieldNumber = parseInt(words.shift());
        } else {
            // if receiving data for a field
            if (!isNumberToken(words[0])) {
                data.push(words.shift());
            } else {
                patient[patientFields[fieldNumber]] = data.join(' ');
                data = [];
                fieldNumber = null;
            }
        }
    }

    // Save the last information
    if (data.length > 0) {
        patient[patientFields[fieldNumber]] = data.join(' ');
    }

    console.log(patient);
    
}

let constraintObj = { 
    audio: true, 
    video: false
}; 

navigator.mediaDevices.getUserMedia(constraintObj)
.then(function(mediaStreamObj) {
    
    //add listeners for saving audio
    let start = document.getElementById('btnStart');
    let stop = document.getElementById('btnStop');
    let audioSave = document.getElementById('audioRecording');
    let mediaRecorder = new MediaRecorder(mediaStreamObj);
    let chunks = [];
    stop.disabled = true;
    
    start.addEventListener('click', (ev)=>{
        mediaRecorder.start();
        start.disabled = true;
        stop.disabled = false;
        console.log(mediaRecorder.state);
    })

    stop.addEventListener('click', (ev)=>{
        mediaRecorder.stop();
        start.disabled = false;
        stop.disabled = true;
        console.log(mediaRecorder.state);
    });

    mediaRecorder.ondataavailable = function(ev) {
        chunks.push(ev.data);
    }

    mediaRecorder.onstop = (ev)=>{
        let blob = new Blob(chunks, { 'type' : 'audio/mp4;' });
        chunks = [];
        let audioURL = window.URL.createObjectURL(blob);
        audioSave.src = audioURL;

        let data = new FormData()
        data.append('file', blob, 'file')

        fetch('http://127.0.0.1:5000/uploader', {
          method: 'POST',
          body: data

        }).then(response => response.json()
        ).then(json => {
          displayTranscribedSpeech(json.message)
        });
    }
})
.catch(function(err) { 
    console.log(err.name, err.message); 
});
function processAudioRecording(){
    console.log(audioRecording);
}

function displayTranscribedSpeech(text){
    let textTag = document.getElementById("transcribedSpeech");
    textTag.innerHTML = text;
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
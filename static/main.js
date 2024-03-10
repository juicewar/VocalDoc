function processAudioRecording(){
    console.log(audioRecording);
}

// Show what was actually said
function displayTranscribedSpeech(text){
    let textTag = document.getElementById("transcribedSpeech");
    textTag.innerHTML = text;    
}

function showLoadingMessage(){
    let textTag = document.getElementById("transcribedSpeech");
    textTag.innerHTML = "Please wait... It may take a moment to trascribe your audio."; 
}

function parseDisplayedTable(){
    let table = document.getElementById("parsedTable");
    patient = {}
    for (let i=0; i<table.rows.length; i++){
        let row = table.rows.item(i).cells;
        patient[row.item(0).innerHTML] = row.item(1).innerHTML;
    }
    return patient;
}

function clearTable(){
    let table = document.getElementById("parsedTable");
    for (let i=0; i<table.rows.length; i++){
        let row = table.rows.item(i).cells.item(1).innerHTML = '';
    }
}

function submitData(){
    if (isAllDataFilled()){
        alert("data submitted!");
        clearTable();
        btnSubmit.disabled = true;
    } else {
        alert("error: not all data filled in");
        btnSubmit.disabled = true;
    }
}

// Display a table of the parsed information
function displaySpeechTable(text){
    let patient = parseMessage(text);
    let existingPatientData = parseDisplayedTable();
    let combinedPatientData = updateAndMerge(existingPatientData, patient);    
    patient = combinedPatientData;
    
    let table = document.getElementById("parsedTable");

    // Clear existing table content
    table.innerHTML = "";

    // Iterate through patient data and update the table
    Object.entries(patient).forEach(function([key, value]) {
        let row = table.insertRow(); // Insert a new row
        let keyCell = row.insertCell(); // Insert a new cell for key
        let valueCell = row.insertCell(); // Insert a new cell for value

        // Set content for key and value cells
        keyCell.textContent = key;
        valueCell.textContent = value;
        valueCell.contentEditable = true;
    });

    // Allow the doctor to submit if all the fields are filled in
    if (isAllDataFilled()){
        btnSubmit.disabled = false;
    } else {
        btnSubmit.disabled = true;
    }
}

// When taking multiple recordings, allow to update fields from multiple takes
function updateAndMerge(fields1, fields2){
    let clone = { ...fields1 }
    Object.entries(fields2).forEach(function([key, value]) {
        if (value != null && value != '' && fields1.hasOwnProperty(key)){
            clone[key] = value;
        }
    })
    return clone;
}

function isAllDataFilled(){
    patient = parseDisplayedTable();
    return !(Object.values(patient).some(x => x === null || x === ''));
}

// Will show both what the software understood from the text, as well as the formatted table
function displaySpeechInfo(text){
    displayTranscribedSpeech(text);
    displaySpeechTable(text);
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

    // Edge cases where the first word is not a valid field number, ignore.
    words = text.split(' ');
    while (words.length > 0){
        // patient number is an edge case since two words
        if (words.length > 1 && words[0] + words[1] == "patientnumber") {
            break;

        // if first word is one of the other valid fields
        } else if (patient.hasOwnProperty(words[0])) {
            break;
        }
        words.shift();
    }

    text = words.join(' ');

    // Pre process message to be parsed
    for (let i=0; i<patientFields.length; i++){
        text = text.replace(patientFields[i], i);
    }
    
    words = text.split(' ');
    let fieldNumber = null;
    let data = [];
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
    return patient;
    
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
        showLoadingMessage();
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
          displaySpeechInfo(json.message)
        });
    }
})
.catch(function(err) { 
    console.log(err.name, err.message); 
});
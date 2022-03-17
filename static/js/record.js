let getUserMediaStream;  // Stream from getUserMedia()
let recorder;  // Recorder.js object
let input;  // MediaStreamAudioSourceNode

let AudioContext = window.AudioContext || window.webkitAudioContext;
let audioContext;

let recordButton = document.getElementById("recordButton");
recordButton.addEventListener("click", startRecording);  // Add the event to the record button


function startRecording() {
    let constraints = { audio: true, video:false };

    recordButton.disabled = true;  // Disable the record button until getting a success or fail from getUserMedia()

    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        audioContext = new AudioContext();  // Create an audio context after getUserMedia is called

        getUserMediaStream = stream;  // Assign gumStream for later use
        input = audioContext.createMediaStreamSource(stream);  // Use the stream

        recorder = new Recorder(input);
        recorder.record();  // Start the recording process

        setTimeout(stopRecording, 5000);  // Wait 5 sec

    }).catch(function(error) {
        recordButton.disabled = true;  // Enable the record button if getUserMedia() fails
    });
}


function stopRecording() {
    recordButton.disabled = false;  // Enable the record button to allow new recordings
    recorder.stop();  // Tell the recorder to stop the recording
    getUserMediaStream.getAudioTracks()[0].stop();  // Stop microphone access
    recorder.exportWAV(postAudio);  // Create the wav blob and pass it on to postAudio
}


function postAudio(blob) {
    // Name of .wav file to use during upload and download (without extension)
    let filename = new Date().toISOString();

    let request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append("speech_recording", blob, filename);
    request.open("POST", "/", true);
    request.send(formData);
}

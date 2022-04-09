let get_user_media_stream;
let recorder;  // Recorder.js object
let input;  // MediaStreamAudioSourceNode

let AudioContext = window.AudioContext || window.webkitAudioContext;
let audio_context;

let record_button = document.getElementById("record-btn");
record_button.addEventListener("click", start_recording);  // Add the event to the record button


function start_recording() {
    let constraints = { audio: true, video:false };

    record_button.disabled = true;  // Disable the record button until getting a success or fail from getUserMedia()

    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        audio_context = new AudioContext();  // Create an audio context after getUserMedia is called

        get_user_media_stream = stream;  // Assign gumStream for later use
        input = audio_context.createMediaStreamSource(stream);  // Use the stream

        recorder = new Recorder(input);
        recorder.record();  // Start the recording process

        setTimeout(stop_recording, 5000);  // Wait 5 sec

    }).catch(function(error) {
        record_button.disabled = true;  // Enable the record button if getUserMedia() fails
    });
}


function stop_recording() {
    record_button.disabled = false;  // Enable the record button to allow new recordings
    recorder.stop();  // Tell the recorder to stop the recording
    get_user_media_stream.getAudioTracks()[0].stop();  // Stop microphone access
    recorder.exportWAV(post_audio);  // Create the wav blob and pass it on to postAudio
}


function post_audio(blob) {
    // Name of .wav file to use during upload and download (without extension)
    let filename = new Date().toISOString();

    let request = new XMLHttpRequest();
    let form_data = new FormData();
    form_data.append("speech_recording", blob, filename);
    request.open("POST", "/", true);
    request.send(form_data);
}

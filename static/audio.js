let audioCtx;
let source;
let mediaRecorder;
let mediaStream;
let audioBuffers = [];
let startTime = 0;
let pauseTime = 0;
let isPlaying = false;
let isPaused = false;
let stopPlaying = false;
let recordedChunks = [];


$(document).ready(function() {
    audioBuffers = [];
    startTime = 0;
    pauseTime = 0;
    isPlaying = false;
    isPaused = false;
    stopPlaying = false;
    recordedChunks = [];

    setInterval(function () {
        if (audioCtx !== undefined) {loadAudioFromQueue();}
    }, 1000);
});


function initAudio() {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
}


function loadAudioFromQueue() {
    try {
        if (!stopPlaying) {
            $.get('/get_next_from_audio_queue', async function (response) {
                if (!response['empty']) {
                    const file_url = response['file_url'];
                    console.log('Fetching audio file:', file_url);
                    const fetchResponse = await fetch(file_url);
                    const arrayBuffer = await fetchResponse.arrayBuffer();

                    // Decode the audio data from the MP3 file
                    audioBuffers.push(await audioCtx.decodeAudioData(arrayBuffer));
                    if (!isPlaying && !isPaused && !stopPlaying) {
                        playAudio();
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading audio:', error);
    }
}


function playAudio() {
    if (!isPlaying) {
        isPlaying = true;
        isPaused = false;
        stopPlaying = false;
        source = audioCtx.createBufferSource();
        source.buffer = audioBuffers[0];
        source.connect(audioCtx.destination);

        // Set up an event handler to detect when the audio has finished playing
        source.onended = function () {
            isPlaying = false;
            if (!isPaused) {
                audioBuffers.shift();
                if (audioBuffers.length > 0) {
                    startTime = 0;
                    pauseTime = 0;
                    playAudio();
                } else {
                    stopAudio();
                }
            }
        };

        // Start the source to play the audio
        let offset = pauseTime;
        source.start(0, offset);
        startTime = audioCtx.currentTime - offset;
        updateUIByAudioStatus(isPlaying);
    }
}


async function playSingleAudioFile(file_url) {
    if (audioCtx === undefined) {
        initAudio();
    }
    const fetchResponse = await fetch(file_url);
    const arrayBuffer = await fetchResponse.arrayBuffer();
    const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
    source = audioCtx.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioCtx.destination);
    source.start()
}


function pauseAudio() {
    isPaused = true;
    source.stop();
    pauseTime = audioCtx.currentTime - startTime;
    isPlaying = false;
}


function stopAudio() {
    stopPlaying = true;
    isPlaying = false;
    isPaused = false;
    source.stop();
    $.get('/clear_audio_queue', function (response) {});
    audioBuffers = [];
    pauseTime = 0;  // Reset the pause time so the audio starts from the beginning next time
    startTime = 0;
    updateUIByAudioStatus(isPlaying);
}


function startRecording() {
    return new Promise(async (resolve, reject) => {
    try {
        stopAudio();
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(mediaStream);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            const blob = new Blob(recordedChunks, { type: 'audio/mpeg-3' });
            recordedChunks = [];
            resolve(blob);
        };

        mediaRecorder.onerror = (event) => {
            reject(event.error);
        };

        mediaRecorder.start();

        } catch (error) {
            console.error('Error starting recording:', error);
            reject(error);
        }
    });
}


function stopRecording() {
    if (mediaRecorder) {
        mediaRecorder.stop();
    }
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
}


async function uploadAudio(blob) {
    let filename = null;
    try {
        console.log('Uploading recording...');
        const formData = new FormData();
        formData.append('file', blob, 'recording.mp3');
        console.log('FormData created:', formData, 'Blob size:', blob.size);
        for (let [key, value] of formData.entries()) {
            console.log(key, value);
        }

        const response = await fetch(upload_endpoint, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        filename = data.filename;
        if (response.ok && filename !== null) {
            filename = data.filename;
        } else if (response.ok && filename === null) {
            console.error('Error uploading audio: no file found on request');
        } else {
            console.error('Error uploading audio:', response.statusText);
        }
    } catch (error) {
        console.error('Error uploading audio:', error);
    }
    return filename;
}


function updateUIByAudioStatus(is_playing) {

    var record_button = $('#record-button');
    var record_icon = $('#record-icon');
    var lang_button = $('#lang-toggle-button');
    var lang_text = $('#lang-text');
    var pause_icon = $('#pause-icon');

    if (is_playing && record_button.attr('name') === 'record') {
        record_button.attr('name', 'stop');
        record_button.attr('title', 'Stop Audio');
        lang_button.attr('name', 'pause');
        lang_button.attr('title', 'Pause Audio');

        record_icon.removeClass('fas');
        record_icon.removeClass('fa-microphone');
        record_icon.addClass('fa-solid');
        record_icon.addClass('fa-stop');

        lang_text.css('display', 'none');
        pause_icon.css('display', 'block');
        pause_icon.removeClass('fa-play');
        pause_icon.addClass('fa-pause');

    } else if (!is_playing && record_button.attr('name') === 'stop') {
        record_button.attr('name', 'record');
        record_button.attr('title', 'Record Message [Alt+R]');
        lang_button.attr('name', 'lang-record');
        lang_button.attr('title', 'Switch Recording Language [Alt+L]');

        record_icon.addClass('fas');
        record_icon.addClass('fa-microphone');
        record_icon.removeClass('fa-solid');
        record_icon.removeClass('fa-stop');

        lang_text.css('display', 'block');
        pause_icon.css('display', 'none');
    }
}
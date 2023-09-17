let audioCtx;
let source;
let mediaRecorder;
let mediaStream;
let audioBuffers = [];
let startTime = 0;
let pauseTime = 0;
let isPlaying = false;
let isPaused = false;
let recordedChunks = [];


$(document).ready(function() {
    setInterval(function () {
        if (audioCtx !== undefined) {loadAudioFromCache();}
    }, 1000);
});


function initAudio() {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
}


function loadAudioFromCache() {
    try {
        $.get('/audio_cache', async function (response) {
            if (!response['empty']) {
                const file_url = response['file_url'];
                const fetchResponse = await fetch(file_url);
                const arrayBuffer = await fetchResponse.arrayBuffer();

                // Decode the audio data from the MP3 file
                audioBuffers.push(await audioCtx.decodeAudioData(arrayBuffer));
                if (!isPlaying && !isPaused) {
                    playAudio();
                }
            }
        });
    } catch (error) {
        console.error('Error loading audio:', error);
    }
}


function playAudio() {
    if (!isPlaying) {
        isPaused = false;
        source = audioCtx.createBufferSource();
        source.buffer = audioBuffers[0];
        source.connect(audioCtx.destination);

        // Set up an event handler to detect when the audio has finished playing
        source.onended = function () {
            isPlaying = false;
            if (!isPaused) {
                audioBuffers.shift();
                if (audioBuffers.length > 0) {playAudio();}
            }
        };

        // Start the source to play the audio
        let offset = pauseTime;
        source.start(0, offset);
        startTime = audioCtx.currentTime - offset;
        isPlaying = true;
    }
}


function pauseAudio() {
    if (isPlaying) {
        isPaused = true;
        source.stop();
        pauseTime = audioCtx.currentTime - startTime;
        isPlaying = false;
    }
}


function stopAudio() {
    if (isPlaying) {
        source.stop();
        audioBuffers = [];
        isPlaying = false;
        pauseTime = 0;  // Reset the pause time so the audio starts from the beginning next time
    }
}


async function startRecording() {
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
            const blob = new Blob(recordedChunks, { type: 'audio/mp3' });
            recordedChunks = [];
            console.log('Blob created:', blob);
            uploadAudio(blob);
        };

        mediaRecorder.start();
    } catch (error) {
        console.error('Error starting recording:', error);
    }
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
        console.log(response);
        if (response.ok) {
            console.log('Audio uploaded successfully');
        } else {
            console.error('Error uploading audio:', response.statusText);
        }
    } catch (error) {
        console.error('Error uploading audio:', error);
    }
}


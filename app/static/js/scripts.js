// Funcionalidades adicionales (por ejemplo, reproducción de audio)
document.addEventListener('DOMContentLoaded', function () {
    const audioElements = document.querySelectorAll('audio');
    audioElements.forEach(audio => {
        audio.addEventListener('play', () => {
            audioElements.forEach(otherAudio => {
                if (otherAudio !== audio) {
                    otherAudio.pause();
                }
            });
        });
    });
});
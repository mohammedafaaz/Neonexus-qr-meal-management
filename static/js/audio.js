// Audio Feedback System using Tone.js

// Initialize audio context
let audioInitialized = false;

// Initialize audio on first user interaction
document.addEventListener('click', initializeAudio, { once: true });
document.addEventListener('touchstart', initializeAudio, { once: true });

async function initializeAudio() {
    if (!audioInitialized && typeof Tone !== 'undefined') {
        try {
            await Tone.start();
            audioInitialized = true;
            console.log('Audio context initialized');
        } catch (error) {
            console.warn('Failed to initialize audio:', error);
        }
    }
}

// Play audio feedback
function playAudio(type) {
    if (!audioInitialized || typeof Tone === 'undefined') {
        console.warn('Audio not initialized or Tone.js not loaded');
        return;
    }

    try {
        if (type === 'success') {
            playSuccessSound();
        } else if (type === 'failure') {
            playFailureSound();
        }
    } catch (error) {
        console.warn('Error playing audio:', error);
    }
}

// Success sound - Pleasant ascending tone
function playSuccessSound() {
    const synth = new Tone.Synth({
        oscillator: {
            type: "sine"
        },
        envelope: {
            attack: 0.1,
            decay: 0.2,
            sustain: 0.3,
            release: 0.5
        }
    }).toDestination();

    const melody = [
        { note: "C4", duration: "8n" },
        { note: "E4", duration: "8n" },
        { note: "G4", duration: "4n" }
    ];

    let time = Tone.now();
    melody.forEach(({ note, duration }) => {
        synth.triggerAttackRelease(note, duration, time);
        time += Tone.Time(duration).toSeconds();
    });

    // Clean up
    setTimeout(() => {
        synth.dispose();
    }, 2000);
}

// Failure sound - Short and soothing tone
function playFailureSound() {
    const synth = new Tone.Synth({
        oscillator: {
            type: "sine"
        },
        envelope: {
            attack: 0.05,
            decay: 0.1,
            sustain: 0.1,
            release: 0.2
        }
    }).toDestination();

    // Single short gentle tone
    synth.triggerAttackRelease("D4", "8n", Tone.now());

    // Clean up
    setTimeout(() => {
        synth.dispose();
    }, 500);
}

// Fallback audio for browsers without Tone.js support
function playFallbackAudio(type) {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        if (type === 'success') {
            // Success: Higher frequency, shorter duration
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(1200, audioContext.currentTime + 0.3);
        } else {
            // Failure: Lower frequency, longer duration
            oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(200, audioContext.currentTime + 0.5);
        }

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + (type === 'success' ? 0.3 : 0.5));

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + (type === 'success' ? 0.3 : 0.5));
    } catch (error) {
        console.warn('Fallback audio failed:', error);
    }
}

// Export for global use
window.playAudio = playAudio;

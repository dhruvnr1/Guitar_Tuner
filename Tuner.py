import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt

# Parameters
duration = 3        # seconds
fs = 44100          # Sampling rate

# Set default samplerate and channels
sd.default.samplerate = fs
sd.default.channels = 1

# Record audio
print("Recording audio")
myrecording = sd.rec(int(duration * fs))
sd.wait()  # Wait until recording is finished

# Compute the FFT
n = len(myrecording)
yf = np.fft.fft(myrecording[:, 0])  # Perform FFT on the first channel
xf = np.fft.fftfreq(n, 1/fs)  # Find frequency axis

# Only take the positive half of the frequencies
xf = xf[:n//2]
yf = np.abs(yf[:n//2])  # Magnitude of the FFT

# Identify the dominant frequency
peak_index = np.argmax(yf)
dominant_freq = xf[peak_index]

print(f"Dominant frequency: {dominant_freq} Hz")

# Generate a pure tone at the dominant frequency
t = np.linspace(0, duration, int(fs * duration), endpoint=False)
pure_tone = 0.5 * np.sin(2 * np.pi * dominant_freq * t)

# Plot the pure tone
plt.figure(figsize=(12, 6))
plt.plot(t, pure_tone, label='Pure Tone at Dominant Frequency')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.title('Generated Pure Tone')
plt.grid(True)
plt.show()

# Play the pure tone
print("Playing pure tone")
sd.play(pure_tone, fs)
sd.wait()

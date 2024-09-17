import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt

# Parameters
duration = 1       # seconds
fs = 44100          # Sampling rate
low_freq_threshold = 62  # Hz threshold to zero out below

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

# Zero out frequencies below 62 Hz (overtones below 62 Hz)
yf[xf < low_freq_threshold] = 0

# Harmonic Product Spectrum (HPS) to emphasize the fundamental
def harmonic_product_spectrum(yf, num_harmonics=3):
    """Apply the Harmonic Product Spectrum (HPS) to the FFT."""
    hps = yf.copy()
    for h in range(2, num_harmonics + 1):
        decimated = yf[::h]  # Downsample by a factor of h
        hps[:len(decimated)] *= decimated
    return hps

# Apply HPS to the FFT
hps_spectrum = harmonic_product_spectrum(yf)
peak_index_hps = np.argmax(hps_spectrum)
fundamental_freq_hps = xf[peak_index_hps]

print(f"Fundamental frequency using HPS: {fundamental_freq_hps} Hz")

# Generate a pure tone at the fundamental frequency
t = np.linspace(0, duration, int(fs * duration), endpoint=False)
pure_tone = 0.5 * np.sin(2 * np.pi * fundamental_freq_hps * t)

# Plot the original FFT and HPS-enhanced FFT
plt.figure(figsize=(12, 6))
plt.plot(xf, np.abs(yf), label='Filtered FFT (No Frequencies Below 62 Hz)')
plt.plot(xf, hps_spectrum, label='HPS-enhanced FFT', linestyle='--')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude')
plt.legend()
plt.title('Frequency Spectrum with Fundamental Isolation (HPS)')
plt.grid(True)
plt.show()

# Play the pure tone at the detected fundamental frequency
print("Playing pure tone at fundamental frequency")
sd.play(pure_tone, fs)
sd.wait()

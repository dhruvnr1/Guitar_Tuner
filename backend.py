import sounddevice as sd
import numpy as np
import queue

# Parameters
fs = 44100                      # Sampling rate
fft_window_size = fs            # 1 second rolling buffer
harmonics = 5                   # Number of harmonics to use in HPS
low_freq_threshold = 62         # Hz threshold to zero out below
freq_dict = {82.0: "E", 110.0: "A", 147.0: "D", 196.0: "G", 247.0: "B", 330.0: "E"}

# Rolling buffer & queue for streaming audio
audio_buffer = np.zeros(fft_window_size)
q = queue.Queue()

# Precompute Hann window to save CPU
hann_window = np.hanning(fft_window_size)

def closest_freq(val, freq_list):
    lo, hi = 0, len(freq_list) - 1
    best_ind = lo
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if freq_list[mid] < val:
            lo = mid + 1
        elif freq_list[mid] > val:
            hi = mid - 1
        else:
            best_ind = mid
            break
        if abs(freq_list[mid] - val) < abs(freq_list[best_ind] - val):
            best_ind = mid
    return freq_list[best_ind]

def freq_to_letter(freq):
    if freq < 450:
        return freq_dict[closest_freq(freq, list(freq_dict))]
    return None

def hps(signal, fs, harmonics=5):
    # Compute FFT with windowing
    fft = np.abs(np.fft.rfft(signal * hann_window))
    frequencies = np.fft.rfftfreq(len(signal), 1/fs)
    # Harmonic Product Spectrum
    hps_spectrum = np.copy(fft)
    for harmonic in range(2, harmonics + 1):
        downsampled = fft[::harmonic][:len(hps_spectrum)]
        hps_spectrum[:len(downsampled)] *= downsampled
    return frequencies, hps_spectrum

def detect_pitch(signal, fs, harmonics=5):
    frequencies, hps_spectrum = hps(signal, fs, harmonics)
    fundamental_freq = frequencies[np.argmax(hps_spectrum)]
    return fundamental_freq

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(indata.copy()[:, 0])  # Put audio samples in queue

import sounddevice as sd
import numpy as np
import tkinter as tk
from tkinter import ttk
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

def update_pitch():
    global audio_buffer
    # Pull all available chunks from queue and append to rolling buffer
    while not q.empty():
        data = q.get_nowait()
        audio_buffer = np.roll(audio_buffer, -len(data))
        audio_buffer[-len(data):] = data

    # Detect pitch from rolling buffer
    fundamental_freq = detect_pitch(audio_buffer, fs, harmonics)
    if fundamental_freq < 450:
        expected_freq = closest_freq(fundamental_freq, list(freq_dict))
        note = freq_to_letter(fundamental_freq)
        freq_label.config(text=f"Frequency: {fundamental_freq:.2f} Hz ({expected_freq:.2f} Hz)")
        note_label.config(text=f"Note: {note}")

    root.after(50, update_pitch)  # Update every 50ms

# Set up GUI
root = tk.Tk()
root.title("Tuner")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 18), background="#f0f0f0")

freq_label = ttk.Label(root, text="Frequency: ", style="TLabel")
freq_label.pack(pady=20)

note_label = ttk.Label(root, text="Note: ", style="TLabel")
note_label.pack(pady=20)

# Start audio stream in the background
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=fs, blocksize=2048)
stream.start()

# Start GUI loop with continuous pitch updates
root.after(50, update_pitch)
root.mainloop()

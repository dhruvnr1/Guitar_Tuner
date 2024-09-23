import sounddevice as sd
import numpy as np
import tkinter as tk
from tkinter import ttk

# Parameters
duration = 1      # seconds
fs = 44100         # Sampling rate
harmonics = 5      # Number of harmonics to use in HPS
low_freq_threshold = 62  # Hz threshold to zero out below
freq_dict = {82.0: "E", 110.0: "A", 147.0: "D", 196.0: "G", 247.0: "B", 330.0: "E"}

prev_note = "E"
prev_freq = 0

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
    global prev_note
    if freq < 450:
        prev_note = freq_dict[closest_freq(freq, list(freq_dict))]
    return prev_note

def hps(signal, fs, harmonics=5):
    # Compute the Harmonic Product Spectrum (HPS)
    windowed_signal = signal * np.hanning(len(signal))
    #Split sound into seperate frequencies using fft
    fft = np.abs(np.fft.rfft(windowed_signal))
    frequencies = np.fft.rfftfreq(len(signal), 1/fs)
    #Apply HPS alg to downsample conflicting frequencies
    hps_spectrum = np.copy(fft)
    for harmonic in range(2, harmonics + 1):
        downsampled = fft[::harmonic][:len(hps_spectrum)]
        hps_spectrum[:len(downsampled)] *= downsampled
    
    return frequencies, hps_spectrum

def detect_pitch(signal, fs, harmonics=5):

    #Detect the fundamental frequency using HPS
    frequencies, hps_spectrum = hps(signal, fs, harmonics)
    #Find the now isolated highest frequency
    fundamental_freq = frequencies[np.argmax(hps_spectrum)]
    return fundamental_freq

def update_pitch():
    global prev_freq
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    
    # Detect pitch
    fundamental_freq = detect_pitch(myrecording[:, 0], fs, harmonics)
    if fundamental_freq < 450:
        prev_freq = fundamental_freq

    # Get the closest frequency and note
    expected_freq = closest_freq(prev_freq, list(freq_dict))
    note = freq_to_letter(prev_freq)

    # Update GUI labels with actual frequency and expected frequency
    freq_label.config(text=f"Frequency: {prev_freq:.2f} Hz ({expected_freq:.2f} Hz)")
    note_label.config(text=f"Note: {note}")
    
    root.after(1000, update_pitch)

# Set up GUI
root = tk.Tk()
root.title("Tuner")

# Make the window larger and center it
root.geometry("400x300")
root.configure(bg="#f0f0f0")

# Set custom styles for the labels
style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 18), background="#f0f0f0")

# Frequency label
freq_label = ttk.Label(root, text="Frequency: ", style="TLabel")
freq_label.pack(pady=20)

# Note label
note_label = ttk.Label(root, text="Note: ", style="TLabel")
note_label.pack(pady=20)

# Start the pitch detection
root.after(1000, update_pitch)

# Run the GUI event loop
root.mainloop()

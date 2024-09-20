import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import collections
import bisect

# Parameters
duration = 1       # seconds
fs = 44100          # Sampling rate
low_freq_threshold = 62  # Hz threshold to zero out below
harmonics = 5       # Number of harmonics to use in HPS
runs = 50
# Set default samplerate and channels
sd.default.samplerate = fs
sd.default.channels = 1
freq_dict = {82.0 : "E", 110.0 : "A", 147.0 : "D",
              196.0 : "G", 247.0 : "B", 330.0: "E"}
prev_note = "E"
prev_freq = 0
def closest_freq(val, list):
    lo, hi = 0, len(list) - 1
    best_ind = lo
    while lo <= hi: 
      mid = lo + (hi - lo) // 2
      if(list[mid] < val):
          lo = mid + 1
      elif list[mid] > val:
          hi = mid - 1
      else: 
         best_ind = mid
         break
      if abs(list[mid] - val) < abs(list[best_ind] - val):
            best_ind = mid
    return list[best_ind]

def freq_to_letter(freq):
    if freq < 450:
        global prev_note
        prev_note = freq_dict[closest_freq(freq, list(freq_dict))]

def hps(signal, fs, harmonics=5):
    
    #Compute the Harmonic Product Spectrum (HPS)

    #Apply a hanning window to limit the signal width
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

while runs > 0:
   # Record audio
   #print("Recording audio")
   myrecording = sd.rec(int(duration * fs))
   sd.wait()  # Wait until recording is finished
   #print("Recording finished.")

   # Detect pitch
   fundamental_freq = detect_pitch(myrecording[:, 0], fs, harmonics)
   if fundamental_freq < 450:
       prev_freq = fundamental_freq
   #print(f"Detected fundamental frequency: {fundamental_freq:.2f} Hz")
   print(prev_freq, "(", closest_freq(prev_freq, list(freq_dict)), 
         ")")
   freq_to_letter(prev_freq)
   #print("Closest to:", prev_note)
   # # Generate a pure tone at the fundamental frequency
   # t = np.linspace(0, duration, int(fs * duration), endpoint=False)
   # pure_tone = 0.5 * np.sin(2 * np.pi * fundamental_freq * t)

   # # Play the pure tone at the detected fundamental frequency
   # print("Playing pure tone at fundamental frequency")
   # sd.play(pure_tone, fs)
   # sd.wait()

   # # Plot the original FFT and HPS
   # plt.figure(figsize=(12, 8))

   # # Original FFT
   # fft = np.abs(np.fft.rfft(myrecording[:, 0]))
   # freq = np.fft.rfftfreq(len(myrecording[:, 0]), 1/fs)
   # plt.subplot(2, 1, 1)
   # plt.plot(freq, fft)
   # plt.title('Original FFT')
   # plt.xlabel('Frequency [Hz]')
   # plt.ylabel('Amplitude')

   # # HPS
   # frequencies, hps_spectrum = hps(myrecording[:, 0], fs, harmonics)
   # plt.subplot(2, 1, 2)
   # plt.plot(frequencies, hps_spectrum)
   # plt.title('Harmonic Product Spectrum')
   # plt.xlabel('Frequency [Hz]')
   # plt.ylabel('Amplitude')

   # plt.tight_layout()
   # plt.show()
   runs = runs - 1
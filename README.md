# 🎵 Real-Time Pitch Detection Tuner

This is a Python-based real-time pitch detection tuner that uses the **Harmonic Product Spectrum (HPS)** algorithm to identify musical notes from audio input. It features a simple **Tkinter GUI** to display the detected frequency and its corresponding musical note, commonly used for tuning guitar strings.

---

## 📦 Features

- 🎤 Live audio capture via microphone
- 📊 Harmonic Product Spectrum (HPS) pitch detection
- 🔠 Maps frequency to nearest guitar string (E A D G B E)
- 🪟 Clean, responsive Tkinter GUI

---

## TO-DO
 - Revamp UI with ideal TKinter library but retain core visual features
 - Package into executable file
## ChangeLog
 - Improve visual experience using Tkinter library
   - Added bar meter to represent proximity to note
   - Made meter fluid and change color if closest to note
 - Reduce pipeline lag using optimizations
   - Switched to using streaming for audio
   - Enabled concurency in pipeline, dropped latency to 50ms rather than 1 second

---

## 🛠️ Requirements

Install the required Python packages with:

```bash
pip install sounddevice numpy
Python 3.7+ is recommended.

🚀 Usage
Run the tuner using:

bash
Copy
Edit
python tuner.py
Once launched:

The GUI will update every second with:

The detected pitch in Hz

The closest matching guitar note

The algorithm ignores frequencies above 450 Hz (useful for standard guitar tuning range)

🎸 Supported Guitar Notes
This tuner supports standard 6-string tuning:

String	Frequency (Hz)
E (low)	82.0
A	110.0
D	147.0
G	196.0
B	247.0
E (high)	330.0

🧠 How It Works
Audio Recording: Uses sounddevice to capture 1 second of mono audio.

Windowing: Applies a Hann window to reduce spectral leakage.

FFT: Transforms audio to frequency domain.

HPS Algorithm: Downsamples and multiplies spectra to isolate the fundamental frequency.

Note Matching: Matches frequency to the closest known guitar string using a binary search.

GUI Update: Displays the frequency and note using tkinter.

🖼 GUI Preview
A simple, centered window displays the detected frequency and note in real time.

📌 Notes
You may need to allow microphone access if prompted.

For better accuracy, try using this in a quiet environment.

The tuner is optimized for fundamental frequencies under 450 Hz, making it ideal for guitar tuning.

📃 License
MIT License – free to use and modify.

🙌 Credits
Developed using:

sounddevice

NumPy

Tkinter

yaml
Copy
Edit

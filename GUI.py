import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import backend

def update_pitch():
    # Pull all available chunks from queue and append to rolling buffer
    while not backend.q.empty():
        data = backend.q.get_nowait()
        backend.audio_buffer = backend.np.roll(backend.audio_buffer, -len(data))
        backend.audio_buffer[-len(data):] = data

    # Detect pitch from rolling buffer
    fundamental_freq = backend.detect_pitch(backend.audio_buffer, backend.fs, backend.harmonics)
    if fundamental_freq < 450:
        expected_freq = backend.closest_freq(fundamental_freq, list(backend.freq_dict))
        note = backend.freq_to_letter(fundamental_freq)
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
stream = sd.InputStream(callback=backend.audio_callback, channels=1, samplerate=backend.fs, blocksize=2048)
stream.start()

# Start GUI loop with continuous pitch updates
root.after(50, update_pitch)
root.mainloop()

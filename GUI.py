import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import backend

# Variables to track note switching
closest_note = None
closest_note_freq = None

def update_pitch():
    global closest_note, closest_note_freq

    # Pull all available chunks from queue and append to rolling buffer
    while not backend.q.empty():
        data = backend.q.get_nowait()
        backend.audio_buffer = backend.np.roll(backend.audio_buffer, -len(data))
        backend.audio_buffer[-len(data):] = data

    # Detect pitch from rolling buffer
    fundamental_freq = backend.detect_pitch(backend.audio_buffer, backend.fs, backend.harmonics)
    if fundamental_freq < 450:
        # Find closest note frequency
        expected_freq = backend.closest_freq(fundamental_freq, list(backend.freq_dict))
        note = backend.freq_to_letter(expected_freq)

        # Update if note has changed
        if closest_note != note:
            closest_note = note
            closest_note_freq = expected_freq

        # If pitch is closer to another note, switch
        second_closest = backend.closest_freq(fundamental_freq, [f for f in backend.freq_dict if f != closest_note_freq])
        if abs(fundamental_freq - second_closest) < abs(fundamental_freq - closest_note_freq):
            closest_note_freq = second_closest
            closest_note = backend.freq_to_letter(second_closest)

        # Update labels
        freq_label.config(text=f"Frequency: {fundamental_freq:.2f} Hz ({closest_note_freq:.2f} Hz)")
        note_label.config(text=f"Note: {closest_note}")

        # Calculate meter position (percentage)
        half_range = (second_closest - closest_note_freq) / 2 if second_closest > closest_note_freq else (closest_note_freq - second_closest) / 2
        deviation = (fundamental_freq - closest_note_freq) / half_range
        deviation = max(-1, min(1, deviation))  # clamp between -1 and 1

        meter_pos = (deviation + 1) * 50  # map [-1, 1] to [0, 100]
        meter_var.set(meter_pos)

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

# Meter widget
meter_var = tk.DoubleVar(value=50)  # start in the middle
meter = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", variable=meter_var, maximum=100)
meter.pack(pady=20)

# Start audio stream in the background
stream = sd.InputStream(callback=backend.audio_callback, channels=1, samplerate=backend.fs, blocksize=2048)
stream.start()

# Start GUI loop with continuous pitch updates
root.after(50, update_pitch)
root.mainloop()

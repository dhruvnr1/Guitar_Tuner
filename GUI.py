import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import backend
import math

# Variables to track note switching
closest_note = None
closest_note_freq = None


class BarMeter(tk.Canvas):
    def __init__(self, parent, width=300, height=60, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg="#f0f0f0", highlightthickness=0, **kwargs)
        self.width = width
        self.height = height

        # Mid point (0 cents)
        self.mid = self.width // 2

        # Draw baseline
        self.create_line(0, self.height // 2,
                         self.width, self.height // 2, fill="black", width=2)

        # Draw tick marks every 10 cents
        for cents in range(-50, 51, 10):
            x = self.mid + (cents / 50) * (self.width // 2)

            if cents % 50 == 0:  # -50, 0, +50 big ticks
                self.create_line(x, 0, x, self.height, fill="black", width=2)
            elif cents % 20 == 0:  # medium ticks
                self.create_line(x, 10, x, self.height - 10, fill="black", width=2)
            else:  # small ticks
                self.create_line(x, 15, x, self.height - 15, fill="black")

            # Label only -50, 0, +50
            if cents in (-50, 0, 50):
                self.create_text(x, self.height - 5, text=str(cents),
                                 anchor="n", font=("Helvetica", 10))

        self.bar = None
        self.update_bar(0)

    def update_bar(self, cents_deviation):
        """
        cents_deviation: -50 to +50
        """
        cents_deviation = max(-50, min(50, cents_deviation))

        # Map to bar position
        pos = self.mid + (cents_deviation / 50) * (self.width // 2)

        # Clear old bar
        if self.bar:
            self.delete(self.bar)

        # Draw bar
        color = "green" if abs(cents_deviation) < 5 else "red"
        self.bar = self.create_rectangle(self.mid, 5, pos,
                                         self.height - 20, fill=color)


def update_pitch():
    global closest_note, closest_note_freq

    # Pull all available chunks from queue and append to rolling buffer
    while not backend.q.empty():
        data = backend.q.get_nowait()
        backend.audio_buffer = backend.np.roll(
            backend.audio_buffer, -len(data))
        backend.audio_buffer[-len(data):] = data

    # Detect pitch from rolling buffer
    fundamental_freq = backend.detect_pitch(
        backend.audio_buffer, backend.fs, backend.harmonics)

    if fundamental_freq > 0 and fundamental_freq < 450:
        # Find closest note frequency
        expected_freq = backend.closest_freq(
            fundamental_freq, list(backend.freq_dict))
        note = backend.freq_to_letter(expected_freq)

        # Update if note has changed
        if closest_note != note:
            closest_note = note
            closest_note_freq = expected_freq

        # If pitch is closer to another note, switch
        second_closest = backend.closest_freq(
            fundamental_freq, [f for f in backend.freq_dict if f != closest_note_freq])
        if abs(fundamental_freq - second_closest) < abs(fundamental_freq - closest_note_freq):
            closest_note_freq = second_closest
            closest_note = backend.freq_to_letter(second_closest)

        # Update labels
        freq_label.config(
            text=f"Frequency: {fundamental_freq:.2f} Hz ({closest_note_freq:.2f} Hz)")
        note_label.config(text=f"Note: {closest_note}")

        # --- Compute cents deviation safely ---
        if fundamental_freq > 0 and closest_note_freq > 0:
            cents = 1200 * math.log2(fundamental_freq / closest_note_freq)
            cents = max(-50, min(50, cents))  # clamp
        else:
            cents = 0

        # Update bar meter
        meter.update_bar(cents)

        # Show cents deviation text
        cents_label.config(text=f"Deviation: {cents:+.1f} cents")

    root.after(50, update_pitch)  # Update every 50ms


# Set up GUI
root = tk.Tk()
root.title("Tuner")
root.geometry("400x400")
root.configure(bg="#f0f0f0")

style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 18), background="#f0f0f0")

freq_label = ttk.Label(root, text="Frequency: ", style="TLabel")
freq_label.pack(pady=10)

note_label = ttk.Label(root, text="Note: ", style="TLabel")
note_label.pack(pady=10)

cents_label = ttk.Label(root, text="Deviation: 0.0 cents", style="TLabel")
cents_label.pack(pady=10)

# Symmetric bar meter with ticks
meter = BarMeter(root, width=300, height=60)
meter.pack(pady=20)

# Start audio stream in the background
stream = sd.InputStream(callback=backend.audio_callback,
                        channels=1, samplerate=backend.fs, blocksize=2048)
stream.start()

# Start GUI loop with continuous pitch updates
root.after(50, update_pitch)
root.mainloop()

import tkinter as tk
from datetime import datetime, timedelta
import threading
import time
import pygame
import math

class AlertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("5-Minute Alert")
        self.is_running = False
        self.alert_thread = None
        self.clock_thread = None

        # Initialize pygame mixer for sound
        pygame.mixer.init()
        try:
            self.alert_sound = pygame.mixer.Sound("alert_digdong.mp3")
        except FileNotFoundError:
            print("alert.wav not found, using fallback message")
            self.alert_sound = None
        try:
            self.hour_alert_sound = pygame.mixer.Sound("alert_dodo.mp3")
        except FileNotFoundError:
            print("hour_alert.wav not found, using fallback message")
            self.hour_alert_sound = None

        self.volume = 0.5
        if self.alert_sound:
            self.alert_sound.set_volume(self.volume)
        if self.hour_alert_sound:
            self.hour_alert_sound.set_volume(self.volume)

        # --- Mobile-like UI Design ---

        # Header bar
        self.header = tk.Frame(root, bg="#1976D2", height=60)
        self.header.pack(fill=tk.X)
        self.header_label = tk.Label(
            self.header, text="5-Minute Alert", fg="white", bg="#1976D2",
            font=("Segoe UI", 20, "bold")
        )
        self.header_label.pack(pady=10)

        # Countdown timer (large and centered)
        self.timer_frame = tk.Frame(root, bg="white")
        self.timer_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.canvas = tk.Canvas(self.timer_frame, width=180, height=180, bg="white", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.canvas.create_oval(20, 20, 160, 160, fill="#E3F2FD", outline="#90CAF9", width=4)
        self.countdown_arc = self.canvas.create_arc(
            20, 20, 160, 160, start=90, extent=0, fill="#1976D2", outline="#1976D2"
        )
        self.countdown_text = self.canvas.create_text(
            90, 90, text="--:--", font=("Segoe UI", 32, "bold"), fill="#212121"  # Changed color to dark gray
        )

        # Current time
        self.clock_label = tk.Label(
            root, text="Current Time: --:--:--", font=("Segoe UI", 16), bg="white", fg="#1976D2"
        )
        self.clock_label.pack(pady=(0, 10))

        # Status label
        self.status_label = tk.Label(
            root, text="Status: Stopped", font=("Segoe UI", 14), bg="white", fg="#757575"
        )
        self.status_label.pack(pady=(0, 10))

        # Start/Stop buttons (large, rounded)
        self.button_frame = tk.Frame(root, bg="white")
        self.button_frame.pack(pady=10)
        self.start_button = tk.Button(
            self.button_frame, text="Start", command=self.start_alerts,
            font=("Segoe UI", 14, "bold"), bg="#43A047", fg="white",
            activebackground="#388E3C", activeforeground="white",
            relief="flat", bd=0, padx=30, pady=10
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.stop_button = tk.Button(
            self.button_frame, text="Stop", command=self.stop_alerts, state="disabled",
            font=("Segoe UI", 14, "bold"), bg="#E53935", fg="white",
            activebackground="#B71C1C", activeforeground="white",
            relief="flat", bd=0, padx=30, pady=10
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Volume slider (styled)
        self.volume_frame = tk.Frame(root, bg="white")
        self.volume_frame.pack(pady=10)
        self.volume_label = tk.Label(
            self.volume_frame, text="Volume:", font=("Segoe UI", 12), bg="white", fg="#1976D2"
        )
        self.volume_label.pack(side=tk.LEFT)
        self.volume_slider = tk.Scale(
            self.volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=150,
            command=self.update_volume, bg="white", fg="#1976D2", highlightthickness=0
        )
        self.volume_slider.set(self.volume * 100)
        self.volume_slider.pack(side=tk.LEFT, padx=5)

        # Set background color for root
        root.configure(bg="white")

    def update_volume(self, value):
        self.volume = float(value) / 100
        if self.alert_sound:
            self.alert_sound.set_volume(self.volume)
        if self.hour_alert_sound:
            self.hour_alert_sound.set_volume(self.volume)

    def start_alerts(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="Status: Running")

            if self.alert_sound:
                self.alert_sound.play()
            else:
                print("Beep! (Start)")
            self.status_label.config(text=f"Alert at {datetime.now().strftime('%H:%M')} (Start)")

            self.alert_thread = threading.Thread(target=self.alert_loop)
            self.alert_thread.daemon = True
            self.alert_thread.start()
            self.clock_thread = threading.Thread(target=self.update_clock_and_countdown)
            self.clock_thread.daemon = True
            self.clock_thread.start()

    def stop_alerts(self):
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Status: Stopped")
        self.clock_label.config(text="Current Time: --:--:--")
        self.canvas.itemconfig(self.countdown_text, text="--:--")
        self.canvas.itemconfig(self.countdown_arc, extent=0)

    def alert_loop(self):
        while self.is_running:
            now = datetime.now()
            current_minute = now.minute
            current_second = now.second

            if current_minute % 5 == 0 and current_second < 5:
                if current_minute == 0:
                    if self.hour_alert_sound:
                        self.hour_alert_sound.play()
                    else:
                        print("Hour Beep!")
                    self.status_label.config(text=f"Hour Alert at {now.strftime('%H:%M')}")
                else:
                    if self.alert_sound:
                        self.alert_sound.play()
                    else:
                        print("Beep!")
                    self.status_label.config(text=f"Alert at {now.strftime('%H:%M')}")
                time.sleep(60)
            else:
                time.sleep(1)

    def update_clock_and_countdown(self):
        while self.is_running:
            now = datetime.now()
            self.clock_label.config(text=f"Current Time: {now.strftime('%H:%M:%S')}")

            current_minute = now.minute
            current_second = now.second
            seconds_since_last_mark = (current_minute % 5) * 60 + current_second
            seconds_to_next_mark = (5 * 60) - seconds_since_last_mark
            minutes, seconds = divmod(seconds_to_next_mark, 60)
            self.canvas.itemconfig(self.countdown_text, text=f"{minutes:02d}:{seconds:02d}")

            fraction_remaining = seconds_to_next_mark / (5 * 60)
            arc_extent = 360 * fraction_remaining
            self.canvas.itemconfig(self.countdown_arc, extent=-arc_extent)

            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = AlertApp(root)
    root.geometry("320x520")
    root.mainloop()
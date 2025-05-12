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
            self.alert_sound = pygame.mixer.Sound("alert_digdong.mp3")  # Regular 5-minute alert
        except FileNotFoundError:
            print("alert.wav not found, using fallback message")
            self.alert_sound = None
        try:
            self.hour_alert_sound = pygame.mixer.Sound("alert_dodo.mp3")  # Hourly alert
        except FileNotFoundError:
            print("hour_alert.wav not found, using fallback message")
            self.hour_alert_sound = None

        # GUI Elements
        # Frame for buttons at the top
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)
        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_alerts)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_alerts, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(root, text="Status: Stopped")
        self.status_label.pack(pady=5)
        self.clock_label = tk.Label(root, text="Current Time: --:--:--")
        self.clock_label.pack(pady=5)

        # Canvas for circular countdown
        self.canvas = tk.Canvas(root, width=150, height=150)
        self.canvas.pack(pady=5)
        # Background circle (full duration, gray)
        self.canvas.create_oval(25, 25, 125, 125, fill="lightgray", outline="gray")
        # Countdown arc (remaining time, green)
        self.countdown_arc = self.canvas.create_arc(
            25, 25, 125, 125, start=90, extent=0, fill="skyblue", outline="skyblue"
        )
        # Countdown text (mm:ss)
        self.countdown_text = self.canvas.create_text(75, 75, text="--:--", font=("Arial", 16))

    def start_alerts(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="Status: Running")

            # Play regular alert sound immediately
            if self.alert_sound:
                self.alert_sound.play()
            else:
                print("Beep! (Start)")
            self.status_label.config(text=f"Alert at {datetime.now().strftime('%H:%M')} (Start)")

            # Start threads
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

            # Check for 5-minute mark
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
            # Update current time
            self.clock_label.config(text=f"Current Time: {now.strftime('%H:%M:%S')}")

            # Calculate countdown to next 5-minute mark
            current_minute = now.minute
            current_second = now.second
            seconds_since_last_mark = (current_minute % 5) * 60 + current_second
            seconds_to_next_mark = (5 * 60) - seconds_since_last_mark
            minutes, seconds = divmod(seconds_to_next_mark, 60)
            self.canvas.itemconfig(self.countdown_text, text=f"{minutes:02d}:{seconds:02d}")

            # Update pie arc (extent proportional to time remaining)
            fraction_remaining = seconds_to_next_mark / (5 * 60)
            arc_extent = 360 * fraction_remaining
            self.canvas.itemconfig(self.countdown_arc, extent=-arc_extent)

            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = AlertApp(root)
    root.geometry("250x300")
    root.mainloop()
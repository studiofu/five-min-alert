import tkinter as tk
from datetime import datetime, timedelta
import threading
import time
import pygame

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
            # Load regular 5-minute alert sound
            self.alert_sound = pygame.mixer.Sound("alert3.mp3")  # Regular 5-minute alert sound
        except FileNotFoundError:
            print("alert.wav not found, using fallback message for regular alerts")
            self.alert_sound = None
        try:
            # Load hourly alert sound
            self.hour_alert_sound = pygame.mixer.Sound("alert2.mp3")  # Hourly alert sound
        except FileNotFoundError:
            print("hour_alert.wav not found, using fallback message for hourly alerts")
            self.hour_alert_sound = None

        # GUI Elements
        self.start_button = tk.Button(root, text="Start", command=self.start_alerts)
        self.start_button.pack(pady=10)
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_alerts, state="disabled")
        self.stop_button.pack(pady=10)
        self.status_label = tk.Label(root, text="Status: Stopped")
        self.status_label.pack(pady=5)
        self.clock_label = tk.Label(root, text="Current Time: --:--:--")
        self.clock_label.pack(pady=5)
        self.countdown_label = tk.Label(root, text="Next Alert: --:--")
        self.countdown_label.pack(pady=5)

    def start_alerts(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="Status: Running")

            # Play regular alert sound immediately when Start is pressed
            if self.alert_sound:
                self.alert_sound.play()
            else:
                print("Beep! (Start)")
            self.status_label.config(text=f"Alert at {datetime.now().strftime('%H:%M')} (Start)")

            # Start the alert and clock threads
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
        self.countdown_label.config(text="Next Alert: --:--")

    def alert_loop(self):
        while self.is_running:
            now = datetime.now()
            current_minute = now.minute
            current_second = now.second

            # Check if the minute is a multiple of 5 and seconds are close to 0
            if current_minute % 5 == 0 and current_second < 5:
                # Check if it's a whole hour (00 minutes)
                if current_minute == 0:
                    if self.hour_alert_sound:
                        self.hour_alert_sound.play()  # Play hourly alert sound
                    else:
                        print("Hour Beep!")
                    self.status_label.config(text=f"Hour Alert at {now.strftime('%H:%M')}")
                else:
                    if self.alert_sound:
                        self.alert_sound.play()  # Play regular 5-minute alert sound
                    else:
                        print("Beep!")
                    self.status_label.config(text=f"Alert at {now.strftime('%H:%M')}")
                time.sleep(60)  # Sleep for a minute to avoid multiple alerts
            else:
                time.sleep(1)  # Check every second

    def update_clock_and_countdown(self):
        while self.is_running:
            now = datetime.now()
            # Update current time
            self.clock_label.config(text=f"Current Time: {now.strftime('%H:%M:%S')}")

            # Calculate time to next 5-minute mark
            current_minute = now.minute
            current_second = now.second
            seconds_since_last_mark = (current_minute % 5) * 60 + current_second
            seconds_to_next_mark = (5 * 60) - seconds_since_last_mark
            minutes, seconds = divmod(seconds_to_next_mark, 60)
            self.countdown_label.config(text=f"Next Alert: {minutes:02d}:{seconds:02d}")

            time.sleep(1)  # Update every second

if __name__ == "__main__":
    root = tk.Tk()
    app = AlertApp(root)
    root.geometry("250x200")
    root.mainloop()
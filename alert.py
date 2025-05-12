import tkinter as tk
from datetime import datetime
import threading
import time
import winsound  # For Windows alert sound (use alternative for other OS)

class AlertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("5-Minute Alert")
        self.is_running = False
        self.alert_thread = None

        # GUI Elements
        self.start_button = tk.Button(root, text="Start", command=self.start_alerts)
        self.start_button.pack(pady=10)
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_alerts, state="disabled")
        self.stop_button.pack(pady=10)
        self.status_label = tk.Label(root, text="Status: Stopped")
        self.status_label.pack(pady=10)

    def start_alerts(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="Status: Running")
            self.alert_thread = threading.Thread(target=self.alert_loop)
            self.alert_thread.daemon = True
            self.alert_thread.start()

    def stop_alerts(self):
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Status: Stopped")

    def alert_loop(self):
        while self.is_running:
            now = datetime.now()
            current_minute = now.minute
            current_second = now.second

            # Check if the minute is a multiple of 5 and seconds are close to 0
            if current_minute % 5 == 0 and current_second < 5:
                winsound.Beep(1000, 500)  # 1000 Hz, 500 ms beep
                self.status_label.config(text=f"Alert at {now.strftime('%H:%M')}")
                time.sleep(60)  # Sleep for a minute to avoid multiple alerts
            else:
                time.sleep(1)  # Check every second

if __name__ == "__main__":
    root = tk.Tk()
    app = AlertApp(root)
    root.geometry("200x150")
    root.mainloop()
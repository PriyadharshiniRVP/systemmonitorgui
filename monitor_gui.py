import os
import psutil
import smtplib
import threading
import time
import tkinter as tk
from tkinter import ttk
from email.mime.text import MIMEText

# Configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Use environment variable
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
CPU_THRESHOLD = 80  # Percentage
RAM_THRESHOLD = 80  # Percentage
DISK_THRESHOLD = 80  # Percentage

monitoring = False  # Global flag to control monitoring


# Function to send email alerts
def send_email_alert(subject, message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS  # Sending to self

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        log_label.config(text="📧 Email Alert Sent!", fg="green")
    except Exception as e:
        log_label.config(text=f"Error sending email: {e}", fg="red")


# Function to check system health
def check_system_health():
    global monitoring
    while monitoring:
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage("/").percent

        # Update GUI values
        cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
        ram_label.config(text=f"RAM Usage: {ram_usage}%")
        disk_label.config(text=f"Disk Usage: {disk_usage}%")

        # Update progress bars
        cpu_progress["value"] = cpu_usage
        ram_progress["value"] = ram_usage
        disk_progress["value"] = disk_usage

        alerts = []
        if cpu_usage > CPU_THRESHOLD:
            alerts.append(f"⚠️ CPU usage high: {cpu_usage}%")
        if ram_usage > RAM_THRESHOLD:
            alerts.append(f"⚠️ RAM usage high: {ram_usage}%")
        if disk_usage > DISK_THRESHOLD:
            alerts.append(f"⚠️ Disk usage high: {disk_usage}%")

        if alerts:
            alert_message = "\n".join(alerts)
            send_email_alert("System Health Alert", alert_message)

        time.sleep(2)  # Update every 2 seconds


# Start monitoring
def start_monitoring():
    global monitoring
    if not monitoring:
        monitoring = True
        monitor_button.config(state="disabled")
        stop_button.config(state="normal")
        thread = threading.Thread(target=check_system_health, daemon=True)
        thread.start()
        log_label.config(text="✅ Monitoring started...", fg="blue")


# Stop monitoring
def stop_monitoring():
    global monitoring
    monitoring = False
    monitor_button.config(state="normal")
    stop_button.config(state="disabled")
    log_label.config(text="🛑 Monitoring stopped!", fg="red")


# GUI setup
root = tk.Tk()
root.title("System Health Monitor")
root.geometry("400x300")
root.resizable(False, False)

# Labels
cpu_label = tk.Label(root, text="CPU Usage: 0%", font=("Arial", 12))
cpu_label.pack(pady=5)
cpu_progress = ttk.Progressbar(root, length=300, mode="determinate", maximum=100)
cpu_progress.pack(pady=5)

ram_label = tk.Label(root, text="RAM Usage: 0%", font=("Arial", 12))
ram_label.pack(pady=5)
ram_progress = ttk.Progressbar(root, length=300, mode="determinate", maximum=100)
ram_progress.pack(pady=5)

disk_label = tk.Label(root, text="Disk Usage: 0%", font=("Arial", 12))
disk_label.pack(pady=5)
disk_progress = ttk.Progressbar(root, length=300, mode="determinate", maximum=100)
disk_progress.pack(pady=5)

# Start & Stop Buttons
monitor_button = tk.Button(root, text="Start Monitoring", command=start_monitoring, bg="green", fg="white")
monitor_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Monitoring", command=stop_monitoring, bg="red", fg="white", state="disabled")
stop_button.pack(pady=5)

# Log Label
log_label = tk.Label(root, text="Click 'Start Monitoring' to begin...", font=("Arial", 10), fg="gray")
log_label.pack(pady=5)

# Run GUI
root.mainloop()

import tkinter as tk
import threading
import time
import random
import ctypes
from ctypes import wintypes

# Windows API setup
MOUSEEVENTF_MOVE = 0x0001
KEYEVENTF_KEYUP = 0x0002
WM_HOTKEY = 0x0312
VK_F6 = 0x75

user32 = ctypes.windll.user32

# Globals
running = False
kill_flag = False

def move_mouse(dx, dy):
    user32.mouse_event(MOUSEEVENTF_MOVE, dx, dy, 0, 0)

def press_and_release(vk_code, hold_time=0.05):
    user32.keybd_event(vk_code, 0, 0, 0)
    time.sleep(hold_time)
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

VK = {
    'W': 0x57,
    'A': 0x41,
    'S': 0x53,
    'D': 0x44,
    'F': 0x46
}

def movement_loop():
    global running, kill_flag
    last_f_time = time.time()

    while running and not kill_flag:
        # Mouse sweep
        move_amount = random.randint(4, 14)
        jitter_y = random.randint(-3, 3)
        move_mouse(move_amount, jitter_y)
        time.sleep(0.025 + random.random() * 0.035)
        move_mouse(-move_amount - random.randint(0, 4), random.randint(-3, 3))
        time.sleep(0.04 + random.random() * 0.04)

        # Micro WASD
        if random.random() < 0.65:
            key = random.choice(['W', 'A', 'S', 'D'])
            hold = 0.018 + random.random() * 0.055
            press_and_release(VK[key], hold)

        # F press ~7-13s
        if time.time() - last_f_time > (7 + random.random() * 6):
            press_and_release(VK['F'], 0.05)
            last_f_time = time.time()

        time.sleep(0.08 + random.random() * 0.35)

def countdown_and_start():
    global running
    for i in range(5, 0, -1):
        if not running or kill_flag:
            return
        status_label.config(text=f"Starting in {i}...", fg="#ffcc00")
        root.update()
        time.sleep(1)

    if not running or kill_flag:
        return

    status_label.config(text="RUNNING — F6 to kill", fg="#00ff99")
    launch_btn.config(state="disabled")
    stop_btn.config(state="normal")

    t_move = threading.Thread(target=movement_loop, daemon=True)
    t_move.start()

    t_hot = threading.Thread(target=hotkey_listener, daemon=True)
    t_hot.start()

    root.after(100, check_for_kill)

def hotkey_listener():
    global kill_flag
    if not user32.RegisterHotKey(None, 1, 0, VK_F6):
        print("Could not register F6 hotkey (already in use?)")
        return

    try:
        msg = wintypes.MSG()
        while True:
            if user32.GetMessageA(ctypes.byref(msg), None, 0, 0) <= 0:
                break
            if msg.message == WM_HOTKEY and msg.wParam == 1:
                kill_flag = True
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageA(ctypes.byref(msg))
    finally:
        user32.UnregisterHotKey(None, 1)

def launch():
    global running, kill_flag
    if running:
        return
    kill_flag = False
    running = True
    launch_btn.config(state="disabled")
    stop_btn.config(state="disabled")  # enable only after countdown
    status_label.config(text="Starting in 5...", fg="#ffcc00")
    threading.Thread(target=countdown_and_start, daemon=True).start()

def stop():
    global running
    running = False
    status_label.config(text="STOPPED", fg="#ff4444")
    launch_btn.config(state="normal")
    stop_btn.config(state="disabled")

def check_for_kill():
    global running, kill_flag
    if kill_flag:
        running = False
        status_label.config(text="KILLED by F6", fg="#ff4444")
        launch_btn.config(state="normal")
        stop_btn.config(state="disabled")
        root.quit()
        return
    root.after(100, check_for_kill)

def on_close():
    global running
    running = False
    root.destroy()

root = tk.Tk()
root.title("0MNI.B0T")
root.geometry("360x300")
root.resizable(False, False)
root.attributes("-topmost", True)
root.configure(bg="#0d0d0d")

# Title area
title_frame = tk.Frame(root, bg="#0d0d0d")
title_frame.pack(pady=(20, 5))

tk.Label(title_frame, text="0MNI.B0T", font=("Arial", 24, "bold", "italic"),
         fg="#ffffff", bg="#0d0d0d").pack()

tk.Label(title_frame, text="made by fragment", font=("Arial", 9),
         fg="#aaaaaa", bg="#0d0d0d").pack()

# Buttons
btn_frame = tk.Frame(root, bg="#0d0d0d")
btn_frame.pack(pady=15)

launch_btn = tk.Button(btn_frame, text="LAUNCH", font=("Arial", 14, "bold"),
                       bg="#006600", fg="white", activebackground="#008800",
                       width=12, height=2, command=launch)
launch_btn.pack(side="left", padx=10)

stop_btn = tk.Button(btn_frame, text="STOP", font=("Arial", 14, "bold"),
                     bg="#660000", fg="white", activebackground="#880000",
                     width=12, height=2, command=stop, state="disabled")
stop_btn.pack(side="left", padx=10)

# Status & kill note
tk.Label(root, text="F6 = INSTANT KILL (global hotkey)", font=("Arial", 10, "bold"),
         fg="#ff5555", bg="#0d0d0d").pack(pady=(0, 10))

status_label = tk.Label(root, text="Ready", font=("Arial", 11),
                        fg="#cccccc", bg="#0d0d0d")
status_label.pack(pady=10)

close_btn = tk.Button(root, text="× CLOSE", font=("Arial", 10),
                      bg="#222222", fg="#dddddd", activebackground="#444444",
                      command=on_close)
close_btn.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()

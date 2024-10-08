import threading
import time
from tkinter import ttk

import cv2
from PIL import Image, ImageTk
from queue import Queue, Empty
import tkinter as tk



class VideoPlayerGUI:
    def __init__(self, root, synchronizer):
        self.root = root
        self.synchronizer = synchronizer
        self.labels = []
        self.images = []
        self.frame_queue = Queue()
        self.running = True

        for i in range(len(self.synchronizer.video_streams)):
            frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
            frame.grid(row=0, column=i, padx=5, pady=5)
            label = tk.Label(frame)
            label.pack()
            self.labels.append(label)

        control_frame = tk.Frame(root)
        control_frame.grid(row=1, column=0, columnspan=len(self.synchronizer.video_streams), pady=10)
        tk.Label(control_frame, text="Скорость:").pack(side=tk.LEFT, padx=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_options = [0.2, 1.0, 2.0, 5.0, 10.0]
        self.speed_menu = ttk.Combobox(control_frame, values=speed_options, textvariable=self.speed_var, state="readonly", width=5)
        self.speed_menu.pack(side=tk.LEFT)
        self.speed_menu.bind("<<ComboboxSelected>>", self.change_speed)

        self.play_button = tk.Button(control_frame, text="Play", command=self.play)
        self.play_button.pack(side=tk.LEFT, padx=5)
        self.pause_button = tk.Button(control_frame, text="Pause", command=self.pause)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(control_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.update_thread = threading.Thread(target=self.update_video_thread, daemon=True)
        self.update_thread.start()

        self.periodic_check()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def change_speed(self, event):
        speed = self.speed_var.get()
        self.synchronizer.set_speed(speed)

    def play(self):
        self.synchronizer.start()

    def pause(self):
        self.synchronizer.stop()

    def reset(self):
        self.synchronizer.reset()

    def update_video_thread(self):
        while self.running:
            if self.synchronizer.running and not self.synchronizer.pause_event.is_set():
                frames = self.synchronizer.get_synced_frames()
                for i, (frame, timestamp, stream) in enumerate(frames):
                    if frame is not None:

                        frame_number_text = f"Frame: {stream.frame_count}"
                        cv2.putText(frame, frame_number_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (255, 255, 0), 2, cv2.LINE_AA)


                        if stream.frame_count in stream.shown_frames:
                            cv2.putText(frame, "OLD FRAME", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                                        1, (0, 0, 255), 2, cv2.LINE_AA)
                        else:
                            stream.shown_frames.add(stream.frame_count)

                        # Изменение размера кадра для отображения
                        desired_size = (450, 350)
                        frame_resized = cv2.resize(frame, desired_size)

                        img = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
                        imgtk = ImageTk.PhotoImage(image=img)

                        self.frame_queue.put((i, imgtk))
                    else:
                        self.frame_queue.put((i, None))

                with self.synchronizer.lock:
                    frame_interval = self.synchronizer.frame_interval

                time.sleep(frame_interval)
            else:
                time.sleep(0.1)

    def periodic_check(self):
        try:
            while True:
                i, imgtk = self.frame_queue.get_nowait()
                if imgtk is not None:
                    self.labels[i].imgtk = imgtk
                    self.labels[i].configure(image=imgtk)
                else:
                    self.labels[i].configure(image='')
        except Empty:
            pass
        finally:
            self.root.after(100, self.periodic_check)

    def on_close(self):
        self.running = False
        self.synchronizer.stop()
        for stream in self.synchronizer.video_streams:
            stream.release()
        self.root.destroy()
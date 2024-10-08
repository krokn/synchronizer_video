import threading
import time

import cv2


class VideoSynchronizer:
    def __init__(self, video_streams, base_frame_rate=5):
        self.video_streams = video_streams
        self.base_frame_rate = base_frame_rate
        self.speed = 1.0
        self.frame_interval = 1.0 / (self.base_frame_rate * self.speed)
        self.start_time = None
        self.running = False
        self.pause_event = threading.Event()
        self.reset_event = threading.Event()
        self.lock = threading.Lock()

    def set_speed(self, speed):
        with self.lock:
            self.speed = speed
            self.frame_interval = 1.0 / (self.base_frame_rate * self.speed)

    def start(self):
        if not self.running:
            with self.lock:
                self.start_time = time.time()
                self.running = True
                self.pause_event.clear()
                self.reset_event.clear()

    def stop(self):
        if self.running:
            with self.lock:
                self.running = False
                self.pause_event.set()

    def reset(self):
        with self.lock:
            self.start_time = time.time()
            self.running = True
            self.pause_event.clear()
            self.reset_event.set()
            for stream in self.video_streams:
                stream.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                stream.current_index = 0
                stream.last_frame = None
                stream.last_timestamp = 0.0
                stream.frame_count = 0
                stream.shown_frames.clear()

    def get_synced_frames(self):

        with self.lock:
            if self.start_time is None:
                self.start()

            current_time = (time.time() - self.start_time) * self.speed

        frames = []
        for stream in self.video_streams:
            frame = stream.get_frame_at_time(current_time)
            frames.append((frame, stream.last_timestamp, stream))
        return frames
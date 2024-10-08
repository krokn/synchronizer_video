import cv2


class VideoStream:
    def __init__(self, video_path, annotations, stream_id):
        self.stream_id = stream_id
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Не удалось открыть видеофайл: {video_path}")
        self.annotations = annotations
        self.current_index = 0
        self.total_frames = len(self.annotations)
        self.last_frame = None
        self.last_timestamp = 0.0
        self.frame_count = 0
        self.shown_frames = set()

    def get_frame_at_time(self, current_time):

        while self.current_index < self.total_frames and self.annotations[self.current_index] <= current_time:
            ret, frame = self.cap.read()
            if not ret:
                break
            self.last_frame = frame
            self.last_timestamp = self.annotations[self.current_index]
            self.current_index += 1
            self.frame_count += 1

        if self.last_frame is not None:
            return self.last_frame.copy()
        else:
            return None

    def release(self):
        self.cap.release()
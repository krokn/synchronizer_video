import tkinter as tk
import os

from GUI import VideoPlayerGUI
from stream import VideoStream
from synchronizer import VideoSynchronizer


def read_annotations(file_path):
    with open(file_path, 'r') as file:
        timestamps = [float(line.strip()) for line in file.readlines()]
    return timestamps



def main():
    VIDEO_DIR = "videos"
    ANNOTATION_DIR = "annotations"

    video_filenames = ["1.avi", "2.avi", "3.avi", "4.avi"]
    annotation_filenames = ["1.txt", "2.txt", "3.txt", "4.txt"]

    video_paths = [os.path.join(VIDEO_DIR, vf) for vf in video_filenames]
    annotation_paths = [os.path.join(ANNOTATION_DIR, af) for af in annotation_filenames]

    # Проверка существования файлов
    for vp, ap in zip(video_paths, annotation_paths):
        if not os.path.exists(vp):
            raise FileNotFoundError(f"Видеофайл не найден: {vp}")
        if not os.path.exists(ap):
            raise FileNotFoundError(f"Файл аннотаций не найден: {ap}")

    all_annotations = []
    for ap in annotation_paths:
        annotations = read_annotations(ap)
        all_annotations.append(annotations)

    for i, ann in enumerate(all_annotations):
        if not ann:
            raise ValueError(f"Аннотация файла {annotation_filenames[i]} пуста.")

    min_timestamp = min([ann[0] for ann in all_annotations if len(ann) > 0])

    relative_annotations = []
    for ann in all_annotations:
        relative_ann = [timestamp - min_timestamp for timestamp in ann]
        relative_annotations.append(relative_ann)

    try:
        streams = [VideoStream(v, a, stream_id=i + 1) for i, (v, a) in
                   enumerate(zip(video_paths, relative_annotations))]
    except ValueError as e:
        return

    synchronizer = VideoSynchronizer(streams)

    root = tk.Tk()
    root.title("Синхронный проигрыватель AVI видео")
    player = VideoPlayerGUI(root, synchronizer)
    root.mainloop()

if __name__ == "__main__":
    main()

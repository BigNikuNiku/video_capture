import os
import cv2
import json
from enum import Enum
from datetime import timedelta


def seconds_to_hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    
    return f"{h:02d}_{m:02d}_{s:02d}"

class CaptureOption(Enum):
    Invalid = 0
    Before = 1
    Center= 2
    After = 3

class ConfigBase:
    def __init__(self, path):
        with open(path, encoding='UTF-8') as f:
            self.json_data = json.load(f)

    def input_file_full_path(self):
        return self.json_data['input']['file_full_path']

    def highlight_key_time_list(self):
        return self.json_data['highlights']['key_time_list']

    def highlight_capture_option(self):
        option = self.json_data['highlights']['capture_option']
        if 'Before' == option:
            return CaptureOption.Before
        elif 'Center' == option:
            return CaptureOption.Center
        elif 'After' == option:
            return CaptureOption.After
        else:
            # return Before as the default option
            return CaptureOption.Before

    def highlight_time_in_seconds(self):
        return self.json_data['highlights']['capture_time_in_seconds']

    def output_file_directory(self):
        return self.json_data['output']['file_directory']

    def output_file_prefix(self):
        return self.json_data['output']['file_prefix']


def main() :
    config = ConfigBase('./config.json')
    capture_option = config.highlight_capture_option()
    key_time_list = config.highlight_key_time_list()
    video_file_path = config.input_file_full_path()
    start_frame_id_list = []
    start_time_list = []

    cap = cv2.VideoCapture(video_file_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    resolution_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    resoulition_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    for time in key_time_list:
        hours, minutes, seconds = map(int, time.split(':'))
        total_seconds = int(timedelta(hours = hours, minutes = minutes, seconds = seconds).total_seconds())
        if CaptureOption.Before == capture_option:
            start_time = total_seconds - config.highlight_time_in_seconds()
            start_frame = (total_seconds - config.highlight_time_in_seconds()) * fps
        elif CaptureOption.Center == capture_option:
            start_time = total_seconds - config.highlight_time_in_seconds() / 2
            start_frame = (total_seconds - config.highlight_time_in_seconds() / 2) * fps
        elif CaptureOption.After == capture_option:
            start_time = total_seconds
            start_frame = total_seconds * fps
        start_frame_id_list.append(start_frame)
        start_time_list.append(seconds_to_hms(start_time))

    capture_frame_count = config.highlight_time_in_seconds() * fps
    output_file_suffix = 0
    capture_file_id = 0

    while capture_file_id < len(start_frame_id_list):
        frame_id = start_frame_id_list[capture_file_id]
        output_file_suffix = start_time_list[capture_file_id]
        output_frames = 0
        output_file_path = os.path.join(config.output_file_directory(), f'{config.output_file_prefix()}_{output_file_suffix}.mp4')
        out = cv2.VideoWriter(output_file_path, fourcc, fps, (resolution_width, resoulition_height))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        print(f'Capture started. start_frame = {frame_id}, capture_frame_count = {capture_frame_count}')
        while output_frames <= capture_frame_count:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            output_frames += 1
        print(f'Capture finished. video_name = {output_file_path}')
        out.release()
        capture_file_id += 1

    cap.release()
    cv2.destroyAllWindows()

    print('Done')


if __name__== "__main__" :
    main()
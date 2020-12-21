import json

from src.music_base import MusicBase, Frame
from src.music_info import HandSwitch

class MusicJson(MusicBase):
    def __init__(self, music_id, music_name, music_path, zone_id='', note_num=0, frame_num=0, count_zone_notes=0, min_pitch=0, max_pitch=127, hand=HandSwitch.BOTH_HAND, frame_length_in_ms=32, onset_thres=0.5):
        super(MusicJson, self).__init__(music_id, music_name, music_path, zone_id, note_num, frame_num, count_zone_notes, min_pitch, max_pitch, hand)
        self.frame_length_in_ms = frame_length_in_ms
        self.onset_thres = onset_thres

    def construct_frames(self):
        hand_int = self.hand
        framenum2pitches = {}
        with open(self.music_path, 'r') as fp:
            json_data = json.load(fp)
        for note in json_data['notes']:
            if float(note['confidence']) < self.onset_thres:
                continue
            frame_num = int(note['start_time']) / self.frame_length_in_ms
            if frame_num not in framenum2pitches.keys():
                framenum2pitches[frame_num] = []
            framenum2pitches[frame_num].append(int(note['pitch']))
        frame_vector = []
        for key in sorted(framenum2pitches.keys()):
            frame_vector.append(framenum2pitches[key])
        for pitches in frame_vector:
            pitches = list(set(pitches))
            pitches.sort()
            frame = Frame(self.frame_num)
            for pitch in pitches:
                if pitch > 127:
                    continue
                if pitch < self.min_pitch or pitch > self.max_pitch:
                    continue
                frame.noteVec.append(pitch)
            if len(frame.noteVec) > 0:
                self.frames.append(frame)
                self.frame_num += 1


if __name__ == '__main__':
    f = MusicJson(1, '05 op.10 nr5', '/Users/yang/Desktop/CCFAI2021/dataset/test.json')
    f.construct_frames()
    print(f.frame_num)
    for i, frame in enumerate(f.frames):
        print("=============>Frame {}<============".format(str(i)))
        print(frame)
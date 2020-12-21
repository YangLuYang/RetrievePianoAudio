from mido import MidiFile
from src.music_base import MusicBase, Frame

class MusicFile(MusicBase):
    def construct_frames(self):
        midi_data = MidiFile(self.music_path)
        tick = 0
        tickCurr = -1
        frame = None
        # mido automaticllly merged tracks
        for msg in midi_data:
            # only record note_on
            if msg.type != 'note_on':
                continue
            tick = msg.time
            # 一帧中的note的tick是相同的
            if tick > tickCurr:
                # new frame comes
                tickCurr = tick
                if frame is not None and len(frame.noteVec) > 0:
                    self.frames.append(frame)
                    self.frame_num += 1
                frame = Frame(self.frame_num)
            # filter invalid pitch
            note = msg.note
            if note > 127:
                print('invalid pitch')
                return False
            if note < self.min_pitch or note > self.max_pitch:
                continue
            # filter duplicate note
            if note in frame.noteVec:
                continue
            frame.noteVec.append(note)





if __name__ == '__main__':
    f = MusicFile(1, '05 op.10 nr5', '/Users/yang/Desktop/CCFAI2021/dataset/test.mid')
    f.construct_frames()
    print(f.frame_num)
    for i, frame in enumerate(f.frames):
        print("=============>Frame {}<============".format(str(i)))
        print(frame)

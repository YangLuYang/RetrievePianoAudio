from enum import Enum

class MusicType(Enum):
    JSON = 0
    MIDI = 1

class HandSwitch(Enum):
    UNKNOWN_HAND = -1
    BOTH_HAND = 0
    LEFT_HAND = 1
    RIGHT_HAND = 2

class MusicInfo():
    def __init__(self, music_id, music_name, music_path, hand=HandSwitch.BOTH_HAND, has_abc=True, note_num=0, sum_zone_num=0, match_zone_num=0, time_coherence=0):
        self.music_id = music_id
        self.music_name = music_name
        self.music_path = music_path
        self.hand = hand
        self.has_abc = has_abc
        self.note_num = note_num
        self.sum_zone_num = sum_zone_num
        self.match_zone_num = match_zone_num
        self.time_coherence = time_coherence
        self.matched = False

    def __lt__(self, other):
        if self.match_zone_num > other.match_zone_num:
            return True
        if self.match_zone_num == other.match_zone_num:
            return self.time_coherence > other.time_coherence
        return False

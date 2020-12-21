from abc import abstractmethod, ABC
from intbitset import intbitset
from music_info import HandSwitch


class MusicBase(ABC):
    def __init__(self, music_id, music_name, music_path, zone_id='', note_num=0, frame_num=0, count_zone_notes=0, min_pitch=0, max_pitch=127, hand=HandSwitch.BOTH_HAND):
        self.music_id = music_id
        self.music_name = music_name
        self.music_path = music_path
        self.zone_id = zone_id
        self.note_num = note_num
        self.frame_num = frame_num
        self.count_zone_notes = count_zone_notes   #number of zone anchors
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        self.hand = hand
        self.frames = []
        self.zones = []
        self.pairs = []
        self.notes = []
        self.frameNos = []

    @abstractmethod
    def construct_frames(self):
        pass

    def construct_target_zones(self):
        # sort notes in a specified order (from lefe to right in time, from bottom to up in pitch)
        for frame in self.frames:
            frame_notes = frame.noteVec
            frame_notes.sort()
            for note in frame_notes:
                self.notes.append(note)
                self.frameNos.append(frame.id)
                self.note_num += 1
        self.frames = []
        if len(self.notes) < self.count_zone_notes:
            return False

        for i in range(0, len(self.notes) - self.count_zone_notes + 1):
            zone = TargetZone(self.zone_id)
            self.zone_id += 1
            zone.note = self.notes[i]
            zone.frame_num = self.frameNos[i]
            # default zone anchor is first note
            for j in range(1, self.count_zone_notes):
                zone.offsetNotes.append(self.notes[i + j] - self.notes[i])
                zone.offsetTimes.append(self.frameNos[i + j] - self.frameNos[i])
            self.zones.append(zone)

        # delete notes that had been anchors
        self.notes = self.notes[self.count_zone_notes:]
        self.frameNos = self.frameNos[self.count_zone_notes:]
        return True

    def construct_pair_of_zone(self, zone, zone_pairs):
        for i in range(len(zone.offsetNotes)):
            note = zone.note
            offsetNote = zone.offsetNotes[i]
            offsetTime = zone.offsetTime[i]
            pair = NotePair(note, offsetNote, offsetTime, zone.id, zone.frame_num)
            zone_pairs.append(pair)
        return True


class Frame():
    def __init__(self, id):
        self.id = id # frame id (tick number in mid track)
        self.noteVec = [] # pitches in the frame (0-128)

    def __repr__(self):
        return ",".join(str(note) for note in self.noteVec)

class TargetZone():
    def __init__(self, id):
        self.id = id
        self.note = '' # pitch of anchor note
        self.offsetNotes = [] # pitch delta between zone and anchor
        self.offsetTimes = [] # time delta between zone notes and anchor
        self.frame_num = 0

class NotePair():
    def __init__(self, note, offsetNote, offsetTime, idZone, zoneFrameNum):
        self.note = note
        self.offsetNote = offsetNote
        self.offsetTime = offsetTime
        self.idZone = idZone
        self.zoneFrameNum = zoneFrameNum
        self.id = offsetTime * 256 * 256 + note * 256 + (offsetNote + 127)

class IndexContent():
    def __init__(self, id_music_file, id_target_zone, zone_frame_num, logic_music_id):
        self.id_music_file = id_music_file
        self.id_target_zone = id_target_zone
        self.zone_frame_num = zone_frame_num
        self.logic_music_id = logic_music_id

class IndexContentArray():
    def __init__(self, id):
        self.id = id
        self.content_size = 0
        self.indexContents = {}
        self.musicid2index = {}
        self.index2musicid = {}
        self.music_bitset = intbitset()
        self.zone_bitsets = {}

    def build_music_bitmap(self, sum_music_num):
        self.music_bitset = intbitset(rhs=sum_music_num)
        for value in self.musicid2index.values():
            self.music_bitset[value] = 1
        return True

    def build_music_zone_bitmap(self, logic_music_id, sum_zone_num):
        zone_bitmap = intbitset(rhs=sum_zone_num)
        for value in self.indexContents[logic_music_id].values():
            zone_bitmap[value.idTargetZone] = 1
        self.zone_bitsets[logic_music_id] = zone_bitmap
        return True

    def add_index_content(self, music_index, content):
        logic_musicid = content.logic_music_id
        if logic_musicid in self.indexContents.keys():
            self.indexContents[logic_musicid][content.id_target_zone] = content
        else:
            self.musicid2index[logic_musicid] = music_index
            self.index2musicid[music_index] = logic_musicid
        self.content_size += 1



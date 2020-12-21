from multiprocessing import Lock
from src.music_base import IndexContentArray, NotePair, IndexContent
from src.music_info import MusicType
from src.music_file import MusicFile
from src.music_json import MusicJson

class IVIndex():
    def __init__(self, count_zone_notes, min_pitch, max_pitch, zones_per_logic_music, overlap_zones,
                 frame_length_in_ms=32, onset_thres=0.5, split_points=[]):
        self.count_zone_notes = count_zone_notes
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        self.zones_per_logic_music = zones_per_logic_music
        self.overlap_zones = overlap_zones
        self.frame_length_in_ms = frame_length_in_ms
        self.onset_thres = onset_thres
        self.split_points = split_points
        self.info_map = {}
        self.ivIndexes = []
        self.curr_music_index = 0
        self.sum_content_num = 0
        self.sum_zone_num = 0
        self.sum_logic_music = 0
        self.music_zones = {}
        self.pitch_range = 256
        self.valid_musics = 0
        self.index_mutex = Lock()
        self.info_mutex = Lock()

        for j in range(len(split_points) + 1):
            ivIndex = []
            for i in range(len(count_zone_notes * 256 * 256)):
                icArray = IndexContentArray(i)
                ivIndex.append(icArray)
            self.ivIndexes.append(ivIndex)


    def build_index(self, music_infos, music_type):
        self.valid_musics = len(music_infos)
        del_index = []
        print('add music to retrieval lib')
        for i in range(len(music_infos)):
            ret = False
            if music_type == MusicType.MIDI:
                music_file = MusicFile(music_infos[i].music_id, music_infos[i].music_name, music_infos[i].music_path,
                                       count_zone_notes=self.count_zone_notes, min_pitch=self.min_pitch, max_pitch=self.max_pitch)
                ret = self.add_new_music_to_lib(i, music_file)
                music_infos[i].note_num = music_file.note_num
            elif music_type == MusicType.JSON:
                music_json = MusicJson(music_infos[i].music_id, music_infos[i].music_name, music_infos[i].music_path,
                                       count_zone_notes=self.count_zone_notes, min_pitch=self.min_pitch, max_pitch=self.max_pitch,
                                       hand=music_infos[i].hand, frame_length_in_ms=self.frame_length_in_ms, onset_thres=self.onset_thres)
                ret = self.add_new_music_to_lib(i, music_json)
                music_infos[i].note_num = music_json.note_num
            if not ret:
                del_index.append(i)
                self.valid_musics -= 1
            self.info_map[music_infos[i].music_id] = music_infos[i]
        for index in del_index:
            music_infos.pop(index)
        # build bitmap
        print('build bit set for every index')
        music_size = len(music_infos)
        for ivIndex in self.ivIndexes:
            for content_array in ivIndex:
                content_array.build_music_bitmap(music_size)
                for key in content_array.musicid2index.keys():
                    content_array.build_music_zone_bitmap(key, self.music_zones[key])
        print('finish building bitset')

        print('sum retrieval lib: {}'.format(len(self.ivIndexes)))


    def add_new_music_to_lib(self, index, music):
        print('{}/{} hand:{} {}'.format(index, self.valid_musics, music.hand, music.music_path))
        if not music.construct_frames():
            print('Error when construct Frames')
            return False
        note_size = 0
        for frame in music.frames:
            note_size += len(frame.noteVec)
        print('frame: {} note: {}'.format(len(music.frames), note_size))
        if not music.construct_target_zones():
            print('Error when construct Zones, no enough notes')
            return False

        # find out which ivIndex this music should be add in, according to zone size
        zone_size = len(music.zones)
        lib_index = 0
        for i in range(len(self.split_points)):
            if zone_size <= self.split_points[i]:
                lib_index = i
                break
            lib_index += 1

        print('lib: {}'.format(lib_index))

        self.add_music_zone_to_lib(music, lib_index)

        return True

    def add_music_zone_to_lib(self, music, lib_index):
        logic_sequence_id = 0
        zone_id = 0
        zoneid_base = 0
        while zone_id < len(music.zones):
            logic_musicid = '{}_{}'.format(music.music_id, logic_sequence_id)
            for i in range(self.zones_per_logic_music):
                zone_id = zoneid_base + i
                if zone_id >= len(music.zones):
                    self.music_zones[logic_musicid] = len(music.zones)
                    break

                # push zone to index
                zone = music.zones[zone_id]
                zone_pairs = []
                music.construct_pair_of_zone(zone, zone_pairs)
                for pair in zone_pairs:
                    if pair.id > len(self.ivIndexes[lib_index]):
                        continue
                    content = IndexContent(music.music_id, pair.idZone, pair.zoneFrameNum, logic_musicid)
                    self.ivIndexes[lib_index][pair.id].add_index_content(self.curr_music_index, content)
                    self.sum_content_num += 1

            # musicid2zone
            self.music_zones[logic_musicid] = len(music.zones)
            zoneid_base = zone_id + 1

            # split
            if (zone_id + 1) * 1.0 / len(music.zones) < 0.7:
                logic_sequence_id += 1
                zoneid_base = zoneid_base - self.overlap_zones

        self.sum_logic_music += (logic_sequence_id + 1)
        self.curr_music_index += 1




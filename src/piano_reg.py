import yaml
import json
import MySQLdb
from src.inverted_index import IVIndex
from src.music_info import MusicInfo, MusicType

params = yaml.load('../global_params.yaml')
connection = MySQLdb.connect(host='localhost', port=3306, user='root', password='123456', database='Music', charset='utf8')
db = connection.cursor()

def main():
    # build retrieval lib
    lib_split_points = params['split_points']
    ivIndex = IVIndex(params['count_zone_notes'], params['min_pitch'], params['max_pitch'], params['zones_per_logic_music'],
                      params['overlap_zones'], float(1000) / params['frame_per_second'], params['onset_threshold'], lib_split_points)

    # read music info from database
    music_collections = []
    with connection:
        db.execute('select id, canonical_title, canonical_composer, split, audio_filename, midi_filename from musicinfo')
        for row in db.fetchall():
            music_collections.append(MusicInfo(row[0], row[1], row[5]))
    ivIndex.build_index(music_collections, MusicType.MIDI)

def importMetaData():
    path_to_json = '/data/disk4/dataset/piano/MAESTRO/raw/maestro-v1.0.0.json'
    with open(path_to_json, 'r') as fp:
        maestro_meta = json.load(fp.read())
    for obj in maestro_meta:
        insert_sql = "insert into musicinfo (canonical_title, canonical_composer, split, audio_filename, midi_filename) " \
                     "values ('{}', '{}', '{}', '{}', '{}', '{}');".format(obj['canonical_title'], obj['canonical_composer'], obj['split'],
                    obj['audio_filename'], obj['midi_filename'])
        with connection:
            db.execute(insert_sql)



if __name__ == '__main__':
    importMetaData()
    main()
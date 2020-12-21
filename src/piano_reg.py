import yaml
import json
import MySQLdb
from datetime import datetime
from inverted_index import IVIndex
from music_info import MusicInfo, MusicType

with open('/home/yangluyang/RetrievePianoAudio/global_params.yaml', 'r') as f:
    params = yaml.load(f.read())
connection = MySQLdb.connect(host=params['db_host'], port=params['db_port'], user=params['db_user'], password=params['db_passwd'], database='Music', charset='utf8')
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
        maestro_meta = json.loads(fp.read())
    with connection:
        delete_sql = "delete from musicinfo where 1=1;"
        db.execute(delete_sql)
        for obj in maestro_meta:
            if obj['split'] == 'train':
                split = 0
            elif obj['split'] == 'validation':
                split = 1
            elif obj['split'] == 'test':
                split = 2
            canonical_title = obj['canonical_title'].replace("'", "\'")
            canonical_composer = obj['canonical_composer'].replace("'", "\'")
            insert_sql = "insert into musicinfo (canonical_title, canonical_composer, split, year, duration,audio_filename, midi_filename, create_time) " \
                         "values ('{}', '{}', '{}', '{}', '{}', '{}', '{}, '{}');".format(canonical_title, canonical_composer, split,
                        int(obj['year']), int(obj['duration']), obj['audio_filename'], obj['midi_filename'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            db.execute(insert_sql)
            db.close()



if __name__ == '__main__':
    importMetaData()
    main()

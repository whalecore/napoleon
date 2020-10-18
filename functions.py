from pydub import AudioSegment
from google_images_search import GoogleImagesSearch

import random
import string
import os
import glob
import io


octaves = 0.5
gis = GoogleImagesSearch('AIzaSyCgtnY9D1Ai-OOa5ZJNiCoP5F1EiSq_4pU', '296ed5193c8ec3c4b')


def hi_pitch(sound):
    sound = AudioSegment.from_file(sound, format='ogg')
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
    hipitch_sound = sound._spawn(sound.raw_data, overrides={
        'frame_rate': new_sample_rate})
    hipitch_sound = hipitch_sound.set_frame_rate(44100)
    random_filename = ''.join(random.choice(
        string.ascii_lowercase) for i in range(8))
    hipitch_sound.export(random_filename + '.ogg', format='ogg')
    return random_filename + '.ogg'


def low_pitch(sound1):
    sound = AudioSegment.from_file(sound1, format='ogg')
    new_sample_rate = int(sound.frame_rate * (1.5 * octaves))
    hipitch_sound = sound._spawn(sound.raw_data, overrides={
        'frame_rate': new_sample_rate})
    hipitch_sound = hipitch_sound.set_frame_rate(44100)
    random_filename = ''.join(random.choice(
        string.ascii_lowercase) for i in range(8))
    hipitch_sound.export(random_filename + '.ogg', format='ogg')
    final_name = random_filename + '.ogg'
    return final_name


def remove_all_oggs():
    BASE_DIR = glob.glob(os.getcwd())
    for f in BASE_DIR:
        if f.endswith('.ogg'):
            os.remove(f)

def google_photo():
    _search_params = {
    'q': 'щенок',
    'num': 10,
    'safe': 'medium',
    'fileType': 'jpg',
    'imgType': 'photo',
    'imgSize': 'MEDIUM',
    'imgDominantColor': '',
    'rights': 'cc_publicdomain'
    }
    gis.search(search_params=_search_params)
    for image in gis.results():
        image.download('/home/whalecore/PyProjects/miha')
        image.resize(500, 500)

def low_pitch_new(zvuk):
    sound = AudioSegment.from_file(zvuk, format='ogg')
    print(sound.frame_rate)
    octaves = -0.5
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
    lowpitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    lowpitch_sound.export('testing.ogg', format='ogg')

def get_hi_pitch(sound):
    a = hi_pitch(sound)
    return a
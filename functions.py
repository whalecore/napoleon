from pydub import AudioSegment
import random
import string
import os
import glob

octaves = 0.5


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


def low_pitch(sound):
    sound = AudioSegment.from_file(sound, format='ogg')
    new_sample_rate = int(sound.frame_rate * (1.5 * octaves))
    hipitch_sound = sound._spawn(sound.raw_data, overrides={
        'frame_rate': new_sample_rate})
    hipitch_sound = hipitch_sound.set_frame_rate(44100)
    random_filename = ''.join(random.choice(
        string.ascii_lowercase) for i in range(8))
    hipitch_sound.export(random_filename + '.ogg', format='ogg')
    return random_filename + '.ogg'


def remove_all_oggs():
    BASE_DIR = glob.glob(os.getcwd())
    for f in BASE_DIR:
        if f.endswith('.ogg'):
            os.remove(f)

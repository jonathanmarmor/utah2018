#!/usr/bin/env python

import random

import numpy as np

from music_tools3 import Music
from utils import scale_weights, flatten


class Movement1(object):
    def __init__(self):
        self.pick_duration_and_bpm()

        self.music = Music(
            part_names=(
                'oboe',
                'bass_clarinet',
                'vibraphone',
                'bass',
            ),
            bpm=self.bpm,
            output_dir_name='experiment16',
            n_quarters=self.n_quarters
        )
        self.part_names = self.music.part_names
        self.instruments = self.music.instruments
        self.layers = self.music.layers

        self.ob = self.music.oboe
        self.cl = self.music.bass_clarinet
        self.vib = self.music.vibraphone
        self.bass = self.music.bass

        self.make_music()

        self.music.closeout()
        self.music.notate()

    def pick_duration_and_bpm(self):
        min_seconds = 135
        max_seconds = 160
        target_duration_seconds = random.randint(min_seconds, max_seconds + 1)
        # target_duration_seconds = 140

        min_bpm = 90
        max_bpm = 125
        self.bpm = random.randint(min_bpm, max_bpm + 1)
        # self.bpm = 110

        self.quarter_duration_seconds = 60.0 / self.bpm
        self.bar_duration_seconds = self.quarter_duration_seconds * 4

        self.n_bars = int(target_duration_seconds / self.bar_duration_seconds)
        self.n_quarters = self.n_bars * 4

        self.duration_seconds = self.bar_duration_seconds * self.n_bars
        self.duration_quarters = float(self.n_quarters)

    def put_fragment(self, fragment, instrument, offset):
        for pitch, duration in fragment:
            instrument.put_note(offset, duration, pitch)
            offset += duration

    # def propose_fragment(self, fragment, instrument, offset):

    def make_music(self):
        for instrument in self.instruments:
            failures = 0
            for _ in range(1000):
                duration = random.choice(np.linspace(.25, 2.0, 8))
                openings = instrument.find_openings(duration)
                if openings:
                    offset = random.choice(openings)
                    instrument.put_note(offset, duration, pitch=random.choice(flatten(instrument.registers[-4:-1])))
                else:
                    failures += 1
                    if failures > 10:
                        break

        # for sixteenth in self.layers.sixteenths:
        #     if random.random() < .6:
        #         self.ob.put_note(sixteenth.offset, .25, 77)

        # for note in self.ob.get(12, 5):
        #     print note




        # self.make_form()

        # self.make_intro()
        # self.make_first_wedge()

        # # sixteenths = self.layers.sixteenths
        # self.layers.add_layer('rhythm', [3, 3, 2] * self.layers.n_halves)

        # # weight_options = scale_weights([6 ** x for x in range(1, 7)])
        # # weights = [random.choice(weight_options) for _ in range(8)]
        # # print weights

        # pitches = {
        #     'oboe': 79,
        #     'bass_clarinet': 70,
        #     'vibraphone': [60, 67],
        #     'bass': 48,
        # }

        # notes = []
        # for beat in self.layers.rhythm:
        #     # weight = weights[sixteenth.index % len(weights)]
        #     for instrument in [vibes]:  #, bass_clarinet, vibes, bass]:
        #         instrument.put_note(beat.offset, beat.duration, pitches[instrument.part_name])

        #         # if random.random() > weight:
        #         #     instrument.put_note(sixteenth.offset, .25, pitches[instrument.part_name])
        #         # else:
        #         #     instrument.put_note(sixteenth.offset, .25, None)

    # def make_form(self):
    #     section_durations = [
    #         3,
    #         4,
    #         4,
    #         4,
    #         4,
    #         1,
    #         8,
    #         4,
    #         4,
    #         1,
    #         8,
    #         8,
    #         8,
    #         3,
    #     ]
    #     section_names = [
    #         'intro',
    #         'verseA',
    #         'verseB',
    #         'verseA',
    #         'verseB',
    #         'transition',
    #         'chorus',
    #         'verseA',
    #         'verseB',
    #         'transition',
    #         'chorus',
    #         'bridge',
    #         'chorus',
    #         'outro',
    #     ]
    #     self.layers.add_layer('top_level_form', section_durations)
    #     for section, name in zip(self.layers.top_level_form, section_names):
    #         section.name = name



    # def make_first_wedge(self):
    #     self.layers.add_layer('rhythm', [3, 3, 2] * self.layers.n_halves)


def utah2018():
    m1 = Movement1()


if __name__ == '__main__':
    utah2018()

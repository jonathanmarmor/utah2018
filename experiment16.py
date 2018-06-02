#!/usr/bin/env python

import random
import collections
import argparse

import numpy as np

from music_tools3 import Music
from sections2 import Layers
import utils


class Movement1(object):
    def __init__(self):
        self.part_names = (
            'oboe',
            'bass_clarinet',
            'vibraphone',
            'bass',
        )

        self.pick_duration_and_bpm()

        m = self.music = Music(
            part_names=self.part_names,
            starting_tempo_bpm=self.bpm,
            output_dir_name='experiment16',
            n_quarters=self.n_quarters,
            ticks_per_quarter=self.ticks_per_quarter,
        )

        self.make_music()

        for i in self.music.instruments:
            i.closeout()

        print 'Done making the music. Starting notation.'

    def pick_duration_and_bpm(self):
        min_seconds = 8  # 135
        max_seconds = 16  # 160
        target_duration_seconds = random.randint(min_seconds, max_seconds + 1)

        min_bpm = 90
        max_bpm = 125
        self.bpm = random.randint(min_bpm, max_bpm + 1)

        self.quarter_duration_seconds = 60.0 / self.bpm
        self.bar_duration_seconds = self.quarter_duration_seconds * 4

        self.n_bars = int(target_duration_seconds / self.bar_duration_seconds)
        self.n_quarters = self.n_bars * 4

        self.duration_seconds = self.bar_duration_seconds * self.n_bars
        self.duration_quarters = float(self.n_quarters)

        self.ticks_per_quarter = 32
        self.n_ticks = self.n_quarters * self.ticks_per_quarter

        self.layers = Layers(self.n_quarters, self.ticks_per_quarter, self.bpm)

    def put_fragment(self, fragment, instrument, offset):
        for pitch, duration in fragment:
            instrument.put_note(offset, duration, pitch)
            offset += duration

    def make_music(self):
        oboe = self.music.oboe
        bass_clarinet = self.music.bass_clarinet
        vibes = self.music.vibraphone
        bass = self.music.bass

        sixteenths = self.layers['sixteenths']

        weight_options = utils.scale_weights([6 ** x for x in range(1, 7)])
        weights = [random.choice(weight_options) for _ in range(8)]
        print weights

        pitches = {
            'oboe': 79,
            'bass_clarinet': 70,
            'vibraphone': [60, 67],
            'bass': 48,
        }

        notes = []
        offset = 0
        for sixteenth in sixteenths:
            weight = weights[sixteenth.index % len(weights)]
            for instrument in [vibes]:  #, bass_clarinet, vibes, bass]:
                if random.random() > weight:
                    instrument.put_note(offset, .25, pitches[instrument.part_name])
                else:
                    instrument.put_note(offset, .25, None)
            offset += .25

    def notate(self):
        self.music.notate()


def utah2018():
    m1 = Movement1()
    m1.notate()


if __name__ == '__main__':
    utah2018()

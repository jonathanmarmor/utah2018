#!/usr/bin/env python

import random
import collections
import argparse

import numpy as np

from music_tools2 import Music
from duration import Duration


duration_tools = Duration(ticks=24)


def find_closest_scale_members(pitch, scale):
    scale = [p for p in range(36, 96) if p % 12 in scale]

    diffs = collections.defaultdict(list)
    for scale_member in scale:
        diff = np.abs(scale_member - pitch)
        diffs[diff].append(scale_member)

    return diffs[min(diffs)]


def transpose(lick, n):
    return [(p + n, d) for p, d in lick]


def put_in_scale(lick, scale):
    result = []
    for p, d in lick:
        if p % 12 not in scale:
            closest_scale_members = find_closest_scale_members(p, scale)
            p = random.choice(closest_scale_members)
        result.append((p, d))
    return result


def put_in_register(lick, register):
    pitches = [p for p, d in lick]
    durations = [d for p, d in lick]
    top_of_register = max(register)
    bottom_of_register = min(register)

    while not all([p in register for p in pitches]):
        if max(pitches) > top_of_register:
            pitches = [p - 12 for p in pitches]
        elif min(pitches) < bottom_of_register:
            pitches = [p + 12 for p in pitches]

    return zip(pitches, durations)


def get_random_scale():
    root = random.randint(0, 11)
    scale_type = random.choice([
        [0, 2, 4, 5, 7, 9, 11],
        # [0, 1, 4, 6, 7, 8, 11],
        # [0, 2, 4, 7, 9],
        # [0, 2, 4, 6, 8, 10],
    ])
    scale = [(p + root) % 12 for p in scale_type]
    scale.sort()
    return scale


class Lick(list):
    def __init__(self):
        self.make()

    def make(self):
        rhythm = []
        for length in [1, 1]:
            rhythm.extend(self.make_rhythmic_figure(length))
        rhythm.append(2)

        self.duration_quarters = 4
        self.duration_sixteenths = 0

        register = range(60, 85)

        pitch = random.choice(register)
        for duration in rhythm:

            lowest = max([pitch - 3, register[0]])
            highest = min([pitch + 3, register[-1]])
            pitch_options = [p for p in register if lowest <= p <= highest and p is not pitch]
            pitch = random.choice(pitch_options)

            self.append((pitch, duration))

    def make_rhythmic_figure(self, duration_in_quarters=4):
        remaining_duration = duration_in_quarters
        rhythm = []
        while remaining_duration:
            duration_options = np.linspace(.25, remaining_duration, remaining_duration * 4)
            duration = random.choice(duration_options)
            rhythm.append(duration)
            remaining_duration -= duration
        return rhythm

    def pitches(self):
        return [p for p, d in self]

    def intervals(self):
        return [b[0] - a[0] for a, b in pairwise(self)]


class NoMoreOpenings(Exception):
    pass


class Movement1(object):
    def __init__(self):

        self.part_names = (
            'oboe',
            'bass_clarinet',
            'vibraphone',
            'bass'
        )
        self.starting_tempo_bpm = starting_tempo_bpm = 105
        self.output_dir_parent = 'output'
        self.output_dir_name = 'experiment10'
        self.n_quarters = 128
        self.ticks_per_quarter = 24

        m = self.music = Music(
            part_names=self.part_names,
            starting_tempo_bpm=self.starting_tempo_bpm,
            output_dir_parent=self.output_dir_parent,
            output_dir_name=self.output_dir_name,
            n_quarters=self.n_quarters,
            ticks_per_quarter=self.ticks_per_quarter,
        )

        self.scale = get_random_scale()

        self.licks = []
        for _ in range(2):
            self.licks.append(Lick())


        # openings_remaining = {}
        # for instrument in self.part_names:
        #     openings_remaining[instrument] = True

        openings_remaining = True
        # while any(openings_remaining.values()):
        while openings_remaining:
            instrument = random.choice(self.music.instruments)
            try:
                self.put_lick(self.licks[0], instrument)
            except NoMoreOpenings:
                # openings_remaining[instrument] = False
                openings_remaining = False

        for i in self.music.instruments:
            i.closeout()

        print 'Done making the music. Starting notation.'


    def put_lick(self, lick, instrument):
        # instrument = random.choice(self.music.instruments)

        openings = instrument.timeline.find_openings(
            length_quarters=lick.duration_quarters,
            length_sixteenths=lick.duration_sixteenths
        )
        if not openings:
            raise NoMoreOpenings()


        # Find openings that start on the quarternote
        openings = [o for o in openings if o[1] == 0]
        if openings:
            start_quarter, start_sixteenth, length_quarter, length_sixteenth = random.choice(openings)
        else:
            return

        start_offset = duration_tools.quarters_and_sixteenths_to_ticks(quarters=start_quarter, sixteenths=start_sixteenth)

        duration = duration_tools.quarters_and_sixteenths_to_ticks(quarters=length_quarter, sixteenths=length_sixteenth)

        lick = transpose(lick, random.randint(1, 11))
        lick = put_in_scale(lick, self.scale)
        lick = put_in_register(lick, instrument.safe_register)

        for pitch, dur in lick:
            duration_in_ticks = int(dur * self.ticks_per_quarter)
            instrument.put_note(start_offset, duration_in_ticks, pitch=pitch)
            start_offset += duration_in_ticks

    def notate(self):
        self.music.notate()


def command_line_interface():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--dont-notate',
        help='dont generate notation',
        action="store_true")
    return parser.parse_args()


if __name__ == '__main__':
    args = command_line_interface()

    m1 = Movement1()
    if not args.dont_notate:
        m1.notate()

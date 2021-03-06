#!/usr/bin/env python

import random
import collections
import argparse

import numpy as np

from music_tools import Music


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
        for length in [1, 2, 1]:
            rhythm.extend(self.make_rhythmic_figure(length))
        rhythm.append(2)

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


class Movement1(object):
    def __init__(self):
        m = self.music = Music(
            part_names=(
                'oboe',
                'clarinet',
                'vibraphone',
                'bass'
            ),
            starting_tempo_bpm=105,
            output_dir_parent='output',
            output_dir_name='experiment9',
        )

        self.scale = get_random_scale()

        for _ in range(5):
            self.make_it(20)

    def make_it(self, n=100):
        self.lick = Lick()

        for _ in range(n):
            instrument = random.choice(self.music.instruments)

            lick = transpose(self.lick, random.randint(1, 11))
            lick = put_in_scale(lick, self.scale)
            lick = put_in_register(lick, instrument.safe_register)

            rest_before = random.choice([0, 0, 1, 1, 1, 2, 2, 2, 3, 4])
            rest_after = random.choice([0, 0, 1, 1, 1, 2, 2, 2, 3, 4])

            if rest_before:
                instrument.add_note(pitch='rest', duration=rest_before)

            for p, d in lick:
                instrument.add_note(pitch=p, duration=d)

            if rest_after:
                instrument.add_note(pitch='rest', duration=rest_after)

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

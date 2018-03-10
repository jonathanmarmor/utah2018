#!/usr/bin/env python

import random
import collections
import argparse

import numpy as np

from music_tools2 import Music


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


class Timeline(object):
    def __init__(self,
            n_quarters=64,
            ticks_per_quarter=24,
        ):
        self.ticks_per_quarter = ticks_per_quarter
        self.ticks_per_sixteenth = ticks_per_quarter / 4
        self.n_quarters = n_quarters
        self.n_sixteenths = n_quarters * 4
        self.n_ticks = ticks_per_quarter * n_quarters

        self._timeline = np.zeros([n_ticks], dtype=bool)

    def __len__(self):
        return self._timeline.shape[0]

    def to_ticks(self, length_quarters, length_sixteenths):
        return (length_quarters * self.ticks_per_quarter) + (length_sixteenths * self.ticks_per_sixteenth)

    def ticks_to_quarters_and_sixteenths(self, ticks):
        quarters, remainder = divmod(ticks, self.ticks_per_quarter)
        sixteenths, remaining_ticks = divmod(remainder, self.ticks_per_sixteenth)
        return quarters, sixteenths, remaining_ticks

    def get(self, quarter, sixteenth=0, length_quarters=1, length_sixteenths=0):
        start = self.to_ticks(quarter, sixteenth)
        length = self.to_ticks(length_quarters, length_sixteenths)
        end = start + length
        return self._timeline[start:end]

    def fill(self, quarter, sixteenth=0, length_quarters=1, length_sixteenths=0):
        chunk = self.get(quarter, sixteenth=sixteenth, length_quarters=length_quarters, length_sixteenths=length_sixteenths)
        chunk.fill(True)

    def check_if_clear(self, quarter, sixteenth=0, length_quarters=1, length_sixteenths=0):
        chunk = self.get(quarter, sixteenth=sixteenth, length_quarters=length_quarters, length_sixteenths=length_sixteenths)
        return chunk.any() == False

    def find_openings(self, length_quarters=1, length_sixteenths=0):
        openings = []
        n_starts = self.n_sixteenths - (length_quarters * 4) - length_sixteenths + 1
        for sixteenth in range(n_starts):
            quarter, sixteenth = divmod(sixteenth, 4)
            clear = self.check_if_clear(quarter, sixteenth, length_quarters, length_sixteenths)
            if clear:
                openings.append((quarter, sixteenth, length_quarters, length_sixteenths))
                # chunk = self.get(quarter, sixteenth, length_quarters, length_sixteenths)
                # openings.append(chunk)
        return openings


class Lick(list):
    def __init__(self):
        self.make()

    def make(self):
        rhythm = []
        for length in [1, 2, 1]:
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
            output_dir_name='experiment10',
        )

        n_quarters = 128
        self.timeline = {}
        for i in part_names:
            self.timeline[i] = Timeline(n_quarters=n_quarters)

        self.scale = get_random_scale()
        self.lick = Lick()


    def put_lick(self):
        instrument = random.choice(self.music.instruments)

        timeline = self.timeline[instrument.part_name]

        openings = timeline.find_openings(
            length_quarters=self.lick.duration_quarters,
            length_sixteenths=self.lick.duration_sixteenths
        )

        start_quarter, start_sixteenth, length_quarter, length_sixteenth = random.choice(openings)

        timeline.fill(start_quarter, start_sixteenth, length_quarter, length_sixteenth)




        lick = transpose(self.lick, random.randint(1, 11))
        lick = put_in_scale(lick, self.scale)
        lick = put_in_register(lick, instrument.safe_register)

        # rest_before = random.choice([0, 0, 1, 1, 1, 2, 2, 2, 3, 4])
        # rest_after = random.choice([0, 0, 1, 1, 1, 2, 2, 2, 3, 4])

        # if rest_before:
        #     instrument.add_note(pitch='rest', duration=rest_before)

        # for p, d in lick:
        #     instrument.add_note(pitch=p, duration=d)

        # if rest_after:
        #     instrument.add_note(pitch='rest', duration=rest_after)


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

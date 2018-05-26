#!/usr/bin/env python

import random
import collections
import argparse

import numpy as np

from music_tools2 import Music
from duration import Duration


def weighted_choice(indexes, weights):
    # Make weights sum to 1.0
    weights /= weights.sum()

    # Weighted choice
    index = np.random.choice(indexes, p=weights)

    return index, weights


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
            # If the highest pitch is out of range, lower the whole lick by an octave
            pitches = [p - 12 for p in pitches]
        elif min(pitches) < bottom_of_register:
            # If the lowest pitch is out of range, raise the whole lick by an octave
            pitches = [p + 12 for p in pitches]

    return zip(pitches, durations)


class Lick(list):
    def __init__(self):
        self.make()

    def make(self):
        rhythm = []
        for length in [1, 1]:
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

        self.duration = 0
        for p, d in self:
            self.duration += d

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


class Sequence(list):
    def __init__(self, lick, instrument, repetitions=3):
        self.lick = lick

        self.interval = random.choice([0, 1, -1, 2, -2, 5, -5, 7, -7])
        self.gap_duration = random.choice([0, 2, 4])

        for repetition in range(repetitions):
            transposition = self.interval * repetition

            lick = transpose(lick, transposition)
            # lick = put_in_scale(lick, self.scale)
            lick = put_in_register(lick, instrument.safe_register)

            for p, d in lick:
                self.append((p, d))
            if self.gap_duration:
                self.append((None, self.gap_duration))


class Movement1(object):
    def __init__(self):
        self.part_names = (
            'oboe',
            'bass_clarinet',
            'vibraphone',
            'bass'
        )
        self.starting_tempo_bpm = 105
        self.n_quarters = 128
        self.ticks_per_quarter = 32
        self.duration_tools = Duration(ticks=self.ticks_per_quarter, ticks_per_quarter=self.ticks_per_quarter)

        m = self.music = Music(
            part_names=self.part_names,
            starting_tempo_bpm=self.starting_tempo_bpm,
            output_dir_name='experiment11',
            n_quarters=self.n_quarters,
            ticks_per_quarter=self.ticks_per_quarter,
        )


        instrument = self.music.instruments[0]
        lick = Lick()
        sequence = Sequence(lick, instrument, 12)

        start_offset = self.duration_tools.quarters_and_sixteenths_to_ticks(quarters=0, sixteenths=0, ticks_per_quarter=self.ticks_per_quarter)
        # duration = self.duration_tools.quarters_and_sixteenths_to_ticks(quarters=0, sixteenths=int(lick.duration * 4), ticks_per_quarter=self.ticks_per_quarter)

        for pitch, dur in sequence:
            duration_in_ticks = int(dur * self.ticks_per_quarter)

            instrument.put_note(start_offset, duration_in_ticks, pitch=pitch)
            start_offset += duration_in_ticks


        for i in self.music.instruments:
            i.closeout()

        print 'Done making the music. Starting notation.'


    # def put_lick(self, lick, instrument):
    #     # instrument = random.choice(self.music.instruments)

    #     openings = instrument.timeline.find_openings(
    #         length_quarters=lick.duration_quarters,
    #         length_sixteenths=lick.duration_sixteenths
    #     )
    #     if not openings:
    #         raise NoMoreOpenings()

    #     # Find openings that start on the quarternote
    #     openings = [o for o in openings if o[1] == 0]
    #     if openings:
    #         start_quarter, start_sixteenth, length_quarter, length_sixteenth = random.choice(openings)
    #     else:
    #         return

    #     start_offset = duration_tools.quarters_and_sixteenths_to_ticks(quarters=start_quarter, sixteenths=start_sixteenth)

    #     duration = duration_tools.quarters_and_sixteenths_to_ticks(quarters=length_quarter, sixteenths=length_sixteenth)

    #     lick = transpose(lick, random.randint(1, 11))
    #     lick = put_in_scale(lick, self.scale)
    #     lick = put_in_register(lick, instrument.safe_register)

    #     for pitch, dur in lick:
    #         duration_in_ticks = int(dur * self.ticks_per_quarter)
    #         instrument.put_note(start_offset, duration_in_ticks, pitch=pitch)
    #         start_offset += duration_in_ticks

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

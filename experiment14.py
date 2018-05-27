#!/usr/bin/env python

import random
import collections
import argparse

import numpy as np

from music_tools2 import Music
from duration import Duration
from sections import Sections


def weighted_choice(indexes, weights):
    # Make weights sum to 1.0
    sum_weights = float(sum(weights))
    weights = [w / sum_weights for w in weights]

    # Weighted choice
    index = np.random.choice(indexes, p=weights)

    return index, weights


def descending_weighted_choice(indexes):
    weights = [w + 1 for w in reversed(indexes)]
    return weighted_choice(indexes, weights)


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
        subdivision_durations = random.choice([
            [1],
            [.5, .5],
            [.75, .75],
            [1, .5],
            [2],
            [1, 1],
            [.75, .75, .5],
            [1, .5, .5],
        ])

        end_duration = random.choice([.5, 1.0, 1.5, 2.0])

        rhythm = []
        for length in subdivision_durations:
            rhythm.extend(self.make_rhythmic_figure(length))
        rhythm.append(end_duration)

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

        self.interval = random.choice([0, 1, -1, 2, -2])  # , 5, -5, 7, -7])

        max_gap_duration = lick.duration  # * 2
        gap_duration_options = np.linspace(0, max_gap_duration, (max_gap_duration * 4) + 1)

        # Only include gaps that would make the total duration an even number of sixteenth notes
        gap_duration_options = [g for g in gap_duration_options if (g + lick.duration) % .5 == 0.0]

        self.gap_duration, _ = descending_weighted_choice(gap_duration_options)

        for repetition in range(repetitions):
            transposition = self.interval * repetition

            lick = transpose(lick, transposition)
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
            'bass',
        )

        self.pick_duration_and_bpm()

        m = self.music = Music(
            part_names=self.part_names,
            starting_tempo_bpm=self.bpm,
            output_dir_name='experiment11',
            n_quarters=self.n_quarters,
            ticks_per_quarter=self.ticks_per_quarter,
        )

        self.make_music()

        for i in self.music.instruments:
            i.closeout()

        print 'Done making the music. Starting notation.'

    def pick_duration_and_bpm(self):
        min_seconds = 135
        max_seconds = 160
        target_duration_seconds = random.randint(min_seconds, max_seconds + 1)

        min_bpm = 68
        max_bpm = 118
        self.bpm = random.randint(min_bpm, max_bpm + 1)

        self.quarter_duration_seconds = 60.0 / self.bpm
        self.bar_duration_seconds = self.quarter_duration_seconds * 4

        self.n_bars = int(target_duration_seconds / self.bar_duration_seconds)
        self.n_quarters = self.n_bars * 4

        self.duration = self.bar_duration_seconds * self.n_bars

        self.ticks_per_quarter = 32
        self.n_ticks = self.n_quarters * self.ticks_per_quarter


    def put_fragment(self, fragment, instrument, offset):
        for pitch, duration in fragment:
            instrument.put_note(offset, duration, pitch)
            offset += duration

    def make_music(self):
        # self.setup_harmony_sections()


        oboe = self.music.oboe
        bass_clarinet = self.music.bass_clarinet
        vibes = self.music.vibraphone
        bass = self.music.bass

        lick = Lick()

        vibes_sequence = Sequence(lick, vibes, 20)

        # for note in vibes_sequence:
        #     harmony_section = self.harmony_sections.get_by_sample_offset(start)


        self.put_fragment(vibes_sequence, vibes, 0)

        oboe_sequence = Sequence(lick, oboe, 16)
        self.put_fragment(oboe_sequence, oboe, 8)

        bass_sequence = Sequence(lick, bass, 12)
        self.put_fragment(bass_sequence, bass, 16)

        bass_clarinet_sequence = Sequence(lick, oboe, 8)
        self.put_fragment(bass_clarinet_sequence, bass_clarinet, 20)

    # def make_line(self):


    # def setup_harmony_sections(self):
    #     self.harmony_sections = Sections([3, 1] * self.n_bars, self.n_ticks)
    #     for i, harmony in enumerate(self.harmony_sections):
    #         if i % 2:
    #             harmony.harmony = [0, 4, 7]
    #         else:
    #             harmony.harmony = [5, 9, 0]


    def notate(self):
        self.music.notate()


def utah2018():
    m1 = Movement1()
    m1.notate()


if __name__ == '__main__':
    utah2018()

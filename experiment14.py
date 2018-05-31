#!/usr/bin/env python

import random
import collections
import argparse

import numpy as np

from music_tools2 import Music
from duration import Duration
from sections import Layers


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
    def __init__(self, instrument=None):
        self.instrument = instrument
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
        if self.instrument:
            register = self.instrument.safe_register

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

        max_gap_duration = lick.duration * 1.5
        gap_duration_options = np.linspace(0, max_gap_duration, (max_gap_duration * 4) + 1)
        gap_duration_options = gap_duration_options[2:]

        # Only include gaps that would make the total duration an even number of quarter notes
        gap_duration_options = [g for g in gap_duration_options if (g + lick.duration) % 2.0 == 0.0]

        self.gap_duration, _ = descending_weighted_choice(gap_duration_options)

        self.duration = (lick.duration + self.gap_duration)* repetitions

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
            output_dir_name='experiment14',
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

        # Make harmonies plan
        self.layers.add_layer('harmony', self.n_quarters)
        for harmony in self.layers['harmony']:
            if harmony.index % 8 == 0:
                harmony.harmony = [0, 4, 7]
                harmony.scale = [0, 2, 4, 5, 7, 9, 11]
            elif harmony.index % 8 == 1:
                harmony.harmony = [5, 9, 0]
                harmony.scale = [0, 2, 4, 5, 7, 9, 11]

            elif harmony.index % 8 == 2:
                harmony.harmony = [0, 4, 7]
                harmony.scale = [0, 2, 4, 5, 7, 9, 11]
            elif harmony.index % 8 == 3:
                harmony.harmony = [5, 9, 0]
                harmony.scale = [0, 2, 4, 5, 7, 9, 11]

            elif harmony.index % 8 == 4:
                harmony.harmony = [2, 5, 9, 0]
                harmony.scale = [0, 2, 4, 5, 7, 9, 11]
            elif harmony.index % 8 == 5:
                harmony.harmony = [2, 5, 7, 11]
                harmony.scale = [0, 2, 4, 5, 7, 9, 11]

            elif harmony.index % 8 == 6:
                harmony.harmony = [0, 4, 7, 10]
                harmony.scale = [0, 2, 4, 5, 7, 9, 10]
            elif harmony.index % 8 == 7:
                harmony.harmony = [5, 9, 0, 3]
                harmony.scale = [0, 2, 3, 5, 7, 9, 10]


        for instrument in self.music.instruments:
            offset = 0
            duration_remaining = self.duration_quarters
            while duration_remaining > 50.0:
                lick = Lick(instrument=instrument)
                sequence = Sequence(lick, instrument, repetitions=random.randint(3, 10))
                duration_remaining -= sequence.duration

                previous_pitch = lick[0][0]
                for pitch, duration in sequence:
                    now = self.layers.get_in_window(offset, duration)

                    if pitch is not None:
                        pitch_options = range(pitch - 4, pitch + 5)
                        if previous_pitch in pitch_options:
                            pitch_options.remove(previous_pitch)

                        harmonies = now['harmony']

                        if len(harmonies) > 1:
                            harmony_options = list(set(harmonies[0].harmony).intersection(*[h.harmony for h in harmonies]))
                            if not harmony_options or random.random() < .2:
                                scales = [h.scale for h in harmonies]
                                harmony_options = list(set(scales[0]).intersection(*scales))
                        else:
                            harmony_options = harmonies[0].harmony
                            if not harmony_options or random.random() < .2:
                                harmony_options = harmonies[0].scale

                        # harmony_options = now['harmony'].scale
                        # if now['sixteenths'].index % 2 == 0:
                        #     harmony_options = now['harmony'].harmony

                        pitch_options = [p for p in pitch_options if p % 12 in harmony_options]
                        if not pitch_options:
                            pitch_options = range(pitch - 8, pitch + 9)
                            pitch_options = [p for p in pitch_options if p % 12 in harmony_options]

                        pitch = random.choice(pitch_options)
                        previous_pitch = pitch

                    instrument.put_note(offset, duration, pitch)
                    offset += duration






        # vibes_sequence = Sequence(lick, vibes, 20)

        # # for note in vibes_sequence:
        # #     harmony_section = self.harmony_sections.get_by_sample_offset(start)


        # self.put_fragment(vibes_sequence, vibes, 0)

        # oboe_sequence = Sequence(lick, oboe, 16)
        # self.put_fragment(oboe_sequence, oboe, 8)

        # bass_sequence = Sequence(lick, bass, 12)
        # self.put_fragment(bass_sequence, bass, 16)

        # bass_clarinet_sequence = Sequence(lick, oboe, 8)
        # self.put_fragment(bass_clarinet_sequence, bass_clarinet, 20)

    # def make_line(self):


    def notate(self):
        self.music.notate()


def utah2018():
    m1 = Movement1()
    m1.notate()


if __name__ == '__main__':
    utah2018()

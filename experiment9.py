#!/usr/bin/env python

import random
import collections
import itertools
from collections import Counter
import argparse

import numpy as np

from music_tools import Music, pitches_to_chord_type
from utils import weighted_choice, pairwise



def get_base_interval(interval):
    interval = interval % 12
    if interval > 6:
        interval = 12 - interval
    return interval


def print_chord(chord):
    result = ''
    for pc in range(12):
        if pc in chord:
            result += '{:<2} '.format(pc)
        else:
            result += '.  '
    result = result * 2
    return result


def pc_spell(root, chord_type):
    return [(p + root) % 12 for p in chord_type]


chord_types = [
    (0, 4, 7),
    (0, 3, 7),
    (0, 4, 7, 10),
    (0, 3, 7, 10),
    (0, 4, 7, 11),
    (0, 5, 7),

    # (0, 2, 4, 7, 9),

]
pitch_classes = range(12)


def make_all_transitions():
    """
    Returns this:

    transitions = {
        starting chord type: {
            n common tones: [
                (root motion, destination chord type),
                (root motion, destination chord type),
                ...
            ],
            n+1 common tones: [
                (root motion, destination chord type),
                (root motion, destination chord type),
                ...
            ],
            n+2 common tones: [
                (root motion, destination chord type),
                (root motion, destination chord type),
                ...
            ],
            ...
        },
        another starting chord type: {
            ...
        },
        ...
    }

    """

    transitions = {}
    for starting_chord_type in chord_types:
        transitions[starting_chord_type] = collections.defaultdict(list)

        for destination_chord_type in chord_types:
            for root_motion in pitch_classes:
                destination_pitch_classes = [(p + root_motion) % 12 for p in destination_chord_type]

                if starting_chord_type == tuple(sorted(destination_pitch_classes)):
                    continue

                n_common_tones = len(set(destination_pitch_classes).intersection(set(starting_chord_type)))

                transitions[starting_chord_type][n_common_tones].append((root_motion, destination_chord_type))
    return transitions

transitions = make_all_transitions()


def generate_chords(n=100):
    root = random.choice(pitch_classes)
    chord_type = random.choice(chord_types)

    chords = []

    for _ in range(n):
        n_common_tones_options = transitions[chord_type].keys()
        n_common_tones_options.remove(0)
        n_common_tones_options.remove(1)
        n_common_tones = random.choice(n_common_tones_options)
        options = transitions[chord_type][n_common_tones]

        root_motion, chord_type = random.choice(options)

        root = (root + root_motion) % 12

        chord = pc_spell(root, chord_type)
        chord.sort()
        chords.append(chord)

    return chords


def find_loops(seq):
    seen = []
    dupes = collections.defaultdict(list)
    for i, item in enumerate(seq):
        dupes[item].append(i)

    loops = collections.defaultdict(list)
    for item in dupes:
        indexes = dupes[item]
        if len(indexes) > 1:
            for a, b in pairwise(indexes):
                loops[seq[a]].append(seq[a:b])

    return loops


def get_harmony_loops(min_length=4, max_length=6):
    chords = generate_chords(1500)
    chords = [tuple(c) for c in chords]

    loops = find_loops(chords)

    good_loops = []
    for starting_chord in loops:
        for loop in loops[starting_chord]:
            if min_length <= len(loop) <= max_length:
                good_loops.append(loop)

    return good_loops


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

        # chords_loop = random.choice(get_harmony_loops())

        self.lick = Lick()

        scale = get_random_scale()

        for _ in range(100):
            instrument = random.choice(self.music.instruments)

            lick = transpose(self.lick, random.randint(1, 11))
            lick = put_in_scale(lick, scale)
            lick = put_in_register(lick, instrument.safe_register)

            rest_before = random.choice([0, 0, 1, 1, 1, 2, 2, 2, 3, 4])
            rest_after = random.choice([0, 0, 1, 1, 1, 2, 2, 2, 3, 4])

            if rest_before:
                instrument.add_note(pitch='rest', duration=rest_before)

            for p, d in lick:
                instrument.add_note(pitch=p, duration=d)

            if rest_after:
                instrument.add_note(pitch='rest', duration=rest_after)



    # def make_theme(self):
    #     rhythm = self.make_rhythmic_figure(4)
    #     theme = []

    #     oboe = self.music.oboe
    #     pitch = random.choice(oboe.middle_register)
    #     for duration in rhythm:

    #         lowest = max([pitch - 3, oboe.safe_register[0]])
    #         highest = min([pitch + 3, oboe.safe_register[-1]])
    #         pitch_options = [p for p in oboe.safe_register if lowest <= p <= highest and p is not pitch]
    #         pitch = random.choice(pitch_options)

    #         theme.append((pitch, duration))

    #     return theme

    # def make_rhythmic_figure(self, duration_in_quarters=4):
    #     remaining_duration = duration_in_quarters
    #     rhythm = []
    #     while remaining_duration:
    #         duration_options = np.linspace(.25, remaining_duration, remaining_duration * 4)
    #         duration = random.choice(duration_options)
    #         rhythm.append(duration)
    #         remaining_duration -= duration
    #     return rhythm

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

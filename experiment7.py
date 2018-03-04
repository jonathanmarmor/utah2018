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
            output_dir_name='experiment7-looping',
        )

        harmony_loops = get_harmony_loops()

        loop = random.choice(harmony_loops)
        print loop
        chords = loop * 16

        for i, chord in enumerate(chords):
            # print i
            chord_duration = 2  # random.choice([1, 2, 2, 2, 4])

            for instrument in self.music.instruments:
                # print instrument.instrument_name
                remaining_duration = chord_duration
                while remaining_duration:
                    duration_options = np.linspace(.25, remaining_duration, remaining_duration * 4)
                    duration = random.choice(duration_options)
                    remaining_duration -= duration

                    if len(instrument) == 0:
                        previous_pitch = random.choice(instrument.middle_register)
                    else:
                        previous_pitch = instrument[-1].pitch

                    lowest = max([previous_pitch - 5, instrument.safe_register[0]])
                    highest = min([previous_pitch + 5, instrument.safe_register[-1]])

                    pitch_options = [p for p in instrument.range if p % 12 in chord and lowest <= p <= highest and p is not previous_pitch]
                    # print pitch_options
                    pitch = random.choice(pitch_options)

                    instrument.add_note(pitch=pitch, duration=duration)

# TODO: alternate between this texture and another texture
# TODO: find loop points in the harmonies and loop them


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

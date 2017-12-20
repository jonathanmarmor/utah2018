#!/usr/bin/env python

import random
import collections
import itertools
from collections import Counter
import argparse

from music_tools import Music, pitches_to_chord_type
from utils import weighted_choice



def pc_spell(root, chord_type):
    return [(p + root) % 12 for p in chord_type]


chord_types = [
    (0, 4, 7),
    (0, 3, 7),
    (0, 4, 7, 10),
    (0, 3, 7, 10),
    (0, 4, 7, 11),
    (0, 5, 7),
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


class Movement1(object):
    def __init__(self):
        m = self.music = Music(
            part_names=(
                'flute',
                'oboe',
                'guitar',
                'bass',
            ),
            starting_tempo_bpm=105
        )
        beat_duration = 60.0 / self.music.starting_tempo_bpm

        chords = generate_chords()

        for i, chord in enumerate(chords):
            self.gen(self.music.oboe, chord, n_notes_options=[1, 2, 4], radius=4)
            # self.gen(self.music.flute, chord, n_notes_options=[1, 2, 4], radius=4)
            self.gen(self.music.guitar, chord, n_notes_options=[4, 8], radius=5)
            self.gen(self.music.bass, chord, n_notes_options=[2, 4], radius=5)

    def gen(self, instrument, chord, n_notes_options=[1, 2, 4], radius=4):
        n_notes = random.choice(n_notes_options)
        dur_map = {
            1: 2,
            2: 1,
            4: .5,
            8: .25
        }
        note_duration = dur_map[n_notes]
        for _ in range(n_notes):
            previous_note = instrument.get_last_pitched()
            pitch_options = [p for p in instrument.range if p % 12 in chord]
            if previous_note:
                previous_pitch = previous_note.pitch
                pitch_options = [p for p in pitch_options if previous_pitch - radius < p < previous_pitch + radius]
            pitch = random.choice(pitch_options)
            if previous_note and pitch == previous_note.pitch:
                previous_note.duration += note_duration
            else:
                instrument.add_note(pitch=pitch, duration=note_duration)


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

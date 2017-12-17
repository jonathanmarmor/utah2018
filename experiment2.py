#!/usr/bin/env python

import random
from collections import Counter
import argparse

from music_tools import Music, pitches_to_chord_type
from utils import weighted_choice


class Movement1(object):
    def __init__(self):
        self.stats = self.init_stats()
        m = self.music = Music(
            part_names=(
                'oboe',
                'guitar',
            ),
            starting_tempo_bpm=105
        )
        beat_duration = 60.0 / self.music.starting_tempo_bpm

        self.go()

    def notate(self):
        self.music.notate()

    def init_stats(self):
        stats = Counter()
        stats['beats_since_last_rest'] = Counter()
        stats['harmonies'] = Counter()
        return stats

    # def print_stats(self):
    #     print
    #     print '-' * 10, 'STATS', '-' * 10
    #     for k in self.stats:
    #         print k, self.stats[k]
    #     print
    #     for k in sorted(self.stats['beats_since_last_rest'].keys()):
    #         print '{:<5}: {}'.format(k, self.stats['beats_since_last_rest'][k])

    def print_columns(self):
        print
        header = '{:<16}'.format('tick')
        for part_id in self.music.part_ids:
            header += '{:<16}'.format(part_id)
        print header

        for notes in self.music:
            row = '{:<16}'.format(notes['tick'])
            for part_id in self.music.part_ids:
                row += '{:<16}'.format(notes[part_id].pitch)
            print row

    def first(self):
        oboe_first_pitch = 83
        self.music.ob.add_note(pitch=oboe_first_pitch, duration=2)
        self.music.guitar.add_note(pitch=oboe_first_pitch - 24, duration=2)

    def go(self, duration=120.0):
        self.first()

        while self.music.duration_seconds() < duration:
            self.next()

    def next(self):
        # Just some random notes as a test
        o = self.music.ob
        oboe_pitch = random.choice(o.range)
        self.music.ob.add_note(
            pitch=oboe_pitch,
            duration=random.choice([0.5, 1, 1, 1, 2, 2, 3]))

        g = self.music.guitar
        guitar_pitch = random.choice(g.range)
        self.music.guitar.add_note(
            pitch=guitar_pitch,
            duration=random.choice([0.5, 1, 1, 1, 2, 2, 3]))


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

#!/usr/bin/env python

import random
from collections import Counter

from music_tools import Music, pitches_to_chord_type
from utils import weighted_choice


ALLOWED_HARMONIES = {
    (0, 1): 3.0,

    (0, 1, 2): 2.0,

    (0, 1, 3): 1.0,
    (0, 2, 3): 1.0,

    (0, 1, 4): .2,
    (0, 3, 4): .2,

    (0, 1, 5): .1,
    (0, 4, 5): .1,

    (0, 1, 6): .1,
    (0, 5, 6): .1,

    (0, 1, 7): .1,
    (0, 6, 7): .1,

    (0, 1, 8): .1,
    (0, 7, 8): .1,

    (0, 1, 9): .001,
    (0, 8, 9): .001,

    (0, 1, 10): .001,
    (0, 9, 10): .001,

    (0, 1, 11): .1,
    (0, 10, 11): .1,

    (0, 1, 12): .2,
    (0, 11, 12): .2,

    (0, 1, 13): .2,
    (0, 12, 13): .2,

    (0, 1, 14): .1,
    (0, 13, 14): .1,
}

# REVEALED_HARMONY_WEIGHTS = {
#     0: 75,
#     1: 100,
#     2: 50,
#     3:
#     4:
#     5:
#     6:
#     7: 60,
#     8:
#     9:
#     10:
#     11:
#     12: 75
#     13:
#     14:
# }

THIRDS_INTERVALS = {
    3: 3,
    4: 10,
    5: 4,
    7: 4,
    8: 5,
    9: 10
}


DISTANCE_WEIGHTS = [.25, 1.0, .8] + [1.0 / (2.0 ** x) for x in range(3, 50)]


BLUES_PROGRESSION = [
    (0, 4, 7),
    (0, 4, 7),
    (0, 4, 7),
    (0, 4, 7),
    (0, 5, 9),
    (0, 5, 9),
    (0, 4, 7),
    (0, 4, 7),
    (0, 2, 7, 11),
    (0, 5, 9),
    (0, 4, 7),
    (0, 4, 7, 11)
]
SCALE = (0, 2, 3, 4, 5, 7, 9, 11)


class Experiment1(object):
    def __init__(self):
        self.stats = self.init_stats()
        m = self.music = Music(
            part_names=(
                'oboe',
                'oboe 2',
                'oboe 3',
                # 'english_horn',
                # 'english_horn 2',
                # 'soprano_recorder',
                # 'soprano_recorder 2',
                'alto_recorder',
                'alto_recorder 2',
                'alto_recorder 3',
                # 'baritone_saxophone',
                # 'guitar',
                # 'guitar 2',
                # 'guitar 3',
                # 'piano',
                # 'piano 2',
                # 'organ',
                # 'organ 2',

                # 'violin',
                # 'flute',
                # 'oboe',
                # 'clarinet',
                # 'alto_saxophone',
                # 'trumpet',
                'bass'
            ),
            starting_tempo_bpm=160
        )
        beat_duration = 60.0 / self.music.starting_tempo_bpm

        self.bass = m.bass


        self.clusters = [m.ob, m.ob2, m.ob3]
        cluster_lowest_pitch = 70
        for i in self.clusters:
            i.cluster_range = [p for p in i.range if p >= cluster_lowest_pitch]
        self.clusters[0].add_note(pitch=82, duration=2)
        self.clusters[1].add_note(pitch=81, duration=2)
        self.clusters[2].add_note(pitch=80, duration=2)
        while beat_duration * self.clusters[0].duration() < 120.0:
            self.next(bass=True)

        self.clusters = [m.a_rec, m.a_rec2, m.a_rec3]
        cluster_lowest_pitch = 70
        for i in self.clusters:
            i.cluster_range = [p for p in i.range if p >= cluster_lowest_pitch]
        self.clusters[0].add_note(pitch=85, duration=2)
        self.clusters[1].add_note(pitch=84, duration=2)
        self.clusters[2].add_note(pitch=83, duration=2)
        while beat_duration * self.clusters[0].duration() < 120.0:
            self.next(bass=False)





        # self.clusters = [m.a_rec, m.a_rec2, m.a_rec3]

        # # self.clusters = [m.f, m.ob, m.cl]
        # # self.thirds = [m.alto_saxophone, m.trumpet]
        # # self.violin = m.violin
        # # self.bass = m.bass

        # # self.thirds_register = range(55, 81)

        # cluster_lowest_pitch = 70
        # for i in self.clusters:
        #     i.cluster_range = [p for p in i.range if p >= cluster_lowest_pitch]

        # self.first()
        # self.go(120.0)
        # self.stats['duration'] = self.music.duration_seconds()
        # # self.print_stats()

    def notate(self):
        self.music.notate()

    def init_stats(self):
        stats = Counter()
        stats['beats_since_last_rest'] = Counter()
        stats['harmonies'] = Counter()
        return stats

    def print_stats(self):
        print
        print '-' * 10, 'STATS', '-' * 10
        for k in self.stats:
            print k, self.stats[k]
        print
        for k in sorted(self.stats['beats_since_last_rest'].keys()):
            print '{:<5}: {}'.format(k, self.stats['beats_since_last_rest'][k])

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


        self.clusters[0].add_note(pitch=84, duration=2)
        self.clusters[1].add_note(pitch=83, duration=2)
        self.clusters[2].add_note(pitch=82, duration=2)


        # self.music.f.add_note(pitch=84, duration=2)
        # self.music.ob.add_note(pitch=83, duration=2)
        # self.music.cl.add_note(pitch=82, duration=2)

        # self.music.alto_saxophone.add_note(pitch=67, duration=16)
        # self.music.trumpet.add_note(pitch=64, duration=16)

        # self.music.violin.add_note(pitch=67, duration=16)

        # self.music.bass.add_note(pitch=48, duration=1)

    def go(self, duration=120.0):
        while self.music.duration_seconds() < duration:
            self.next()

    def next(self, bass=False):
        self.clusters_next()
        # self.thirds_next()
        # self.violin_next()
        if bass:
            self.bass_next()

    def clusters_next(self):
        changing, not_changing = self.clusters_pick_changing_instrument()
        new_pitch = self.clusters_pick_new_pitch(changing, not_changing)

        total_event_duration = 0.0
        if random.randint(2, 17) < changing.beats_since_last_rest():
            # If the last note in the phrase was a quarter note, make it longer
            if changing[-1].duration == 1:
                # Make it even longer if the revealed harmony is good
                revealed_harmony = self.clusters_get_revealed_harmony(not_changing)
                nice_dyads = [0, 1, 2, 7, 12]
                if revealed_harmony in nice_dyads:
                    options_for_durations_to_add = [1.0, 2.0, 2.0, 2.0, 3.0, 4.0]
                else:
                    options_for_durations_to_add = [1.0, 1.0, 1.0, 2.0]

                dur_to_add = random.choice(options_for_durations_to_add)
                for instrument in self.clusters:
                    instrument[-1].duration += dur_to_add

            self.stats['beats_since_last_rest'][changing.beats_since_last_rest()] += 1

            # Add a rest before the next note
            rest_duration_options = [1,  2]
            rest_duration_weights = [16, 1]
            if changing.beats_since_last_rest(rest_duration=4) > 40:
                if random.random() < .5:
                    rest_duration_options = [4,  5,  6, 7]
                    rest_duration_weights = [16, 12, 2, 1]

            rest_duration = weighted_choice(rest_duration_options, rest_duration_weights)

            total_event_duration += rest_duration
            changing.add_note(pitch='rest', duration=rest_duration)

        note_duration = random.choice([1, 1, 1, 1, 1, 2, 2, 3])
        total_event_duration += note_duration

        changing.add_note(pitch=new_pitch, duration=note_duration)

        for i in not_changing:
            i[-1].duration += total_event_duration

        harmony = pitches_to_chord_type([i[-1].pitch for i in self.clusters])
        self.stats['harmonies'][harmony] += 1

    def clusters_get_revealed_harmony(self, not_changing):
        not_changing_pitches = [i[-1].pitch for i in not_changing]
        revealed_harmony = max(not_changing_pitches) - min(not_changing_pitches)
        return revealed_harmony

    def clusters_pick_changing_instrument(self):
        # TODO: try prefering picking changing instruments when the other two instruments are playing a minor second

        weights = []
        for inst in self.clusters:
            sustain_time = inst.beats_since_last_rest() * (60.0 / self.music.starting_tempo_bpm)
            # weight = (inst.beats_since_last_rest() + 1) ** 2.0
            # weight = sustain_time ** 2
            sustain_weight = sustain_time

            # not_changing = [i for i in self.clusters if i is not inst]
            # revealed_harmony = self.clusters_get_revealed_harmony(not_changing)
            # revealed_harmony_weight =

            # weight = (sustain_weight * ) + (revealed_harmony_weight * )
            weight = sustain_weight
            weights.append(weight)

        changing = weighted_choice(self.clusters, weights)

        not_changing = [w for w in self.clusters if w is not changing]

        return changing, not_changing

    def clusters_pick_new_pitch(self, changing, not_changing, allow_repeated_pitch=False):

        ### Pick only allowed harmonies
        holdovers = [i[-1].pitch for i in not_changing]
        holdovers.sort()

        previous_pitch = changing.get_last_pitched().pitch

        pitch_options = []
        weights = []

        if allow_repeated_pitch:
            available_pitches = changing.cluster_range[:]
        else:
            available_pitches = [p for p in changing.cluster_range if p is not changing[-1].pitch]

        bar_number = int(changing.duration() % 4)

        for pitch_option in available_pitches:
            harmony = holdovers + [pitch_option]
            harmony.sort()
            harmony = [ps - harmony[0] for ps in harmony]

            harmony = list(set(harmony))
            harmony.sort()
            harmony = tuple(harmony)

            if harmony in ALLOWED_HARMONIES:
                pitch_options.append(pitch_option)

                # The further away the new pitch from the previous pitch, the lower the weight
                distance = abs(previous_pitch - pitch_option)
                distance_weight = DISTANCE_WEIGHTS[distance]

                harmony_weight = ALLOWED_HARMONIES[harmony]

                blues_weight = 1
                if pitch_option % 12 in BLUES_PROGRESSION[bar_number]:
                    blues_weight = 3

                # weight the different weights
                weight = ((distance_weight * 1.0) + (harmony_weight * .33)) * blues_weight

                if pitch_option > previous_pitch:
                    weight *= 1.5

                weights.append(weight)

        new_pitch = weighted_choice(pitch_options, weights)

        if new_pitch == None:
            self.stats['allow_repeated_pitch'] += 1
            new_pitch = self.clusters_pick_new_pitch(changing, not_changing, allow_repeated_pitch=True)
        else:
            self.stats['dont_allow_repeated_pitch'] += 1

        return new_pitch

    def bass_next(self):
        bar_number = self.bass.duration() // 4
        bar_in_progression = bar_number % len(BLUES_PROGRESSION)

        beat_number = int(self.bass.duration() % 4)


        last_pitched_note = self.bass.get_last_pitched()
        if last_pitched_note:
            previous_pitch = self.bass.get_last_pitched().pitch
        else:
            previous_pitch = 48


        pitch_options = []
        weights = []

        available_pitches = range(35, 52)
        for pitch_option in available_pitches:
            weight = 1.0

            if pitch_option % 12 not in SCALE:
                weight = .1

            if pitch_option % 12 in BLUES_PROGRESSION[bar_in_progression]:
                weight = 8.0


            # The further away the new pitch from the previous pitch, the lower the weight
            distance = abs(previous_pitch - pitch_option)

            if distance == 0:
                weight = 1.0
            else:
                if distance < 3:
                    weight = weight * 8
                elif distance < 6:
                    weight = weight * 4
                # elif distance < 9:
                #     weight = weight * 2
                elif distance > 12:
                    weight = .125

            pitch_options.append(pitch_option)
            weights.append(weight)

        pitch = weighted_choice(pitch_options, weights)

        if beat_number == 0:
            duration_options = [1,  2,  3, 4, 5, 6, 7, 8]
            duration_weights = [35, 24, 2, 6, 1, 1, 1, 2]
        elif beat_number == 1:
            duration_options = [1,  2,  3,  4, 5, 6, 7]
            duration_weights = [35, 12, 16, 1, 1, 1, 3]
        elif beat_number == 2:
            duration_options = [1,  2,  4, 6]
            duration_weights = [24, 24, 1, 2]
        elif beat_number == 3:
            duration_options = [1,  2, 5]
            duration_weights = [40, 2, 5]

        duration = weighted_choice(duration_options, duration_weights)

        self.bass.add_note(pitch=pitch, duration=duration)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--dont-notate',
        help='dont generate notation',
        action="store_true")
    args = parser.parse_args()
    m3 = Movement1()
    if not args.dont_notate:
        m3.notate()

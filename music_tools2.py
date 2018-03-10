#!/usr/bin/env python

import math

import numpy as np

from notation_tools import Notation
from instrument_data import instrument_data
import utils


def meter_position(tick):
    position_within_beat, beat = math.modf(tick)
    beat = int(beat)
    beat_within_bar = beat % 4
    bar_number = beat // 4
    return bar_number, beat_within_bar, position_within_beat


# def beats_to_seconds(beats, bpm=60):
#     return beats / (bpm / 60.0)


# def pitches_to_pitchclasses(pitches):
#     pitchclasses = [p % 12 for p in pitches]
#     pitchclasses = list(set(pitchclasses))
#     pitchclasses.sort()
#     pitchclasses = tuple(pitchclasses)
#     return pitchclasses


# def pitches_to_chord_type(pitches):
#     chord_type = list(set(pitches))
#     chord_type.sort()
#     lowest = chord_type[0]
#     chord_type = [p - lowest for p in chord_type]
#     return tuple(chord_type)


# def get_inversions(pitchclasses):
#     inversions = []
#     for p1 in pitchclasses:
#         inversion = [(p2 - p1) % 12 for p2 in pitchclasses]
#         inversion.sort()
#         inversions.append(tuple(inversion))
#     return inversions


# def make_allowed_harmonies():
#     allowed_harmonies_1st_inversions = [
#         # Just a quick draft
#         (0, ),
#         # (0, 2),
#         # (0, 3),
#         (0, 4),
#         (0, 5),
#         (0, 4, 7),
#         (0, 3, 7),
#         (0, 5, 7),
#         (0, 3, 5),
#         (0, 2, 5),
#         # (0, 3, 6),
#         # (0, 4, 8),
#         (0, 2, 4),
#         # (0, 2, 6),
#         (0, 4, 7, 11),
#         (0, 4, 7, 10),
#         (0, 3, 7, 10),
#         (0, 5, 7, 10),
#         (0, 2, 5, 7),
#         (0, 2, 4, 7),
#         (0, 2, 3, 7),
#         (0, 3, 5, 7),
#         # (0, 3, 6, 9),
#         # (0, 2, 4, 8),
#         (0, 2, 4, 7, 11),
#         (0, 2, 4, 7, 10),
#         (0, 2, 3, 7, 10),
#         (0, 2, 4, 6, 8, 10),
#         (0, 2, 4, 5, 7, 11),
#         (0, 2, 4, 5, 7, 10),
#         (0, 2, 3, 5, 7, 10),
#     ]
#     allowed_harmonies = []
#     for harmony in allowed_harmonies_1st_inversions:
#         for root in range(12):
#             transposed_harmony = tuple([(p + root) % 12 for p in harmony])
#             allowed_harmonies.append(transposed_harmony)

#     # for harmony in allowed_harmonies_1st_inversions:
#     #     inversions = get_inversions(harmony)
#     #     allowed_harmonies.extend(inversions)
#     return allowed_harmonies


# allowed_harmonies = make_allowed_harmonies()


# def is_harmony_allowed(pitches):
#     return tuple(pitches_to_pitchclasses(pitches)) in allowed_harmonies


# def get_intervals(pitches):
#     ps = list(set(pitches))
#     ps.sort()
#     return [b - a for a, b in pairwise(ps)]


class Tick(object):
    def __init__(self, tick):
        self.tick = tick
        self.bar_number, self.beat_within_bar, self.position_within_beat = meter_position(tick)


class Note(object):
    def __init__(self, pitch=None, duration=0.0):
        self.pitch = pitch
        self.duration = duration

    def __repr__(self):
        return '<Note - pitch: {} duration: {}>'.format(self.pitch, self.duration)


class Instrument(list):
    def __init__(self, part_name):
        self._make_part_names(part_name)

        self.range = instrument_data[self.instrument_name]['range']
        self._make_registers()

    def _make_part_names(self, part_name):
        self.part_name = part_name
        self.part_id = part_name
        self.instrument_name = part_name
        self.instrument_number = 1

        if ' ' in part_name:
            name_chunks = part_name.split(' ')
            self.instrument_name = ' '.join(name_chunks[:-1])
            self.instrument_number = int(name_chunks[-1])  # if more than one of the same instrument
            self.part_id = part_name.replace(' ', '_')

        self.abbreviation = instrument_data[self.instrument_name]['abbreviation']
        self.abbreviation_id = self.abbreviation
        if self.instrument_number > 1:
            self.abbreviation_id = '{}{}'.format(self.abbreviation, self.instrument_number)
            self.abbreviation = '{} {}'.format(self.abbreviation, self.instrument_number)

    def __repr__(self):
        return '<music_tools.Instrument: {}>'.format(self.part_name)

    def _make_registers(self, n_chunks=7):
        self.lowest_note = self.range[0]
        self.highest_note = self.range[-1]

        registers = list(utils.split_list(self.range, n_chunks=n_chunks))

        self.middle_register = registers[3]  # assuming 7 divisions
        self.highest_register = registers[-1]
        self.lowest_register = registers[0]
        self.safe_register = utils.flatten(registers[1:-1])
        self.very_safe_register = utils.flatten(registers[2:-2])

    # def duration(self):
    #     return sum([note.duration for note in self])

    # def get_tick(self):
    #     return Tick(self.duration())

    def add_note(self, pitch=None, duration=0.0):
        self.append(Note(pitch=pitch, duration=duration))

    # def get_at_tick(self, tick):
    #     duration = 0
    #     for note in self:
    #         if duration <= tick < duration + note.duration:
    #             return note
    #         duration += note.duration

    # def beats_since_last_rest(self, rest_duration=1):
    #     duration = 0.0
    #     for note in reversed(self):
    #         duration += note.duration
    #         if note.pitch is 'rest':
    #             if note.duration >= rest_duration:
    #                 break
    #     return duration

    # def get_last_pitched(self):
    #     for note in reversed(self):
    #         # Check if it's a note with a pitch (that can be 0, or a non-empty chord)
    #         if isinstance(note.pitch, int) or (isinstance(note.pitch, list) and note.pitch):
    #             return note


class Music(object):
    def __init__(self,
            title='Title',
            starting_tempo_bpm=60,
            part_names=None,
            output_dir_parent='output',
            output_dir_name='tmp',
        ):

        self.output_dir_parent = output_dir_parent
        self.output_dir_name = output_dir_name

        if part_names == None:
            part_names = (
                'violin',
                'flute',
                'oboe',
                'clarinet',
                'alto_saxophone',
                'trumpet',
                'bass',
                # 'percussion'
            )
        self.part_names = part_names

        self.title = title
        self.composer = 'Jonathan Marmor'
        self.time_signature = None
        self.starting_tempo_bpm = starting_tempo_bpm
        self.starting_tempo_quarter_duration = 1.0

        self._setup_parts()

    def _setup_parts(self):
        # Instantiate instruments/parts and make them accessible via Music
        self.instruments = []
        self.grid = {}
        self.part_ids = []
        for part_name in self.part_names:
            instrument = Instrument(part_name)
            self.part_ids.append(instrument.part_id)
            setattr(self, instrument.part_id, instrument)
            setattr(self, instrument.abbreviation_id, instrument)
            self.instruments.append(instrument)
            self.grid[instrument.part_id] = instrument

    # def print_registers(self):
    #     lowest = min([i.range[0] for i in self.instruments])
    #     highest = max([i.range[-1] for i in self.instruments])
    #     longest_name = max([len(i.part_id) for i in self.instruments])
    #     format_string = '{:<' + str(longest_name) + '}'

    #     header = ' ' * longest_name
    #     for pc in range(lowest, highest + 1):
    #         if pc % 2 == 0:
    #             header += str(pc)
    #         else:
    #             header += '  '
    #     print header

    #     for i in self.instruments:
    #         line = format_string.format(i.part_id)
    #         for pc in range(lowest, highest + 1):
    #             if pc in i.range:
    #                 line += '. '
    #             else:
    #                 line += '  '
    #         print line

    # def duration(self):
    #     return max(instrument.duration() for instrument in self.instruments)

    # def duration_seconds(self):
    #     n_beats = self.duration()
    #     beat_duration = 60.0 / self.starting_tempo_bpm
    #     duration = beat_duration * n_beats
    #     return duration

    # def get_at_tick(self, tick, instruments=None):
    #     if instruments == None:
    #         instruments = self.instruments
    #     result = {'tick': tick}
    #     for instrument in instruments:
    #         result[instrument.part_id] = instrument.get_at_tick(tick)
    #     return result

    # def __iter__(self):
    #     for tick in range(int(self.duration())):
    #         yield self.get_at_tick(tick)

    # def print_columns(self):
    #     print
    #     print self.title, 'by', self.composer
    #     header = '{:<16}'.format('tick')
    #     for part_id in self.part_ids:
    #         header += '{:<16}'.format(part_id)
    #     print header

    #     for notes in self:
    #         row = '{:<16}'.format(notes['tick'])
    #         for part_id in self.part_ids:
    #             if notes[part_id] == None:
    #                 pitch = 'None'
    #             else:
    #                 pitch = notes[part_id].pitch
    #             row += '{:<16}'.format(pitch)
    #         print row

    # def time_since_last_rest(self, instruments=None):
    #     if instruments == None:
    #         instruments = self.instruments

    #     beat_duration_seconds = 60.0 / self.starting_tempo_bpm  # TODO: this works only if bpm is in quarter notes

    #     result = {}
    #     for i in instruments:
    #         result[i.part_id] = i.beats_since_last_rest() * beat_duration_seconds

    #     return result

    def notate(self):
        self.notation = Notation(
            part_names=self.part_names,
            title=self.title,
            composer=self.composer,
            time_signature=self.time_signature,
            starting_tempo_bpm=self.starting_tempo_bpm,
            starting_tempo_quarter_duration=self.starting_tempo_quarter_duration,
            output_dir_parent=self.output_dir_parent,
            output_dir_name=self.output_dir_name,
        )

        for instrument in self.instruments:
            notation_instrument = self.notation.parts_by_name[instrument.part_name]
            for note in instrument:
                notation_instrument.add_note(note.pitch, note.duration)

        self.notation.show()

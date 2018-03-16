#!/usr/bin/env python

import math

import numpy as np

from notation_tools import Notation
from instrument_data import instrument_data
import utils
from duration import Duration


def float_to_tick(flt, ticks_per_quarter=24):
    return int(round(float(flt) * ticks_per_quarter))


class Tick(object):
    def __init__(self, offset, timings):
        self.offset = offset

        self.quarters_offset, self.sixteenths_offset, self.remaining_ticks_offset = timings

        self.note = None
        self.note_start = False
        self.note_end = False
        self.pitch = None


class Note(object):
    def __init__(self, duration, ticks, pitch=None):
        self.pitch = pitch
        self.duration = duration

        self.ticks = ticks

        self.ticks[0].note_start = True
        self.ticks[-1].note_end = True

        for tick in self.ticks:
            tick.note = self
            tick.pitch = self.pitch

    def __repr__(self):
        return '<Note - pitch: {} duration: {}>'.format(self.pitch, self.duration)


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

        self._timeline = [Tick(offset=tick, timings=self.ticks_to_quarters_and_sixteenths(tick)) for tick in range(self.n_ticks)]

    def __len__(self):
        return len(self._timeline)

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

    def fill(self, pitch, quarter, sixteenth=0, length_quarters=1, length_sixteenths=0):
        chunk = self.get(quarter, sixteenth=sixteenth, length_quarters=length_quarters, length_sixteenths=length_sixteenths)
        for tick in chunk:
            tick.pitch = pitch

    def check_if_clear(self, quarter, sixteenth=0, length_quarters=1, length_sixteenths=0):
        chunk = self.get(quarter, sixteenth=sixteenth, length_quarters=length_quarters, length_sixteenths=length_sixteenths)
        return all([tick.pitch == None for tick in chunk])

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


class Instrument(object):
    def __init__(self, part_name, n_quarters=64, ticks_per_quarter=24):
        self.notes = []
        self.timeline = Timeline(n_quarters=n_quarters, ticks_per_quarter=ticks_per_quarter)

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

    def add_note(self, pitch=None, duration=0.0):
        self.notes.append(Note(pitch=pitch, duration=duration))

    def put_note(self, start_offset, duration, pitch=None):
        # start_tick = float_to_tick(start_offset)
        # duration_in_ticks = float_to_tick(duration)

        start_tick = start_offset
        duration_in_ticks = duration

        ticks = self.timeline._timeline[start_tick:start_tick + duration_in_ticks]

        print 'len(ticks)', len(ticks)
        print 'len(self.timeline._timeline):', len(self.timeline._timeline)
        print 'duration:', duration

        note = Note(pitch=pitch, duration=Duration(flt=duration), ticks=ticks)

    def closeout(self):
        '''Put rests anywhere there aren't notes'''
        rest_ticks = []
        for i, tick in enumerate(self.timeline._timeline):
            if tick.note:
                if tick.note_start:
                    if rest_ticks:
                        # Add up the previous rest duration and append it to self.notes
                        duration_in_ticks = len(rest_ticks)
                        note = Note(duration=Duration(ticks=duration_in_ticks), ticks=rest_ticks)
                        self.notes.append(note)

                    self.notes.append(tick.note)
                if tick.note_end:
                    rest_ticks = []
            else:
                rest_ticks.append(tick)


class Music(object):
    def __init__(self,
            title='Title',
            starting_tempo_bpm=60,
            part_names=None,
            output_dir_parent='output',
            output_dir_name='tmp',
            n_quarters=64,
            ticks_per_quarter=24,
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

        self.n_quarters = n_quarters
        self.ticks_per_quarter = ticks_per_quarter

        self._setup_parts()

    def _setup_parts(self):
        # Instantiate instruments/parts and make them accessible via Music
        self.instruments = []
        self.grid = {}
        self.part_ids = []
        for part_name in self.part_names:
            instrument = Instrument(
                part_name,
                n_quarters=self.n_quarters,
                ticks_per_quarter=self.ticks_per_quarter
            )
            self.part_ids.append(instrument.part_id)
            setattr(self, instrument.part_id, instrument)
            setattr(self, instrument.abbreviation_id, instrument)
            self.instruments.append(instrument)
            self.grid[instrument.part_id] = instrument

    def print_registers(self):
        lowest = min([i.range[0] for i in self.instruments])
        highest = max([i.range[-1] for i in self.instruments])
        longest_name = max([len(i.part_id) for i in self.instruments])
        format_string = '{:<' + str(longest_name) + '}'

        header = ' ' * longest_name
        for pc in range(lowest, highest + 1):
            if pc % 2 == 0:
                header += str(pc)
            else:
                header += '  '
        print header

        for i in self.instruments:
            line = format_string.format(i.part_id)
            for pc in range(lowest, highest + 1):
                if pc in i.range:
                    line += '. '
                else:
                    line += '  '
            print line

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
            for note in instrument.notes:
                notation_instrument.add_note(note.pitch, note.duration.float)

        self.notation.show()

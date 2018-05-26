#!/usr/bin/env python

from notation_tools import Notation
from instrument_data import instrument_data
import utils


class Note(object):
    def __init__(self, duration, pitch=None):
        self.pitch = pitch
        self.duration = duration

    def __repr__(self):
        return '<Note - pitch: {} duration: {}>'.format(self.pitch, self.duration)


class Instrument(object):
    def __init__(self, part_name):
        self.notes = []
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
        return '<Instrument: {}>'.format(self.part_name)

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

    # def put_note(self, start_offset, duration, pitch=None):
    #     # start_tick = float_to_tick(start_offset)
    #     # duration_in_ticks = float_to_tick(duration)

    #     start_tick = start_offset
    #     duration_in_ticks = duration

    #     ticks = self.timeline._timeline[start_tick:start_tick + duration_in_ticks]

    #     # print 'len(ticks)', len(ticks)
    #     # print 'len(self.timeline._timeline):', len(self.timeline._timeline)
    #     # print 'duration:', duration

    #     note = Note(pitch=pitch, duration=Duration(ticks=duration), ticks=ticks)

    # def closeout(self):
    #     '''Put rests anywhere there aren't notes'''
    #     rest_ticks = []
    #     for i, tick in enumerate(self.timeline._timeline):
    #         if tick.note:
    #             if tick.note_start:
    #                 if rest_ticks:
    #                     # Add up the previous rest duration and append it to self.notes
    #                     duration_in_ticks = len(rest_ticks)
    #                     note = Note(duration=Duration(ticks=duration_in_ticks), ticks=rest_ticks)
    #                     self.notes.append(note)

    #                 self.notes.append(tick.note)
    #             if tick.note_end:
    #                 rest_ticks = []
    #         else:
    #             rest_ticks.append(tick)


class Piece(MusicBase):
    def __init__(self):
        self.part_names = (
            'oboe',
            'bass_clarinet',
            'vibraphone',
            'bass'
        )
        self.bpm = 105
        self.notation = Notation(
            part_names=self.part_names,
            title='Utah 2018 Work in Progress',
            composer='Jonathan Marmor',
            starting_tempo_bpm=self.bpm,
            output_dir_name='experiment11',
        )

        self._setup_parts()

        # MAKE NOTES HERE

        self.oboe.add_note(60, 1.0)
        self.oboe.add_note(62, 0.5)
        self.oboe.add_note(64, 0.5)
        self.oboe.add_note(65, 2.0)



        self._closeout_notation()

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

    def _closeout_notation(self):
        for instrument in self.instruments:
            notation_instrument = self.notation.parts_by_name[instrument.part_name]
            for note in instrument.notes:
                notation_instrument.add_note(note.pitch, note.duration)
        self.notation.show()


if __name__ == '__main__':
    Music()

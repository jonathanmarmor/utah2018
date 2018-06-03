#!/usr/bin/env python

from notation_tools import Notation
from instrument_data import instrument_data
from utils import split_list, flatten
from sections2 import Layers


class Note(object):
    def __init__(self, offset, duration, ticks, pitch=None):
        self.pitch = pitch

        self.offset = offset
        self.duration = duration
        self.next_offset = offset + duration

        self.ticks = ticks

        self.ticks[0].note_start = True
        self.ticks[-1].note_end = True

        for tick in self.ticks:
            tick.note = self
            tick.pitch = self.pitch

    def __repr__(self):
        return '<Note: offset: {} duration: {} pitch: {}>'.format(self.offset, self.duration, self.pitch)


class Instrument(object):
    def __init__(self, part_name, n_quarters=64):
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
        return '<music_tools.Instrument: {}>'.format(self.part_name)

    def _make_registers(self, n_chunks=7):
        self.lowest_note = self.range[0]
        self.highest_note = self.range[-1]

        self.registers = list(split_list(self.range, n_chunks=n_chunks))

        self.middle_register = self.registers[3]  # assuming 7 divisions
        self.highest_register = self.registers[-1]
        self.lowest_register = self.registers[0]
        self.safe_register = flatten(self.registers[1:-1])
        self.very_safe_register = flatten(self.registers[2:-2])

    def append_note(self, duration, pitch=None):
        self.notes.sort(key=lambda x: x.next_offset)
        last_note = self.notes[-1]
        self.put_note(last_note.next_offset, duration, pitch=pitch)

    def put_note(self, offset, duration, pitch=None):
        # offset and duration in quarter durations
        ticks = self.ticks.get(offset, duration)
        note = Note(offset, duration, ticks, pitch=pitch)
        self.notes.append(note)
        # self.notes.sort(key=lambda x: x.offset)  Probably too expensive to run every time

    def get(self, offset, duration=.25):
        '''Get all the notes in this instrument happening between offset and offset + duration, where both are quarter durations'''
        self.notes.sort(key=lambda x: x.offset)

        next_offset = offset + duration
        result = []
        for note in self.notes:
            if note.next_offset <= offset:
                continue
            if note.offset >= next_offset:
                break
            result.append(note)
        return result

    def find_openings(self, duration, window_offset=0, window_duration=None):
        if window_duration == None:
            window_duration = self.ticks.duration_quarters
        openings = []
        ticks = self.ticks.get(window_offset, window_duration)
        for tick in ticks:
            if not self.get(tick.offset, duration):
                openings.append(tick.offset)
        return openings

    def closeout(self):
        '''Put rests anywhere there aren't notes'''
        self.finalized_notes = []

        rest_ticks = []
        for tick in self.ticks:
            if tick.note:
                if tick.note_start:
                    if rest_ticks:
                        # Add up the previous rest duration and append it to self.finalized_notes
                        duration = sum([t.duration for t in rest_ticks])
                        note = Note(rest_ticks[0].offset, duration, rest_ticks)
                        self.finalized_notes.append(note)

                    self.finalized_notes.append(tick.note)
                if tick.note_end:
                    rest_ticks = []
            else:
                rest_ticks.append(tick)


class Music(object):
    def __init__(self,
            title='Title',
            bpm=60,
            part_names=None,
            output_dir_parent='output',
            output_dir_name='tmp',
            n_quarters=64,
        ):

        self.output_dir_parent = output_dir_parent
        self.output_dir_name = output_dir_name

        if part_names == None:
            part_names = (
                'oboe',
                'bass_clarinet',
                'vibraphone',
                'bass',
            )
        self.part_names = part_names

        self.title = title
        self.composer = 'Jonathan Marmor'
        self.time_signature = None
        self.bpm = bpm
        self.n_quarters = n_quarters

        self.layers = Layers(self.n_quarters, self.bpm)

        self._setup_parts()

    def _setup_parts(self):
        # Instantiate instruments/parts and make them accessible via Music
        self.instruments = []
        self.grid = {}
        self.part_ids = []
        for part_name in self.part_names:
            instrument = Instrument(part_name, n_quarters=self.n_quarters)

            self.part_ids.append(instrument.part_id)
            setattr(self, instrument.part_id, instrument)
            setattr(self, instrument.abbreviation_id, instrument)
            self.instruments.append(instrument)
            self.grid[instrument.part_id] = instrument

            instrument.ticks = self.layers.add_layer(instrument.part_id + '_ticks', self.layers.n_sixteenths)
            for tick in instrument.ticks:
                tick.note = None
                tick.note_start = False
                tick.note_end = False
                tick.pitch = None

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

    def closeout(self):
        for i in self.instruments:
            i.closeout()
        print 'Done making the music.'

    def notate(self):
        print 'Making notation...'
        self.notation = Notation(
            part_names=self.part_names,
            title=self.title,
            composer=self.composer,
            time_signature=self.time_signature,
            starting_tempo_bpm=self.bpm,
            starting_tempo_quarter_duration=1.0,
            output_dir_parent=self.output_dir_parent,
            output_dir_name=self.output_dir_name,
        )

        for instrument in self.instruments:
            notation_instrument = self.notation.parts_by_name[instrument.part_name]
            for note in instrument.finalized_notes:
                notation_instrument.add_note(note.pitch, note.duration)

        self.notation.show()
        print 'Done making notation.'

    def get(self, offset, duration=.25):
        return {i.part_id:i.get(offset, duration=duration) for i in self.instruments}

    def put_note(self, part_id, offset, duration, pitch=None):
        instrument = self.grid[part_id]
        instrument.put_note(offset, duration, pitch=pitch)

    def get_context(self, part_id, offset, duration):
        '''Get all the things that are happening relative to a duration in an instrument.

            - Notes being played by other instruments
            - Metrical layers
            - Other user-defined layers (e.g, form, harmonies, registers, etc)
        '''
        notes_context = self.get(offset, duration)
        layers_context = self.layers.get(offset, duration)

        pitches = []
        for inst in notes_context:
            if inst == part_id:
                continue
            for note in notes_context[inst]:
                if isinstance(note.pitch, (list, tuple)):
                    for p in note.pitch:
                        pitches.append(p)
                else:
                    pitches.append(note.pitch)
        pitches.sort()
        pitch_classes = sorted(list(set([p % 12 for p in pitches])))

        analysis = {
            'pitches': pitches,
            'pitch_classes': pitch_classes,
            # TODO: 'previous_note': , # previous note in this instrument
            # TODO: 'next_note': , # next note in this instrument

        }

        return notes_context, layers_context, analysis

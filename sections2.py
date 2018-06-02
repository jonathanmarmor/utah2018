import numpy as np

from utils import scale


def quarter_duration_to_ticks(quarter_duration, ticks_per_quarter=32):
    return int(quarter_duration * ticks_per_quarter)


class Section(object):
    def __init__(self, start, next_start, index, of_n_sections, parent):
        self.start = start
        self.next_start = next_start
        self.end = next_start - 1
        self.duration = next_start - start

        self.index = index
        self.of_n_sections = of_n_sections

        self.parent = parent

    def __repr__(self):
        return '<Section {} of {}, start: {}, duration: {}>'.format(
            self.index,
            self.of_n_sections,
            self.start,
            self.duration)


class Layer(list):
    def __init__(self, sections, n_ticks):
        """TODO: Put description here.

            `sections`:
                       If `sections` is an int, then equally divide `n_ticks` into
                       this number of sections
                       If `sections` is a list of ints or floats, divide `n_ticks`
                       into len(`sections`) number of sections with relative
                       durations matching the values in `sections`

            `n_ticks`: The total number of the smallest unit of duration in all
                       sequential sections combined. Eg, Length of audio in samples.


        """

        self.n_ticks = n_ticks

        if isinstance(sections, int):
            self.n_sections = sections
            self.starts = [int(round(start)) for start in np.linspace(0, self.n_ticks, self.n_sections, endpoint=False)]

        if isinstance(sections, (list, tuple)):
            self.n_sections = len(sections)
            self.relative_durations = sections
            self.sum_relative_durations = sum(sections)

            durations = [scale(duration, 0, self.sum_relative_durations, 0, self.n_ticks) for duration in sections]
            start = 0
            self.starts = []
            for duration in durations:
                self.starts.append(start)
                start += duration
            self.starts = [int(round(start)) for start in self.starts]

        self.next_starts = self.starts[1:] + [self.n_ticks + 1]

        index = 0
        for start, next_start in zip(self.starts, self.next_starts):
            section = Section(start, next_start, index, self.n_sections, self)
            self.append(section)
            index += 1

    def get(self, offset, duration=0.0, ticks_per_quarter=32):
        '''Get by quarter note duration offset'''
        ticks_offset = offset * ticks_per_quarter
        return self.get_by_ticks_offset(ticks_offset)

    def get_by_ticks_offset(self, ticks_offset):
        for section in self:
            if section.start <= ticks_offset < section.next_start:
                return section

    def get_in_window(self, offset, duration, ticks_per_quarter=32):
        '''Get all the Sections in this Layer happening between offset and offset + duration, where both are quarter durations'''
        start_tick = quarter_duration_to_ticks(offset, ticks_per_quarter=ticks_per_quarter)
        duration_ticks = quarter_duration_to_ticks(duration, ticks_per_quarter=ticks_per_quarter)

        return self.get_in_window_by_ticks(start_tick, duration_ticks)

    def get_in_window_by_ticks(self, offset, duration):
        next_start = offset + duration
        result = []
        for section in self:
            if section.next_start <= offset:
                continue
            if section.start >= next_start:
                break
            result.append(section)
        return result


class Layers(dict):
    def __init__(self, n_quarters, ticks_per_quarter, bpm):
        self.n_quarters = n_quarters
        self.ticks_per_quarter = ticks_per_quarter
        self.bpm = bpm

        self.n_ticks = n_quarters * ticks_per_quarter

        self.init_meter()


    def init_meter(self):
        self.quarter_duration_seconds = 60.0 / self.bpm
        self.bar_duration_seconds = self.quarter_duration_seconds * 4
        self.half_note_duration_seconds = self.quarter_duration_seconds * 2
        self.eighth_note_duration_seconds = self.quarter_duration_seconds / 2
        self.sixteenth_note_duration_seconds = self.quarter_duration_seconds / 4
        self.thirtysecond_note_duration_seconds = self.quarter_duration_seconds / 8

        self.n_bars = self.n_quarters / 4
        self.n_halves = self.n_quarters / 2
        self.n_eighths = self.n_quarters * 2
        self.n_sixteenths = self.n_quarters * 4
        self.n_thirtyseconds = self.n_quarters * 8

        self.duration = self.bar_duration_seconds * self.n_bars

        self.thirtyseconds = self.add_layer('thirtyseconds', self.n_thirtyseconds)
        self.sixteenths = self.add_layer('sixteenths', self.n_sixteenths)
        self.eighths = self.add_layer('eighths', self.n_eighths)
        self.quarters = self.add_layer('quarters', self.n_quarters)
        self.halves = self.add_layer('halves', self.n_halves)
        self.bars = self.add_layer('bars', self.n_bars)

        # self.metrical_hierarchy = self.add_layer

    def get(self, offset, duration=0.0):
        return {layer_name:self[layer_name].get(offset, duration=duration) for layer_name in self}

    def add_layer(self, name, sections):
        self[name] = Layer(sections, self.n_ticks)

    def get_in_window(self, offset, duration, ticks_per_quarter=32):
        return {layer_name:self[layer_name].get_in_window(offset, duration, ticks_per_quarter=ticks_per_quarter) for layer_name in self}

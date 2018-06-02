'''Layers and Sections

# from sections2 import Layers

>>> layers = Layers(n_quarters=16, bpm=60)
>>> layers.add_layer('harmonies', [3, 1] * 4)
>>> layers.add_layer('equal', 32)
>>> layers.quarter_duration_seconds
1.0
>>> layers.get(offset=0)
{'bars': [<Section 0 of 4, offset: 0, duration: 0.25>],
 'eighths': [<Section 0 of 32, offset: 0, duration: 0.25>],
 'equal': [<Section 0 of 32, offset: 0, duration: 0.25>],
 'halves': [<Section 0 of 8, offset: 0, duration: 0.25>],
 'harmonies': [<Section 0 of 8, offset: 0, duration: 12.0>],
 'quarters': [<Section 0 of 16, offset: 0, duration: 0.25>],
 'sixteenths': [<Section 0 of 64, offset: 0, duration: 0.25>]}
>>> layers.get(12.25)

'''

import numpy as np

from utils import scale


class Section(object):
    def __init__(self, offset, duration, index, of_n_sections, parent):
        self.offset = offset
        self.duration = duration
        self.next_offset = offset + duration

        self.index = index
        self.of_n_sections = of_n_sections

        self.parent = parent

    def __repr__(self):
        return '<Section {} of {}, offset: {}, duration: {}>'.format(
            self.index,
            self.of_n_sections,
            self.offset,
            self.duration)


class Layer(list):
    def __init__(self, sections, duration_quarters):
        """
            `sections`:
                       If `sections` is an int, then equally divide `n_ticks` into
                       this number of sections
                       If `sections` is a list of ints or floats, divide `n_ticks`
                       into len(`sections`) number of sections with relative
                       durations matching the values in `sections`

            `duration_quarters`: the duration of the layer in quarter durations

        """

        self.duration_quarters = float(duration_quarters)

        if isinstance(sections, int):
            self.n_sections = sections
            self.durations = [self.duration_quarters / self.n_sections] * self.n_sections
            self.relative_durations = [1] * self.n_sections
            self.sum_relative_durations = self.n_sections

        elif isinstance(sections, (list, tuple)):
            self.n_sections = len(sections)
            self.relative_durations = sections
            self.sum_relative_durations = sum(sections)
            self.durations = [scale(duration, 0, self.sum_relative_durations, 0, self.duration_quarters) for duration in sections]

        offset = 0
        index = 0
        for duration in self.durations:
            section = Section(offset, duration, index, self.n_sections, self)
            self.append(section)
            offset += duration
            index += 1

    def get(self, offset, duration=.25):
        '''Get all the Sections in this Layer happening between offset and offset + duration, where both are quarter durations'''
        next_offset = offset + duration
        result = []
        for section in self:
            if section.next_offset <= offset:
                continue
            if section.offset >= next_offset:
                break
            result.append(section)
        return result


class Layers(dict):
    def __init__(self, n_quarters, bpm):
        self.n_quarters = n_quarters
        self.bpm = bpm
        self.init_meter()

    def init_meter(self):
        self.quarter_duration_seconds = 60.0 / self.bpm
        self.bar_duration_seconds = self.quarter_duration_seconds * 4
        self.half_note_duration_seconds = self.bar_duration_seconds / 2
        self.eighth_note_duration_seconds = self.bar_duration_seconds / 8
        self.sixteenth_note_duration_seconds = self.bar_duration_seconds / 16
        # self.thirtysecond_note_duration_seconds = self.bar_duration_seconds / 32

        self.n_bars = self.n_quarters / 4
        self.n_halves = self.n_bars * 2
        self.n_eighths = self.n_bars * 8
        self.n_sixteenths = self.n_bars * 16
        # self.n_thirtyseconds = self.n_bars * 32

        self.duration_seconds = self.bar_duration_seconds * self.n_bars

        # self.add_layer('thirtyseconds', self.n_thirtyseconds)
        self.add_layer('sixteenths', self.n_sixteenths)
        self.add_layer('eighths', self.n_eighths)
        self.add_layer('quarters', self.n_quarters)
        self.add_layer('halves', self.n_halves)
        self.add_layer('bars', self.n_bars)
        self.meter_layers = [self.bars, self.halves, self.quarters, self.eighths, self.sixteenths]

    def add_layer(self, name, sections):
        self[name] = Layer(sections, self.n_quarters)
        setattr(self, name, self[name])
        return self[name]

    def get(self, offset, duration=0.25, layer_name=None):
        if layer_name:
            return self[layer_name].get(offset, duration)
        return {layer_name:self[layer_name].get(offset, duration) for layer_name in self}


if __name__ == '__main__':
    import doctest
    doctest.testmod()

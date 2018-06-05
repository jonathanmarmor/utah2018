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
    def __init__(self, offset, duration, index, of_n_sections, parent, relative_duration=None):
        self.offset = offset
        self.duration = duration
        self.next_offset = offset + duration

        self.index = index
        self.of_n_sections = of_n_sections

        self.parent = parent
        self.relative_duration = relative_duration

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
            section = Section(
                offset,
                duration,
                index,
                self.n_sections,
                self,
                relative_duration=self.relative_durations[index],
            )
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()

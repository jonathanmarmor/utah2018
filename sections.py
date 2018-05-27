"""Usage

import numpy as np

from marimba_samples import Marimba
from audio import Audio

marimba = Marimba()
audio_duration_seconds = 120
audio = Audio(audio_duration_seconds)
len_audio = len(audio)

layer_1 = Sections(4, len_audio)
layer_2 = Sections([1, 1, 2, 1, 1, 2], len_audio)

offsets = [int(round(o)) for o in np.linspace(0, len_audio, 16, endpoint=False)]
for offset in offsets:
    layer_1_index = layer_1.get_by_sample_offset(offset).index
    layer_2_index = layer_2.get_by_sample_offset(offset).index
    print offset, layer_1_index, layer_2_index

"""


import numpy as np

from utils import scale


class Section(object):
    def __init__(self, start, next_start, index, of_n_sections, sections):
        self.start = start
        self.next_start = next_start
        self.end = next_start - 1
        self.duration = self.end - self.start

        self.index = index
        self.of_n_sections = of_n_sections

        self.parent = sections

    def __repr__(self):
        return '<Section {} of {}, start: {}, duration: {}>'.format(
            self.index,
            self.of_n_sections,
            self.start,
            self.duration)


class Sections(list):
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

    def get_by_sample_offset(self, sample_offset):
        for section in self:
            if section.start <= sample_offset < section.next_start:
                return section


# class Layers(object):
#     def __init__(self, ):


#     def get_by_sample_offset(self, sample_offset):
#         return = [layer.get_by_sample_offset(sample_offset) for layer in self._layers]


# class Music(object):
#     def __init__(self):
#         self.form = Layers()
#         self.meter = Layers()

#!/usr/bin/env python

import argparse

from instrument_data import instrument_data
# from music_tools import Music


class Instrument(object):
    def __init__(self, instrument_name):
        data = instrument_data[instrument_name]




class Breath(object):
    def __init__(self):
        sounding_duration =
        resting_duration =



class Simulation(object):
    def __init__(self):




# class Movement1(object):
#     def __init__(self):
#         self.stats = self.init_stats()
#         m = self.music = Music(
#             part_names=(
#                 'oboe',
#                 'guitar',
#             ),
#             starting_tempo_bpm=105
#         )
#         beat_duration = 60.0 / self.music.starting_tempo_bpm

#         self.go()

#     def notate(self):
#         self.music.notate()




# def command_line_interface():
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         '-d',
#         '--dont-notate',
#         help='dont generate notation',
#         action="store_true")
#     return parser.parse_args()


# if __name__ == '__main__':
#     args = command_line_interface()

#     m1 = Movement1()
#     if not args.dont_notate:
#         m1.notate()
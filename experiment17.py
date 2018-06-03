#!/usr/bin/env python

import random

from music_tools3 import Music


def pick_duration_and_bpm(min_seconds=10, max_seconds=12, min_bpm=40, max_bpm=180):
    min_seconds = 135
    max_seconds = 160
    target_duration_seconds = random.randint(min_seconds, max_seconds + 1)

    min_bpm = 90
    max_bpm = 125
    bpm = random.randint(min_bpm, max_bpm + 1)

    bar_duration_seconds = (60.0 / bpm) * 4
    n_quarters = int(target_duration_seconds / bar_duration_seconds) * 4

    return bpm, n_quarters


bpm, n_quarters = pick_duration_and_bpm(
    min_seconds=135,
    max_seconds=160,
    min_bpm=90,
    max_bpm=125,
)

m = Music(
    title='Listen/Space 2018',
    part_names=[
        'oboe',
        'bass_clarinet',
        'vibraphone',
        'bass',
    ],
    bpm=90,
    output_dir_name='experiment17',
    n_quarters=8,
)

oboe = m.oboe
bass_clarinet = m.bass_clarinet
vibes = m.vibraphone
bass = m.bass

m.put_note('oboe', 0, 2, 60)
m.put_note('bass_clarinet', 0, 2, 64)
vibes.put_note(1, 1, [67, 70])


m.closeout()
m.notate()

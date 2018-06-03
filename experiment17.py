#!/usr/bin/env python

import random

import numpy as np

from music_tools3 import Music
from utils import round_to_sixteenth


def pick_duration_and_bpm(min_seconds=10, max_seconds=12, min_bpm=40, max_bpm=180):
    target_duration_seconds = random.randint(min_seconds, max_seconds + 1)
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
    bpm=bpm,
    output_dir_name='experiment17',
    n_quarters=n_quarters,
)

oboe = m.oboe
bass_clarinet = m.bass_clarinet
vibes = m.vibraphone
bass = m.bass

sixteenths = m.layers.sixteenths
eighths = m.layers.eighths
quarters = m.layers.quarters
halves = m.layers.halves
bars = m.layers.bars


chord_types = [
    {0, 4, 7},
    {0, 3, 7},
    {0, 5, 7},
    {0, 4, 7, 10},
    {0, 3, 7, 10},
]


failures = 0
for progress in range(500):
    print
    print 'progress', progress
    duration = random.choice(np.linspace(.25, 3.0, 12))

    inst = random.choice(m.instruments)
    openings = inst.find_openings(duration, window_offset=0, window_duration=None)

    if not openings:
        failures += 1
        if failures > 100:
            break
        continue

    offset = random.choice(openings)

    notes_context, layers_context, analysis = m.get_context(inst.part_id, offset, duration)

    existing_harmony = analysis['pitch_classes']

    if not existing_harmony:
        print 'no harmony'
        inst.put_note(offset, duration, pitch=random.choice(inst.safe_register))
        continue

    print 'existing_harmony', existing_harmony

    pitch_class_options = []
    for pc in range(12):
        proposed_harmony = sorted(list(set(existing_harmony + [pc])))
        proposed_harmony_type = set([p - proposed_harmony[0] for p in proposed_harmony])
        if any([proposed_harmony_type.issubset(chord_type) for chord_type in chord_types]):
            pitch_class_options.append(pc)
    pitch_class_options.sort()
    print 'pitch_class_options', pitch_class_options
    pitch_options = [p for p in inst.safe_register if p % 12 in pitch_class_options]
    if pitch_class_options:
        inst.put_note(offset, duration, pitch=random.choice(pitch_options))

m.closeout()
m.notate()

#!/usr/bin/env python

import random

import numpy as np

from music_tools3 import Music
from utils import round_to_sixteenth, flatten


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
    output_dir_name='experiment18',
    n_quarters=n_quarters,
)

oboe = m.oboe
bass_clarinet = m.bass_clarinet
vibes = m.vibraphone
bass = m.bass

sixteenths = m.sixteenths
eighths = m.eighths
quarters = m.quarters
halves = m.halves
bars = m.bars


chord_types = [
    (0,),
    (0, 4),
    (0, 8),
    (0, 5),
    (0, 7),
    (0, 4, 7),
    (0, 3, 8),
    (0, 5, 9),
    (0, 3, 7),
    (0, 4, 9),
    (0, 5, 8),
    (0, 5, 7),
    (0, 2, 7),
    (0, 5, 10),
    (0, 4, 7, 10),
    (0, 3, 6, 8),
    (0, 3, 5, 9),
    (0, 2, 6, 9),
    (0, 3, 7, 10),
    (0, 4, 7, 9),
    (0, 3, 5, 8),
    (0, 2, 5, 9),
]


instrument_register = {
    'oboe': flatten(oboe.registers[-2:-1]),
    'bass_clarinet': flatten(bass_clarinet.registers[1:3]),
    'vibraphone': flatten(vibes.registers[2:-2]),
    'bass': flatten(bass.registers[4:-1]),
}

fragment = {
    'oboe': [],
    'bass_clarinet': [],
    'vibraphone': [],
    'bass': [],
}


def make_rhythm(quarters=8):
    failures = 0
    density = random.randint(14, 29)
    for progress in range(density):
        # TODO: separate into clearly divided phases of generating candidates,
        #       ranking the candidates, and choosing from the ranked candidates

        duration = random.choice([.5, .5, 1.0, 1.0, 1.0, 1.5, 2.0])

        staccato = False
        if duration == .5 and random.random() < 1.0 / 3:
            staccato = True

        inst = random.choice(m.instruments)

        openings = inst.find_openings(
            duration,
            window_offset=0,
            window_duration=8,
        )

        openings = [o for o in openings if o % .5 == 0]

        if not openings:
            failures += 1
            if failures > 100:
                print 'failure x100'
                break
            continue

        offset = random.choice(openings)

        notes_context, layers_context, analysis = m.get_context(inst.part_id, offset, duration)

        existing_harmony = analysis['pitch_classes']

        if not existing_harmony:
            # print 'no harmony'
            pitch = random.choice(instrument_register[inst.part_id])
            # fragment[inst.part_id].append((offset, duration, pitch, staccato))
            inst.put_note(offset, duration, pitch=pitch, staccato=staccato)
            continue

        pitch_class_options = []
        for pc in range(12):
            proposed_harmony = sorted(list(set(existing_harmony + [pc])))
            proposed_harmony_type = tuple([p - proposed_harmony[0] for p in proposed_harmony])
            if proposed_harmony_type in chord_types:
                pitch_class_options.append(pc)
        pitch_class_options.sort()

        pitch_options = [p for p in instrument_register[inst.part_id] if p % 12 in pitch_class_options]
        if pitch_options:
            pitch = random.choice(pitch_options)
            inst.put_note(offset, duration, pitch=pitch, staccato=staccato)
            # fragment[inst.part_id].append((offset, duration, pitch, staccato))


make_rhythm()


for instrument in m.instruments:
    temp = instrument.notes[:]
    for note in temp:
        offsets = [8, 16, 24]
        for offset in offsets:
            instrument.put_note(note.offset + offset, note.duration, pitch=note.pitch, staccato=note.staccato)

'''
TODO:
- Instead of writing directly to the instruments, put the rhythm in a list or dict or something then add it to the music repeatedly.
-
'''

m.closeout()
m.notate()

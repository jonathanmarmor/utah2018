#!/usr/bin/env python

import random
import itertools

import numpy as np

from music_tools3 import Music
from utils import round_to_sixteenth, flatten


# def pick_duration_and_bpm(min_seconds=10, max_seconds=12, min_bpm=40, max_bpm=180):
#     target_duration_seconds = random.randint(min_seconds, max_seconds + 1)
#     bpm = random.randint(min_bpm, max_bpm + 1)
#     bar_duration_seconds = (60.0 / bpm) * 4
#     n_quarters = int(target_duration_seconds / bar_duration_seconds) * 4
#     return bpm, n_quarters


# bpm, n_quarters = pick_duration_and_bpm(
#     min_seconds=135,
#     max_seconds=160,
#     min_bpm=90,
#     max_bpm=125,
# )

bpm = 93
n_quarters = 232


m = Music(
    title='Listen/Space 2018',
    part_names=[
        'oboe',
        'bass_clarinet',
        'vibraphone',
        'bass',
    ],
    bpm=bpm,
    n_quarters=n_quarters,
    output_dir_name='experiment19',
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


section_durations = [1, 4, 4, 4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 1]
section_types = [
    'intro',
    'verse_a',
    'verse_a',
    'verse_b',
    'verse_a',
    'chorus',
    'verse_a',
    'verse_b',
    'chorus',
    'bridge',
    'verse_a',
    'verse_b',
    'chorus',
    'chorus',
    'outro',
]

form = m.add_layer('form', section_durations)
for section, section_type in zip(form, section_types):
    section.section_type = section_type





chord_types = [
    (),
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
    'bass': [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58],
    'bass_clarinet': [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60],
    'oboe': [76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88],
    'vibraphone': [58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73],
}


def make_form():
    form_sections = []

    intro_duration = random.choice([0, 1, 1, 1, 1, 2, 2, 3]) * 4
    if intro_duration:
        intro_offset = 0
        form_sections.append((intro_offset, intro_duration, 'intro'))

    outro_duration = random.choice([0, 1, 1, 1, 1, 2, 2, 3]) * 4
    if outro_duration:
        outro_offset = m.n_quarters - outro_duration
        form_sections.append((outro_offset, outro_duration, 'outro'))

    # Golden mean of the piece duration should happen during the bridge
    golden_ratio = 1.6180339631667064
    golden_mean_offset = round_to_sixteenth(m.n_quarters / golden_ratio)

    golden_mean_bar = m.get_sections(golden_mean_offset, layer_name='bars')[0]

    bridge_duration = random.choice([4, 8]) * 4

    earliest_offset = int(golden_mean_bar.offset - bridge_duration + 4)
    latest_offset = int(golden_mean_bar.offset + 4)
    bridge_offset_options = range(earliest_offset, latest_offset, 4)
    bridge_offset = random.choice(bridge_offset_options)
    form_sections.append((bridge_offset, bridge_duration, 'bridge'))


    duration_from_intro_to_bridge = bridge_offset - intro_duration

    duration_from_bridge_to_outro = m.n_quarters - bridge_offset - bridge_duration - outro_duration

    # chorus



    n_choruses_before_bridge = random.choice([1, 2, 2, 2, 2, 3, 3, 4])
    n_choruses_after_bridge = random.choice([0, 1, 1, 1, 1, 2])

    chorus_duration = random.choice([2, 4]) * 4

    # TODO: pick chorus offsets


    # Verses
    n_verses = random.choice([1, 2, 2, 2, 2, 3, 3, 4])

    for verse in range(n_verses):




    form_sections.sort(key=lambda x: x[0])
    form = m.add_layer('form', form_sections)
    form_section_types = [s[-1] for s in form_sections]
    for section, section_type in zip(form, form_section_types):
        setattr(section, 'section_type', section_type)






def make_fragment(n_quarters=8):
    fragment = Music(
        title='Fragment',
        part_names=[
            'oboe',
            'bass_clarinet',
            'vibraphone',
            'bass',
        ],
        bpm=bpm,
        n_quarters=8,
        output_dir_name='fragment',
    )

    failures = 0
    density = random.randint(14, 29)
    for progress in range(density):
        # TODO: separate into clearly divided phases of generating candidates,
        #       ranking the candidates, and choosing from the ranked candidates

        duration = random.choice([.5, .5, 1.0, 1.0, 1.0, 1.5, 2.0])

        staccato = False
        if duration == .5 and random.random() < 1.0 / 3:
            staccato = True

        inst = random.choice(fragment.instruments)

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

        notes_context, layers_context, analysis = fragment.get_context(inst.part_id, offset, duration)

        existing_harmony = analysis['pitch_classes']

        if not existing_harmony:
            # print 'no harmony'
            pitch = random.choice(instrument_register[inst.part_id])
            fragment.grid[inst.part_id].put_note(offset, duration, pitch=pitch, staccato=staccato)
            # inst.put_note(offset, duration, pitch=pitch, staccato=staccato)
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
            # inst.put_note(offset, duration, pitch=pitch, staccato=staccato)
            fragment.grid[inst.part_id].put_note(offset, duration, pitch=pitch, staccato=staccato)

    fragment.closeout()

    return fragment


def get_good_variations(fragment):
    good_variations = []

    transpositions = [-2, -1, 0, 1, 2]
    for instrument_transpositions in itertools.product(transpositions, repeat=4):

        # Skip if it's just a transposition of all the instruments the same interval
        if all(x == instrument_transpositions[0] for x in instrument_transpositions):
            continue

        fragment_v2 = Music(
            title='Fragment V2',
            part_names=[
                'oboe',
                'bass_clarinet',
                'vibraphone',
                'bass',
            ],
            bpm=bpm,
            n_quarters=8,
            output_dir_name='fragment_v2',
        )

        for original_inst, new_instrument, transposition in zip(fragment.instruments, fragment_v2.instruments, instrument_transpositions):
            for note in original_inst.finalized_notes:
                pitch = None
                if note.pitch != None:
                    pitch = note.pitch + transposition

                new_instrument.put_note(note.offset, note.duration, pitch=pitch, staccato=note.staccato)

        fragment_v2.closeout()

        # Test if the new variation meets some criteria (eg, only uses allowed harmonies)
        goods = []
        for sixteenth in fragment_v2.sixteenths:

            # Test if the harmony at this sixteenth note moment in time is in chord_types
            moment = fragment_v2.get(sixteenth.offset, .25)

            pitchclasses = []
            for inst_name in moment:
                notes = moment[inst_name]
                for note in notes:  # always going to be 0 or 1, I think
                    if note and note.pitch != None:
                        pitchclasses.append(note.pitch % 12)
            pitchclasses = list(set(pitchclasses))
            pitchclasses.sort()
            pitchclasses = tuple([p - pitchclasses[0] for p in pitchclasses])

            if pitchclasses in chord_types:
                good = True
            else:
                good = False
            goods.append(good)

        if all(goods):
            print instrument_transpositions
            good_variations.append(fragment_v2)

    return good_variations


def main():

    while m.
    fragment = make_fragment(n_quarters)

    good_variations = get_good_variations(fragment)

    print 'Good variations:', len(good_variations)

    if len(good_variations) < 1:
        return

    # instrument_register = {
    #     'oboe': flatten(oboe.registers[-2:-1]),
    #     'bass_clarinet': flatten(bass_clarinet.registers[1:3]),
    #     'vibraphone': flatten(vibes.registers[2:-2]),
    #     'bass': flatten(bass.registers[4:-1]),
    # }


    for instrument in fragment.instruments:
        for note in instrument.finalized_notes:
            offsets = [0, 8, 16, 24]
            for offset in offsets:
                m.grid[instrument.part_id].put_note(note.offset + offset, note.duration, pitch=note.pitch, staccato=note.staccato)


    global_offset = 0
    for variation in good_variations:
        global_offset += 32
        for instrument in variation.instruments:
            for note in instrument.finalized_notes:
                offsets = [0, 8, 16, 24]
                for offset in offsets:
                    m.grid[instrument.part_id].put_note(note.offset + offset + global_offset, note.duration, pitch=note.pitch, staccato=note.staccato)


    m.closeout()
    m.notate()


if __name__ == '__main__':
    main()

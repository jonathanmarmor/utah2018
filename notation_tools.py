import datetime
import os

import music21

from instrument_data import instrument_data


def show(stream):
    stream.show('musicxml', '/Applications/MuseScore 2.app')
    # stream.show('musicxml', '/Applications/Sibelius 7.app')


def get_music21_user_settings_path():
    user_settings = music21.environment.UserSettings()
    return user_settings.getSettingsPath()


def print_music21_user_settings():
    for key in sorted(music21.environment.keys()):
        try:
            value = music21.environment.get(key)
        except music21.environment.EnvironmentException:
            value = ''
        print '{:<25} {}'.format(key, value)


instrument_classes = {
    'violin': music21.instrument.Violin,
    'flute': music21.instrument.Flute,
    'oboe': music21.instrument.Oboe,
    'clarinet': music21.instrument.Clarinet,
    'alto_saxophone': music21.instrument.Saxophone,
    'trumpet': music21.instrument.Trumpet,
    'bass': music21.instrument.Bass,
    'percussion': music21.instrument.Percussion,
    'english_horn': music21.instrument.EnglishHorn,
    'alto_recorder': music21.instrument.Recorder,
    'soprano_recorder': music21.instrument.Recorder,
    'baritone_saxophone': music21.instrument.BaritoneSaxophone,
    'guitar': music21.instrument.Guitar,
}

for name in instrument_data:
    instrument_data[name]['class'] = instrument_classes[name]


def parse_part_name(part_name):
    instrument_name = part_name
    instrument_number = 1
    if ' ' in part_name:
        name_chunks = part_name.split(' ')
        instrument_name = ' '.join(name_chunks[:-1])
        instrument_number = int(name_chunks[-1])  # if more than one of the same instrument
    return instrument_name, instrument_number


def make_music21_score(
            part_names=(
                'violin',
                'flute',
                'oboe',
                'clarinet',
                'alto_saxophone',
                'trumpet',
                'bass',
                'percussion'
            ),
            title='Title',
            composer='Jonathan Marmor',
            time_signature=None,
            starting_tempo_bpm=60,
            starting_tempo_quarter_duration=1.0
        ):
    timestamp = datetime.datetime.utcnow()
    metadata = music21.metadata.Metadata()
    metadata.title = title
    metadata.composer = composer
    metadata.date = timestamp.strftime('%Y/%m/%d')

    score = music21.stream.Score()
    score.insert(0, metadata)

    parts = []  # Unnecessary?
    for part_name in part_names:

        instrument_name, instrument_number = parse_part_name(part_name)

        instrument = instrument_data[instrument_name]

        part = music21.stream.Part()

        metronome_mark = music21.tempo.MetronomeMark(
            number=starting_tempo_bpm,
            referent=music21.duration.Duration(starting_tempo_quarter_duration)
        )
        part.append(metronome_mark)

        if time_signature:
            # Should be a string like '12/8'
            music21_time_signature = music21.meter.TimeSignature(time_signature)
            part.append(music21_time_signature)

        m21_instrument = instrument['class']()
        m21_instrument.partName = instrument['name']
        m21_instrument.partAbbreviation = instrument['abbreviation']

        if instrument_number > 1:
            m21_instrument.partName = '{} {}'.format(instrument['name'], instrument_number)
            m21_instrument.partAbbreviation = '{} {}'.format(instrument['abbreviation'], instrument_number)

        part.insert(0, m21_instrument)

        clef = instrument.get('clef')
        if clef:
            part.append(clef())

        parts.append(part)  # Unnecessary?
        score.insert(0, part)

    return score


def make_music21_note(pitch_number=None, duration=1.0):
    if pitch_number == None or pitch_number == 'rest':
        n = music21.note.Rest()
    elif isinstance(pitch_number, list):
        pitches = [music21.pitch.Pitch(p) for p in pitch_number]
        for p in pitches:
            if p.accidental.name is 'natural':
                p.accidental = None
        n = music21.chord.Chord(pitches)
    else:
        p = music21.pitch.Pitch(pitch_number)
        if p.accidental.name is 'natural':
            p.accidental = None
        n = music21.note.Note(p)

    d = music21.duration.Duration()
    d.quarterLength = duration
    n.duration = d

    return n


class Instrument(object):
    """A clean in interface to a music21 part and instrument"""
    def __init__(self, part_name, music21_part):
        self.part_name = part_name
        self.instrument_name, self.instrument_number = parse_part_name(part_name)

        self._music21_part = music21_part

        self.range = instrument_data[self.instrument_name]['range']

    def add_note(self, pitch=None, duration=None):
        m21_note = make_music21_note(pitch, duration)
        self._music21_part.append(m21_note)


class Notation(object):
    """A clean interface to a music21 score"""
    def __init__(
            self,
            part_names=('oboe', 'bass'),
            title='Title',
            composer='Jonathan Marmor',
            time_signature=None,
            starting_tempo_bpm=60,
            starting_tempo_quarter_duration=1.0
        ):

        # Set up temp file directory
        music21.environment.set('directoryScratch', 'output/tmp')

        # if temporary directory doesn't exist, create it
        if not os.path.isdir('output/tmp'):
            if not os.path.isdir('tmp'):
                os.mkdir('output')
            os.mkdir('output/tmp')

        self.part_names = part_names

        # Make Music21 Score, Parts, and Instruments
        self._score = make_music21_score(
            part_names=part_names,
            title=title,
            composer=composer,
            time_signature=time_signature,
            starting_tempo_bpm=starting_tempo_bpm,
            starting_tempo_quarter_duration=starting_tempo_quarter_duration,
        )

        # Instantiate parts and instruments and make them accessible via Notation
        self.instruments = []
        self.parts_by_name = {}
        for part_name, music21_part in zip(self.part_names, self._score.parts):
            instrument = Instrument(part_name, music21_part)
            setattr(self, part_name, instrument)
            self.instruments.append(instrument)
            self.parts_by_name[part_name] = instrument

    def show(self):
        show(self._score)

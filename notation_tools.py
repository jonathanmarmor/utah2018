import datetime
import os

from music21 import environment
from music21.metadata import Metadata
from music21.stream import Score, Part
from music21.tempo import MetronomeMark
from music21.duration import Duration
from music21.meter import TimeSignature
from music21.note import Rest, Note
from music21.pitch import Pitch
from music21.chord import Chord
from music21.instrument import (
    Violin,
    Flute,
    Oboe,
    Clarinet,
    BassClarinet,
    Saxophone,
    Trumpet,
    Bass,
    Percussion,
    EnglishHorn,
    Recorder,
    BaritoneSaxophone,
    Guitar,
    Organ,
    Piano,
    Vibraphone,
)
from music21.articulations import (
    Staccato,
    Tenuto,

    Accent,

    Falloff,  # An indeterminantSlide coming after the main note and going down.
    Plop,     # An indeterminantSlide coming before the main note and going down.
    Scoop,    # An indeterminantSlide coming before the main note and going up
    Doit,     # An indeterminantSlide coming after the main note and going up.

    BreathMark,
)

from instrument_data import instrument_data


def which_notation_app():
    sibelius = '/Applications/Sibelius 7.app'
    muse_score = '/Applications/MuseScore 2.app'
    if os.path.exists(sibelius):
        # Prefer Sibelius
        return sibelius
    elif os.path.exists(muse_score):
        return muse_score
    else:
        raise Exception('Neither Sibelius nor MuseScore is installed')


def show(stream):
    notation_app = which_notation_app()
    stream.show('musicxml', notation_app)


def get_music21_user_settings_path():
    user_settings = environment.UserSettings()
    return user_settings.getSettingsPath()


def print_music21_user_settings():
    for key in sorted(environment.keys()):
        try:
            value = environment.get(key)
        except environment.EnvironmentException:
            value = ''
        print '{:<25} {}'.format(key, value)


instrument_classes = {
    'violin': Violin,
    'flute': Flute,
    'oboe': Oboe,
    'clarinet': Clarinet,
    'bass_clarinet': BassClarinet,
    'alto_saxophone': Saxophone,
    'trumpet': Trumpet,
    'bass': Bass,
    'percussion': Percussion,
    'english_horn': EnglishHorn,
    'alto_recorder': Recorder,
    'soprano_recorder': Recorder,
    'baritone_saxophone': BaritoneSaxophone,
    'guitar': Guitar,
    'organ': Organ,
    'piano': Piano,
    'vibraphone': Vibraphone,
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
            starting_tempo_quarter_duration=1.0,
            timestamp=None,
        ):
    if not timestamp:
        timestamp = datetime.datetime.utcnow()
    metadata = Metadata()
    metadata.title = title
    metadata.composer = composer
    metadata.date = timestamp.strftime('%Y/%m/%d')

    score = Score()
    score.insert(0, metadata)

    for part_name in part_names:

        instrument_name, instrument_number = parse_part_name(part_name)

        instrument = instrument_data[instrument_name]

        part = Part()

        metronome_mark = MetronomeMark(
            number=starting_tempo_bpm,
            referent=Duration(starting_tempo_quarter_duration)
        )
        part.append(metronome_mark)

        if time_signature:
            # Should be a string like '12/8'
            music21_time_signature = TimeSignature(time_signature)
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

        score.insert(0, part)

    return score


def make_music21_note(
        pitch_number=None,
        duration=1.0,
        staccato=False,
        tenuto=False,
        accent=False,
        falloff=False,
        plop=False,
        scoop=False,
        doit=False,
        breath_mark=False,
    ):
    if pitch_number == None or pitch_number == 'rest':
        n = Rest()
    elif isinstance(pitch_number, list):
        pitches = [Pitch(p) for p in pitch_number]
        for p in pitches:
            if p.accidental.name is 'natural':
                p.accidental = None
        n = Chord(pitches)
    else:
        p = Pitch(pitch_number)
        if p.accidental.name is 'natural':
            p.accidental = None
        n = Note(p)

    d = Duration()
    d.quarterLength = duration
    n.duration = d

    if staccato:
        n.articulations.append(Staccato())
    if tenuto:
        n.articulations.append(Tenuto())
    if accent:
        n.articulations.append(Accent())
    if falloff:
        n.articulations.append(Falloff())
    if plop:
        n.articulations.append(Plop())
    if scoop:
        n.articulations.append(Scoop())
    if doit:
        n.articulations.append(Doit())
    if breath_mark:
        n.articulations.append(BreathMark())

    return n


class Instrument(object):
    """A clean in interface to a music21 part and instrument"""
    def __init__(self, part_name, music21_part):
        self.part_name = part_name
        self.instrument_name, self.instrument_number = parse_part_name(part_name)

        self._music21_part = music21_part

        self.range = instrument_data[self.instrument_name]['range']

    def add_note(
            self,
            pitch=None,
            duration=None,
            staccato=False,
            tenuto=False,
            accent=False,
            falloff=False,
            plop=False,
            scoop=False,
            doit=False,
            breath_mark=False,
        ):
        m21_note = make_music21_note(
            pitch,
            duration,
            staccato=staccato,
            tenuto=tenuto,
            accent=accent,
            falloff=falloff,
            plop=plop,
            scoop=scoop,
            doit=doit,
            breath_mark=breath_mark,
        )
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
            starting_tempo_quarter_duration=1.0,
            output_dir_parent='output',
            output_dir_name='tmp',
        ):

        self.timestamp = timestamp = datetime.datetime.utcnow()

        self.output_dir_parent = output_dir_parent
        self.output_dir_name = output_dir_name
        self.create_output_dir()

        self.part_names = part_names

        # Make Music21 Score, Parts, and Instruments
        self._score = make_music21_score(
            part_names=part_names,
            title=title,
            composer=composer,
            time_signature=time_signature,
            starting_tempo_bpm=starting_tempo_bpm,
            starting_tempo_quarter_duration=starting_tempo_quarter_duration,
            timestamp=self.timestamp,
        )

        # Instantiate parts and instruments and make them accessible via Notation
        self.instruments = []
        self.parts_by_name = {}
        for part_name, music21_part in zip(self.part_names, self._score.parts):
            instrument = Instrument(part_name, music21_part)
            setattr(self, part_name, instrument)
            self.instruments.append(instrument)
            self.parts_by_name[part_name] = instrument

    def create_output_dir(self):
        self.output_dir = os.path.join(self.output_dir_parent, self.output_dir_name)

        # if temporary directory doesn't exist, create it
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Set up temp file directory
        environment.set('directoryScratch', self.output_dir)

    def show(self):
        show(self._score)

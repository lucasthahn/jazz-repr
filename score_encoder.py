import os
import sys
import music21
import numpy as np
import pandas as pd

from music21.interval import notesToChromatic
from harmony_tools import scale_matcher

START_POS = 8
NUM_QUALITIES = 8

def chord_symbol_remover(i):
    """Filter to remove chord symbols from a score."""

    return not isinstance(el,music21.harmony.ChordSymbol)

def interval_to_int(inputInterval):
    """Convert music21 interval to integer."""
    result = ""
    inputInterval = str(inputInterval)

    # Need to start at START_POS to not catch the '21' in 'music21'
    for i in inputInterval[START_POS:]:
        if i.isdigit():
            result = result + i

    return int(result)

def different_octaves(n1, n2):
    """Returns true if the n1 and n2 not in same octave."""
    lower = interval_to_int(notesToChromatic(n1, n2)) < 0
    higher = interval_to_int(notesToChromatic(n1, n2)) > 11

    return lower or higher

def lower_octave(n1, n2):
    """Returns true if n1 is in a lower octave than n2."""
    return interval_to_int(notesToChromatic(n1, n2)) < 0

def higher_octave(n1, n2):
    """Returns true if n1 is in a higher octave than n2."""
    return interval_to_int(notesToChromatic(n1, n2)) > 11

def get_scale_degree(chord, note):
    """Gives the scale degree of a chord relative to some chord."""

    root = chord.root()

    if type(note) == music21.note.Note:

        if different_octaves(root, note):
            octave = 3
            octave_name = str(octave)
            note_name = note.name
            note = music21.note.Note(note_name + octave_name)

            # Search so that we're invariant to octaves
            while different_octaves(root, note):

                if lower_octave(root, note):
                    octave += 1
                    octave_name = str(octave)
                    note = music21.note.Note(note_name + octave_name)

                elif higher_octave(root, note):
                    octave -= 1
                    octave_name = str(octave)
                    note= music21.note.Note(note_name + octave_name)

        chrom_int = music21.interval.notesToChromatic(root, note)

        return interval_to_int(chrom_int)


    else:
        raise NotImplementedError

def read_vocab(vocab_file):
    """Get array of all possible chords (for encoding)."""

    chord_list = []
    vocab_file = open(vocab_file, 'r')
    chords = vocab_file.readlines()

    for chord in chords:
        chord = music21.harmony.ChordSymbol(chord.strip())
        chord_list.append(chord)

    vocab_file.close()

    return chord_list

def max_pitch(infile):
    """Calculate highest pitch in an input file."""

    infile = music21.converter.parse(infile)
    iterator = in_file.recurse().notes.iter
    iterator.addFilter(chord_symbol_remover)
    notes = iterator

    max_pitch = -np.inf

    for note in notes:

        if type(note) == music21.chord.Chord:
            top_note = note.pitches[len(note.pitches)-1] > max_pitch
            if top_note > max_pitch:
                max_pitch = top_note

        elif type(note) == music21.note.Note:
            if note > max_pitch:
                max_pitch = note

    return max_pitch

def min_pitch(infile):
    """Calculate lowest pitch in an input file."""

    infile = music21.converter.parse(infile)
    iterator = in_file.recurse().notes.iter
    iterator.addFilter(chord_symbol_remover)

    min_pitch = np.inf

    for note in iterator:

        if type(note) == music21.chord.Chord:
            top_note = note.pitches[len(note.pitches)-1] < max_pitch
            if top_note < max_pitch:
                max_pitch = top_note

        elif type(note) == music21.note.Note:
            if note < max_pitch:
                max_pitch = note

    return max_pitch

def total_range(infile):
    """Range from lowest to highest note (for one-hot encoding)."""

    n1 = min_pitch(infile)
    n2 = max_pitch(infile)

    return music21.interval.notesToChromatic(n1,n2)

def get_length_in_beats(infile):
    """Length of a score (in sixteenth notes)."""

    iterator = infile.recurse().notes.iter
    iterator.addFilter(chord_symbol_remover)

    length = 0

    for note in iterator:
        length += note.quarterLength

    return round(length * 4)

def get_repr(infile):
    """Encode a score into matrix representation."""

    infile = music21.converter.parse(infile)
    iterator = infile.recurse().notes.iter
    iterator.addFilter(chord_symbol_remover)
    chords = read_vocab('chords')

    # Matrix has N columns, where N is the length of the score in 16th notes
    tot_length = get_length_in_beats(infile)
    deg_arr =  np.zeros(tot_length)
    chord_arr = np.zeros(tot_length)
    midi_arr = np.zeros(tot_length)
    note_arr0 = np.zeros(tot_length)
    note_arr1 = np.zeros(tot_length)
    note_arr2 = np.zeros(tot_length)

    curr = 0
    prev = 0

    for note in iterator:

        deg = 0
        length = 0
        curr_chord = 0

        if note.getContextByClass('ChordSymbol') != None:
            curr_chord = note.getContextByClass('ChordSymbol')

            # Randomly sample three consonant notes
            safe_notes = np.array(scale_matcher(curr_chord))
            sampled_notes = np.random.choice(safe_notes, 3)

            if type(note) == music21.note.Note:
                curr += int(note.quarterLength * 4)
                deg = get_scale_degree(curr_chord, note)

                for i in range(prev, curr):
                    deg_arr[i] = deg  # Scale degree representation
                    chord_arr[i] = chords.index(curr_chord)  # Chord encoding
                    midi_arr[i] = note.pitch.midi  # Absolute pitch (MIDI)
                    note_arr0[i] = sampled_notes[0].pitch.midi
                    note_arr1[i] = sampled_notes[1].pitch.midi
                    note_arr2[i] = sampled_notes[2].pitch.midi

            elif type(note) == music21.note.Rest:
                curr += int(note.quarterLength * 4)
                chord_arr[i] = chords.index(curr_chord)

        else:
            raise NotImplementedError

        prev = curr

    trim_ind = 0

    # Remove trailing blank space from the score
    for i in reversed(range(tot_length)):
        if deg_arr[i] + chord_arr[i] != 0:
            trim_ind = i+1
            break

    deg_arr = deg_arr[0:trim_ind]
    chord_arr = chord_arr[0:trim_ind]
    midi_arr = midi_arr[0:trim_ind]
    note_arr0 = note_arr0[0:trim_ind]
    note_arr1 = note_arr1[0:trim_ind]
    note_arr2 = note_arr2[0:trim_ind]

    return np.vstack((chord_arr, deg_arr, midi_arr, note_arr0, note_arr1, note_arr2))

def transpose_chord(chord, steps):
    """Transpose a given chord up by a given number of half steps."""

    chords = read_vocab('chords')

    new_chord = chord + (steps * NUM_QUALITIES)
    if new_chord > len(chords):
        new_chord = new_chord % len(chords) - 1

    r1 = chords[int(chord)][0]
    r2 = chords[int(new_chord)][0]

    # Don't get tripped up by enharmonics
    if r1.pitch.ps == r2.pitch.ps:
        new_chord += NUM_QUALITIES
        if new_chord > len(chords):
            new_chord = new_chord % len(chords) - 1

    return new_chord

def transpose_deg(deg, steps):
    """Transpose a degree up by given number of steps."""

    return (deg + steps) % 11

def transpose_repr(repr, n):
    """Tranpose a score representation up by n semitones."""

    vec_chords = np.vectorize(transpose_chord, otypes=[int], cache=False)
    vec_degs = np.vectorize(transpose_deg, otypes=[int], cache=False)

    new_chords = vec_chords(repr[0], n)
    new_degs = vec_degs(repr[1], n)
    new_midi = repr[2] + n
    new_note0 = repr[3] + n
    new_note1 = repr[4] + n
    new_note2 = repr[5] + n

    return np.vstack((new_chords, new_degs, new_midi))

if __name__ == '__main__':

    ind = 0
    files = []
    basenames = os.listdir('parker')

    for f in basenames:
        files.append('parker/' + f)

    for i, f in enumerate(files):
        name = 'data/' + str(ind) + '.h5'

        try:
            mat = get_repr(f)
            cols = list(range(mat.shape[1]))
            df = pd.DataFrame(mat, columns=cols)
            df.to_hdf(name, key="df", mode="w")
            ind += 1

            mat = transpose_repr(mat, np.random.randint(0, 12))
            cols = list(range(mat.shape[1]))
            df = pd.DataFrame(mat, columns=cols)
            name = 'data/' + str(ind) + '.h5'
            df.to_hdf(name, key="df", mode="w")
            ind += 1

        except ValueError:
            continue

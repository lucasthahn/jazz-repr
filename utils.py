import os
import mido
import torch
import numpy as np
import matplotlib.pyplot as plt

from music21 import midi
from IPython.display import Audio, display

N = 3  # Number of attributes
M = 32  # Two measures worth of sixteenth notes
R = 128  # Total range in Charlie Parker dataset

class Solo:

    def __init__(self, arr):

        self.arr = arr.copy()

        reshaped = self.arr.reshape(-1)
        self.one_hot = np.zeros((N*M, R))

        r = np.arange(N*M)
        self.one_hot[r, reshaped] = 1
        self.one_hot = self.one_hot.reshape(M, N, R)

    def play(self, filename='midi_track.mid'):
        # display an in-notebook widget for playing audio
        # saves the midi file as a file named name in base_dir/midi_files

        midi_arr = self.arr.transpose().copy()
        midi = piano_roll_to_midi(midi_arr)
        midi.save('midi_files/' + filename)
        play_midi('midi_files/' + filename)

def piano_roll_to_midi(piece):

    piece = np.concatenate([piece, [[np.nan, np.nan, np.nan]]], axis=0)

    bpm = 50
    microseconds_per_beat = 60 * 1000000 / bpm

    mid = mido.MidiFile()
    tracks = {'melody': mido.MidiTrack()}
    past_pitches = {'melody': np.nan}
    delta_time = {'melody': 0}

    metatrack = mido.MidiTrack()
    metatrack.append(mido.MetaMessage('set_tempo',
                                      tempo=int(microseconds_per_beat),
                                      time=0))


    mid.tracks.append(tracks['melody'])
    mid.tracks.append(metatrack)

    tracks['melody'].append(mido.Message(
        'program_change', program=52, time=0))

    for i in range(len(piece)):
        pitches = {'melody': piece[i, 2]}
        if np.isnan(past_pitches['melody']):
            past_pitches['melody'] = None
        if np.isnan(pitches['melody']):
            pitches['melody'] = None

        if pitches['melody'] != past_pitches['melody']:

            if past_pitches['melody']:
                tracks['melody'].append(mido.Message('note_off',
                                                  note=int(past_pitches['melody']),
                                                  velocity=64,
                                                  time=delta_time['melody']))
                delta_time['melody'] = 0

            if pitches['melody']:
                tracks['melody'].append(mido.Message('note_on',
                                                  note=int(pitches['melody']),
                                                  velocity=64,
                                                  time=delta_time['melody']))

        past_pitches['melody'] = pitches['melody']
        delta_time['melody'] += 120

    return mid

def play_midi(midifile):

    mf = midi.MidiFile()
    mf.open(midifile)
    mf.read()
    mf.close()
    s = midi.translate.midiFileToStream(mf)
    s.show('midi')

def harmonize(y, C, model):

    model.eval()

    with torch.no_grad():
        x = y
        C2 = C.copy()
        num_steps = int(2*N*M)
        alpha_max = .999
        alpha_min = .001
        eta = 3/4

        for i in range(num_steps):

            p = np.maximum(alpha_min, alpha_max - i*(alpha_max-alpha_min)/(eta*num_steps))
            sampled_binaries = np.random.choice(2, size = C.shape, p=[p, 1-p])
            C2 += sampled_binaries
            C2[C==1] = 1

            x_cache = x
            x = model.pred(x, C2)
            x[C2==1] = x_cache[C2==1]
            C2 = C.copy()

        return x

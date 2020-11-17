# CocoNet Music Generation

## Installation

Install `miniconda` using Homebrew:

```console
brew install --cask miniconda
conda init <shell-name>
```

Activate the environment

```console
make install
conda activate jazz
```

## Directory Structure

The code for feature extraction lives in `score_encoder.py`, and the script
for training the model is in `train.py`.

To generate some examples, use `JazzRepr.ipynb`:

```console
jupyter notebook JazzRepr.ipynb
```

Right now you have to specify what chord every sixteenth-note is within a
2-bar phrase. The codes for the chords can be found in the file `chords` and
the indexing starts from 0 (sorry this will get better!)

Right now, the chord progression is a simple ii-V-I in the key of C major (so
Dm7 -> G7 -> Cmaj7)

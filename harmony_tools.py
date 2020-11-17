import music21

SCALE_LENGTH = 7 # Regular scales
LONG_SCALE_LENGTH = 8 # Diminished scales (half-whole and whole-half)
START_POS = 8

ROOT = 0
SECOND = 1
THIRD = 2
FOURTH = 3
FIFTH = 4
SIXTH = 5
SEVENTH = 6

def interval_to_int(input_interval):

    result = ""
    input_interval = str(input_interval)
    for i in inputInterval[START_POS:]: # Read after the "21" in "music21"
        if i.isdigit():
            result = result + i
    return int(result)

def scale_matcher(chord):

    key_root = chord.root()
    chord_kind = chord.commonName

    if (chord_kind == 'major triad'):
        return ionian(key_root)
    elif (chord_kind == 'minor triad'):
        return aeolian(key_root)
    elif (chord_kind == 'major seventh chord'):
        return lydian(key_root) + ionian(key_root)
    elif (chord_kind == 'minor seventh chord'):
        return dorian(key_root) + aeolian(key_root)
    elif (chord_kind == 'half-diminished seventh chord'):
        return locrian(key_root)
    elif (chord_kind == 'flat-ninth pentachord'):
        return half_whole(key_root)
    elif (chord_kind == 'dominant seventh chord'):
        return myxolydian(key_root)
    elif (chord_kind == 'quartal trichord'):
        return myxolydian(key_root)
    elif (chord_kind == 'augmented major tetrachord'):
        return melodic_min(key_root.transpose('M6'))
    elif (chord_kind == 'Neapolitan pentachord'):
        return half_whole(key_root)
    elif (chord_kind == 'tritone quartal tetrachord'):
        return half_whole(key_root)

def ionian(key):

    current_note = music21.note.Note(key)

    result = []
    count = 0

    while count < SCALE_LENGTH:
        result.append(current_note)
        if count != SECOND:
            current_note = current_note.transpose('M2')
        else:
            current_note = current_note.transpose('m2')
        count += 1

    return result

def aeolian(key):

    current_note = music21.note.Note(key)
    result = []
    count = 0

    while count < SCALE_LENGTH:
        result.append(current_note)
        if count == SECOND or count == FIFTH:
            current_note = current_note.transpose('m2')
        else:
            current_note = current_note.transpose('M2')
        count += 1

    return result

def dorian(key):

    current_note = music21.note.Note(key)
    result = []
    count = 0

    while count < SCALE_LENGTH:
        result.append(current_note)
        if count == SECOND or count == SIXTH:
            current_note = current_note.transpose('m2')
        else:
            current_note = current_note.transpose('M2')
        count += 1

    return result

def phrygian(key):

    current_note = music21.note.Note(key)
    result = []
    count = 0

    while count < SCALE_LENGTH:
        result.append(current_note)
        if count == ROOT or count == FIFTH:
            currentNote = currentNote.transpose('m2')
        else:
            currentNote = currentNote.transpose('M2')
        count += 1

    return result

def lydian(key):

    current_note = music21.note.Note(key)
    result = []
    count = 0

    while count < SCALE_LENGTH:
        result.append(current_note)
        if count == FOURTH:
            current_note = current_note.transpose('m2')
        else:
            current_note = current_note.transpose('M2')
        count += 1

    return result

def myxolydian(key):

    current_note = music21.note.Note(key)
    result = []
    count = 0

    while count < SCALE_LENGTH:
        result.append(current_note)
        if count == THIRD or count == SIXTH:
            current_note = current_note.transpose('m2')
        else:
            current_note = current_note.transpose('M2')
        count += 1

    return result

def locrian(key):

    current_note = music21.note.Note(key)
    result = []
    count = 0

    while count < SCALE_LENGTH:
        result.append(current_note)
        if count == ROOT or count == FOURTH:
            current_note = current_note.transpose('m2')
        else:
            current_note = current_note.transpose('M2')
        count += 1

    return result

def half_whole(keyInput):

    current_note = music21.note.Note(key)
    result = []
    count = 0

    while count < LONG_SCALE_LENGTH:
        result.append(current_note)
        if count % 2 == 0:
            current_note = current_note.transpose('m2')
        else:
            current_note = current_note.transpose('M2')
        count += 1

    return result

def whole_half(key):

    current_note = music21.note.Note(key)
    result = []
    count = 0

    while count < LONG_SCALE_LENGTH:
        result.append(current_note)
        if count % 2 == 0:
            current_note = current_note.transpose('M2')
        else:
            current_note = current_note.transpose('m2')
        count +=1

    return result

def harm_min(key):

    current_note = music21.note.Note(key)
    result = []
    count = 0

    while count < SCALE_LENGTH:
        result.append(currentNote)
        if count == SECOND or count == FOURTH:
            currentNote = currentNote.transpose('m2')

        elif count == SIXTH:
            currentNote = currentNote.transpose('a2')

        else:
            currentNote = currentNote.transpose('M2')

        count += 1

    return result

def melod_min(key):

    current_note = music21.note.Note(key)
    result = []
    count = 0

    while count < SCALE_LENGTH:
        result.append(current_note)
        if count == SECOND:
            current_note = current_note.transpose('m2')

        else:
            current_note = current_note.transpose('M2')

        count += 1

    return result

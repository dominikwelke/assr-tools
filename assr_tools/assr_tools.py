from __future__ import print_function, unicode_literals, division
from sys import platform
import math
import numpy as np
from scipy.io import wavfile
import random
from psychopy import visual, event, data, core, prefs
prefs.general['audioLib'] = ['pyo'] if (platform is 'win32') else ['pygame']
from psychopy import sound


def generate_assr_wav(duration, att, carrier_frequ, am_frequ=0, rise=0.01, smplrate=44100., type='SAM'):

    length = int(duration * smplrate)

    # fader to avoid glitch-artefacts
    len_fade = int(rise*smplrate)
    fader = np.ones(length)
    fader[-len_fade:] = (np.cos(np.linspace(0, np.pi, len_fade))+1)/2
    fader[0:len_fade] = (np.cos(np.linspace(-np.pi, 0, len_fade))+1)/2

    # set loudness
    attenuation = math.pow(10, (-att/20.0))

    # amplitude modulation
    if am_frequ != 0:
        am_factor = float(am_frequ) * (math.pi * 2) / smplrate
        amplitude_mod = (np.sin(np.arange(length) * am_factor) + 1) / 2.
    else:
        amplitude_mod = np.ones(length)

    # construct assr
    if type == 'SAM':
        # constant sine wave
        cf_factor = float(carrier_frequ) * (math.pi * 2.) / float(smplrate)
        carrier_tone = np.sin(np.arange(length) * cf_factor)
        assr_tone = carrier_tone*attenuation*amplitude_mod
    elif type == 'beats':
        cf_factor1 = float(carrier_frequ - am_frequ) * (math.pi * 2.) / float(smplrate)
        carrier_tone1 = np.sin(np.arange(length) * cf_factor1)
        cf_factor2 = float(carrier_frequ + am_frequ) * (math.pi * 2.) / float(smplrate)
        carrier_tone2 = np.sin(np.arange(length) * cf_factor2)
        assr_tone = (0.5*carrier_tone1+0.5*carrier_tone2)*attenuation
    # elif type == 'AM_white':
    # elif type == 'AM_pink':
    else:  # treat as path to wav file
        fs, dat = wavfile.read(type)
        if fs == smplrate:
            assr_tone = dat[0:length]*attenuation
        else:
            print('ERROR')
    return assr_tone*fader


class AudiThreshold:
    """
    in:
        "mode" - staircase mode. either
            'simple' - starting at -100dB, participant uses 'up' and 'down' to define threshhold
            '2afc' - 2-alternative-forced-choice. in development
    """
    def __init__(self, win, mode, assr_type, am_frequency=40., carr_frequency=2000., smplrate=44100., known_threshold=[], verbose=False):
        self.win = win
        self.mode = mode
        self.carr_frequency = carr_frequency
        self.am_frequency = am_frequency
        self.smplrate = smplrate
        self.type = assr_type
        self.behavioral_threshold = known_threshold
        self.verbose = verbose

        # stimuli
        self.fixation = visual.TextStim(
            self.win, height=20,
            pos=(0, 0), text='+'
        )
        self.message_start_1 = visual.TextStim(
            self.win, height=20, pos=(0, 20),
            alignHoriz='center', alignVert='bottom',
            text='Bestimmung Ihrer Hoerschwelle'
        )
        self.message_start_2 = visual.TextStim(
            self.win, height=20, pos=(0, -20),
            alignHoriz='center', alignVert='bottom',
            text='Druecken Sie eine beliebige Taste, um zu beginnen'
        )


    def get_auditory_threshold(self):
        """
        main function to be called for an auditory perceptional threshold estimation
        v1

        in:
        "mode" - staircase mode. either
            'simple' - starting at -100dB, participant uses 'up' and 'down' to define threshhold
            '2afc' - 2-alternative-forced-choice. in development
        """
        # import numpy as np
        # import pylab

        # display instructions and wait
        self.message_start_1.draw()
        self.message_start_2.draw()
        self.win.mouseVisible = False
        self.win.flip()  # to show our newly drawn 'stimuli'
        # pause until there's a keypress
        event.waitKeys()

        # start procedure
        # create the staircase handler
        staircase = data.StairHandler(startVal=-100,
                                      nUp=1, nDown=1,
                                      stepType='lin',
                                      stepSizes=[8, 4, 4, 2, 2, 1, 1, 1],
                                      nReversals=7, nTrials=1)

        for thisIncrement in staircase:
            # set location of stimuli
            print('%i dB' % -thisIncrement)
            info = visual.TextStim(self.win, pos=[0, +300], text='lauter: [up] leiser: [down]')

            wav = generate_assr_wav(0.2, -thisIncrement,
                                    self.carr_frequency, self.am_frequency, 0.01, 44100., self.type)
            tone = sound.Sound(value=wav, secs=1)

            if self.mode == 'simple':
                self.fixation.draw()
                info.draw()
                self.win.flip()
                event.clearEvents()  # must clear other (eg mouse) events - they clog the buffer

                # v1
                # draw all stimuli
                tone.play()
                # get response
                this_response = None
                while this_response is None:
                    all_keys = event.getKeys(['up', 'down', 'escape'])
                    if len(all_keys) > 0:
                        print(all_keys)
                    for thisKey in all_keys:
                        if thisKey == 'up':
                            this_response = 0  # incorrect
                        elif thisKey == 'down':
                            this_response = 1
                        elif thisKey == 'escape':
                            core.quit()  # abort experiment
            elif self.mode == '2afc':
                # fixation.draw()
                # win.flip()
                event.clearEvents()  # must clear other (eg mouse) events - they clog the buffer

                # v2
                flip = random.random() < 0.5
                pos1 = visual.TextStim(self.win, pos=[0, +3], text='left')
                pos2 = visual.TextStim(self.win, pos=[0, +3], text='right')
                # draw all stimuli
                if flip:
                    self.fixation.draw()
                    pos1.draw()
                    self.win.flip()
                    tone.play()
                    core.wait(1)

                    self.win.flip()
                    core.wait(.5)

                    self.fixation.draw()
                    pos2.draw()
                    self.win.flip()
                    core.wait(1)

                    self.win.flip()
                    core.wait(.5)
                else:
                    self.fixation.draw()
                    pos1.draw()
                    self.win.flip()
                    core.wait(1)

                    self.win.flip()
                    core.wait(.5)

                    self.fixation.draw()
                    pos2.draw()
                    self.win.flip()
                    tone.play()
                    core.wait(1)

                    self.win.flip()
                    core.wait(.5)

                # get response
                this_response = None
                while this_response is None:
                    all_keys = event.getKeys(['left', 'right', 'escape'])
                    if len(all_keys) > 0:
                        print(all_keys)
                    for thisKey in all_keys:
                        if thisKey == 'left':
                            this_response = 1 if flip else 0  # 0 = incorrect
                        elif thisKey == 'right':
                            this_response = 0 if flip else 1
                        elif thisKey == 'escape':
                            core.quit()  # abort experiment

            # add the data to the staircase so it can calculate the next level
            staircase.addResponse(this_response)

        result = np.average(staircase.reversalIntensities[-3:])

        # end routine
        self.behavioral_threshold = result
        if self.verbose:
            print('OUTPUT:')
            print(self.behavioral_threshold)
        # pylab.plot(frequencies, results, 'o-')
        # pylab.show()

        return self.behavioral_threshold

    def construct_stimulus(self, duration, loudness):
        """ creates a psychopy.sound.Sound stimulus of a loudness relative to behavioral threshold """
        att = -int(self.behavioral_threshold) - loudness
        print(att)
        wav = generate_assr_wav(duration, att, self.carr_frequency, self.am_frequency, 0.01, 44100., self.type)

        stimulus = sound.Sound(value=wav, secs=duration, sampleRate=int(self.smplrate))
        if self.verbose:
            print('OUTPUT:')
            print(stimulus)
        return stimulus

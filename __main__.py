import os

os.system('clear')
os.system('tset')
print('Slot Race Console is loading!')

import random, time, threading, datetime, string, sys, inflect, serial, json

from enum import unique, IntEnum
from pyfiglet import Figlet
from curtsies import *
from curtsies.fmtfuncs import *


# utility functions
def conditional_sleep(s, i=float(1 / 60), condition=True):
    global RUNNING
    try:
        num_sleeps = int(s / i)
        while condition and num_sleeps > 0 and RUNNING:
            time.sleep(i)
            num_sleeps -= 1
    except ZeroDivisionError:
        pass


# classes
class Game:
    @unique
    class State(IntEnum):
        CANCELED = -3
        PREGAME = -2
        SETUP = -1
        COUNTDOWN = 0
        PLAYING = 1
        FINISHED = 2

    @unique
    class Mode(IntEnum):
        UNSPECIFIED = 0
        LAPS = 1
        FASTEST = 2

    def __init__(self):
        self.num_laps = 3
        self.p1name = 'P1'
        self.p2name = 'P2'
        self.state = Game.State.PREGAME
        self.mode = Game.Mode.UNSPECIFIED
        self.player_1_wins = None
        self.lane_1_correction = 0
        self.lane_2_correction = 0
        self.lane_1_raw_count = 0
        self.lane_2_raw_count = 0

    @property
    def lane_1_count(self):
        return self.lane_1_raw_count - self.lane_1_correction

    @property
    def lane_2_count(self):
        return self.lane_2_raw_count - self.lane_2_correction

    def reset_counts(self):
        self.lane_1_correction = self.lane_1_raw_count
        self.lane_2_correction = self.lane_2_raw_count


class PromptRequest:
    @unique
    class Mode(IntEnum):
        INT = 0
        TEXT = 1
        LOWER = 2
        UPPER = 3
        KEY_OPTIONS = 4
        MIXED = 5

    def __init__(self, prompt, name, mode=Mode.TEXT, options: dict = None):
        self.result = None
        self.entry = ''
        self.name = name
        self.mode = mode
        self.options = options
        self.mode_char_sets = {
            PromptRequest.Mode.INT: string.digits,
            PromptRequest.Mode.TEXT: string.ascii_letters,
            PromptRequest.Mode.MIXED: string.digits + string.ascii_letters,
            PromptRequest.Mode.UPPER: string.ascii_uppercase,
            PromptRequest.Mode.LOWER: string.ascii_lowercase
        }
        self.prompt = prompt + f'({self.mode.name.capitalize() if self.mode != PromptRequest.Mode.KEY_OPTIONS else ", ".join([f"{k}: {v.name}" for k, v in self.options.items()])}' \
                               f'{" " + repr(self.options["range"]) if self.mode == PromptRequest.Mode.INT and self.options is not None else ""})'
        self.display = self.prompt

    def on_loop(self, c):
        if self.result is None:
            if c == '<BACKSPACE>':
                if len(self.entry) > 0:
                    self.entry = self.entry[:-1]
            elif c in ['<Ctrl-j>', '<PADENTER>'] and self.mode != PromptRequest.Mode.KEY_OPTIONS:
                if self.entry == '':
                    return
                if self.mode == PromptRequest.Mode.INT:
                    self.entry = int(self.entry)
                    if self.mode == PromptRequest.Mode.INT and self.options is not None:
                        if self.entry not in self.options['range']:
                            self.entry = ''
                            self.display = self.prompt + ' ' + str(self.entry)
                            return
                self.result = self.entry
            if self.mode == PromptRequest.Mode.KEY_OPTIONS:
                if c in self.options:
                    self.entry += c
                    if self.mode == PromptRequest.Mode.KEY_OPTIONS:
                        self.result = self.options[self.entry]
            else:
                if c in self.mode_char_sets[self.mode]:
                    self.entry += c
                    if type(self.options) is dict:
                        if 'length' in self.options:
                            if len(self.entry) > self.options['length']:
                                self.entry = self.entry[:self.options['length']]
            self.display = self.prompt + ' ' + str(self.entry)


# loop funcs
def serial_stuff():
    global GAME, RUNNING

    delay = 5

    ser = serial.Serial('/dev/ttyACM0', timeout=0.1)
    raw = ""

    last1 = GAME.lane_1_raw_count
    last2 = GAME.lane_2_raw_count

    last1time = time.time()
    last2time = time.time()

    while RUNNING:
        ser.write(b'B')
        raw = ser.readline().decode("utf-8").split(' ')

        now = time.time()

        if raw:
            try:
                if raw:
                    last1 = GAME.lane_1_raw_count
                    last2 = GAME.lane_2_raw_count

                    GAME.lane_1_raw_count = int(raw[0])
                    GAME.lane_2_raw_count = int(raw[1])

                    if GAME.lane_1_raw_count > last1:
                        diff1 = GAME.lane_1_raw_count - last1
                        if now > (last1time + delay):
                            GAME.lane_1_correction += diff1 - 1
                            last1time = now
                        else:
                            GAME.lane_1_correction += diff1

                    if GAME.lane_2_raw_count > last2:
                        diff2 = GAME.lane_2_raw_count - last2
                        if now > (last2time + delay):
                            GAME.lane_2_correction += diff2 - 1
                            last2time = now
                        else:
                            GAME.lane_2_correction += diff2

            except ValueError:
                pass

    ser.close()


def input_processing():
    global RUNNING, GAME, RESTART, PROMPT_REQUESTS, PROMPT_RESPONSES
    with Input() as input_generator:
        for c in input_generator:
            if c == '<ESC>':
                RUNNING = False
                RESTART = False
                break
            elif c == '<F5>':
                RUNNING = False
                RESTART = True
                break
            elif len(PROMPT_REQUESTS) > 0:
                prompting = PROMPT_REQUESTS[0]
                prompting.on_loop(c)
                if prompting.result is not None:
                    PROMPT_RESPONSES[prompting.name] = prompting.result
                    PROMPT_REQUESTS.remove(prompting)
            elif c == '<SPACE>':
                if GAME.state == GAME.State.PREGAME:
                    if all(response_n in PROMPT_RESPONSES for response_n in ['p1name', 'p2name', 'laps', 'game_mode']):
                        GAME.state = GAME.State.SETUP
                    else:
                        PROMPT_RESPONSES = dict(
                            p1name='p 1',
                            p2name='p 2',
                            laps=1,
                            game_mode=1
                        )
                else:
                    GAME.state = GAME.State.CANCELED
            elif c in ['<Ctrl-j>', '<PADENTER>']:
                if GAME.state == GAME.State.PREGAME:
                    GAME.state = GAME.State.SETUP
                    PROMPT_REQUESTS = [
                        PromptRequest("Select Gamemode", "game_mode", mode=PromptRequest.Mode.KEY_OPTIONS,
                                      options=dict(l=Game.Mode.LAPS)),
                        PromptRequest("How many Laps?", "laps", mode=PromptRequest.Mode.INT,
                                      options=dict(range=range(1, 25), length=3)),
                        PromptRequest("Player 1 Name:", "p1name", mode=PromptRequest.Mode.MIXED,
                                      options=dict(length=3)),
                        PromptRequest("Player 2 Name:", "p2name", mode=PromptRequest.Mode.MIXED, options=dict(length=3))
                    ]
                else:
                    GAME.state = GAME.State.CANCELED
            if not RUNNING:
                break


def display():
    global RUNNING, GAME, HEADER
    with FullscreenWindow() as window:

        now = time.time()

        print('Graphics loading')

        figlet = Figlet('starwars', width=window.width - 4, justify='center')
        fig1 = Figlet('starwars', width=int(window.width / 2), justify='center')
        fig2 = Figlet('starwars', width=int(window.width / 2), justify='center')

        while RUNNING:
            last = now
            now = time.time()

            a = FSArray(window.height, window.width)

            state_control_names = {
                Game.State.SETUP: 'Cancel',
                Game.State.CANCELED: 'Reset',
                Game.State.COUNTDOWN: 'Cancel',
                Game.State.PREGAME: 'Setup',
                Game.State.FINISHED: 'Start New',
                Game.State.PLAYING: 'Stop'
            }

            top_left = f'[Slot Race Console v0]'
            top_right = f'Count Data: [' \
                        f'Lane 1: ({GAME.lane_1_raw_count} - {GAME.lane_1_correction} = {GAME.lane_1_count}), ' \
                        f'Lane 2: ({GAME.lane_2_raw_count} - {GAME.lane_2_correction} = {GAME.lane_2_count}) ]'
            btm_left = f'Esc: Quit, F5: Restart, Enter: {state_control_names[GAME.state]} Game, ' \
                       f'Space: Quick Start/Stop' \
                if len(PROMPT_REQUESTS) <= 0 else PROMPT_REQUESTS[0].display
            btm_right = f'FPS: {int(1 / (now - last) * 100) / 100}, Time: {datetime.datetime.now().strftime("%I:%M:%S %p")}'
            top_left = invert(bold(top_left + ((window.width - len(top_left) - len(top_right)) * ' ') + top_right))
            btm_left = invert(bold(btm_left + ((window.width - len(btm_left) - len(btm_right)) * ' ') + btm_right))

            a[0:1, 0:top_left.width] = [top_left]
            a[window.height - 1:window.height, 0:btm_left.width] = [btm_left]
            # a[1:window.height - 1, 1:window.width - 1] = fsarray(
            #    get_empty_box(window.height - 2, window.width - 2, on_black))
            header = fsarray(figlet.renderText(HEADER).split('\n'))
            a[2:header.height + 2, 3:header.width + 3] = header
            # a[1 above top:bottom, 1 before left:right]

            if GAME.state in [Game.State.PLAYING, Game.State.FINISHED, Game.State.CANCELED, Game.State.COUNTDOWN]:
                score1 = fsarray(
                    fig1.renderText(GAME.p1name + '\n' + str(GAME.lane_1_count)).split('\n'))
                score2 = fsarray(
                    fig2.renderText(GAME.p2name + '\n' + str(GAME.lane_2_count)).split('\n'))

                a[window.height - score1.height - 2:window.height - 2, 3:score1.width + 3] = score1
                a[window.height - score2.height - 2:window.height - 2,
                window.width - score2.width - 8:window.width + 8] = score2

            window.render_to_terminal(a)

        window.render_to_terminal(FSArray(window.height, window.width))


def game_loop():
    global RUNNING, RESTART, HEADER, GAME, INFLECT_ENGINE, PROMPT_REQUESTS, PROMPT_RESPONSES
    last_state = GAME.state

    while RUNNING:
        if GAME.state == GAME.State.PREGAME:
            HEADER = 'Slot Race Console'
        elif GAME.state == GAME.State.SETUP:
            HEADER = 'Setting Up Game'
            if len(PROMPT_REQUESTS) == 0:
                GAME.reset_counts()
                GAME.p1name = PROMPT_RESPONSES['p1name']
                GAME.p2name = PROMPT_RESPONSES['p2name']
                GAME.num_laps = PROMPT_RESPONSES['laps']
                GAME.mode = PROMPT_RESPONSES['game_mode']
                GAME.state = Game.State.COUNTDOWN
        elif GAME.state == GAME.State.COUNTDOWN:
            HEADER = 'Starting in 3...'
            conditional_sleep(1, GAME.state == Game.State.COUNTDOWN)
            HEADER = 'Starting in 2...'
            conditional_sleep(1, GAME.state == Game.State.COUNTDOWN)
            HEADER = 'Starting in 1...'
            conditional_sleep(1, GAME.state == Game.State.COUNTDOWN)
            HEADER = 'GO!!!'
            conditional_sleep(2.33, GAME.state == Game.State.COUNTDOWN)
            if GAME.lane_1_count + GAME.lane_2_count > 0:
                GAME.state = Game.State.CANCELED
                HEADER = 'False Start!'
                time.sleep(2.33)
            elif GAME.state == GAME.State.COUNTDOWN:
                GAME.state = GAME.State.PLAYING
        elif GAME.state == GAME.State.PLAYING:
            if GAME.mode == Game.Mode.LAPS:
                HEADER = f'First to {INFLECT_ENGINE.number_to_words(GAME.num_laps)} {INFLECT_ENGINE.plural("lap", GAME.num_laps)}'
            elif GAME.mode == Game.Mode.FASTEST:
                HEADER = f'Fastest out of {INFLECT_ENGINE.number_to_words(GAME.num_laps)} {INFLECT_ENGINE.plural("lap", GAME.num_laps)}'
            else:
                HEADER = f'{GAME.mode}'
                print(GAME.mode)
                time.sleep(1.5)
                RUNNING = False
                RESTART = False
            if max([GAME.lane_1_count, GAME.lane_2_count]) >= GAME.num_laps:
                GAME.state = GAME.State.FINISHED
                if GAME.lane_1_count > GAME.lane_2_count:
                    GAME.player_1_wins = True
                elif GAME.lane_2_count > GAME.lane_1_count:
                    GAME.player_1_wins = False
                else:
                    GAME.player_1_wins = None
        elif GAME.state == GAME.State.FINISHED:
            HEADER = 'Tie Game!' if GAME.player_1_wins is None else (
                    (GAME.p1name if GAME.player_1_wins else GAME.p2name) + ' Wins!')
        elif GAME.state == GAME.State.CANCELED:
            HEADER = 'Game Canceled'
            conditional_sleep(2.33, GAME.state == Game.State.CANCELED)
            GAME.state = GAME.State.PREGAME


# load last settings
try:
    with open('RaceConsole/data.json') as f:
        PROMPT_RESPONSES = dict(json.load(f))
except:
    PROMPT_RESPONSES = dict()

# create globals
INFLECT_ENGINE = inflect.engine()

PROMPT_REQUESTS = []
RUNNING = True
GAME = Game()
RESTART = False
HEADER = 'Slot Race Console'

# start threads
loop_funcs = [input_processing, display, game_loop, serial_stuff]
threads = [threading.Thread(target=func, daemon=True) for func in loop_funcs]

for thread in threads:
    thread.start()

# wait until we should quit
while all([thread.is_alive() for thread in threads]) and RUNNING:
    time.sleep(1)

report = "Stopped at " + str(datetime.datetime.now().strftime("%I:%M:%S %p"))
stopped_unexpectedly = RUNNING

# handle quitting condition
if RUNNING:
    RUNNING = False
    report += red('Quitting because, One or more threads stopped unexpectedly.\n')
    report += underline('Thread Running States\n')

    for thread in threads:
        report += f'\t{loop_funcs[threads.index(thread)].__name__}: {thread.is_alive()}\n'
else:
    report += green("Quit normally.")

if sum([thread.is_alive() for thread in threads]) > 0:
    conditional_sleep(3, condition=(sum([thread.is_alive() for thread in threads]) > 0))
    if sum([thread.is_alive() for thread in threads]) > 0:
        report += red('One or more threads is still running and did not stop in the allotted time (3 sec).\n')
        report += underline('Thread Running States\n')

        for thread in threads:
            report += f'\t{loop_funcs[threads.index(thread)].__name__}: {thread.is_alive()}\n'
    else:
        report += 'One or more threads took longer than expected to stop.'

with open('RaceConsole/data.json', 'w') as json_file:
    json.dump(PROMPT_RESPONSES, json_file)

# fix console
os.system('clear')
os.system('tset')

# final stuffs
if RESTART:
    print(invert('Slot Race Console is restarting!'))

    python = sys.executable
    os.execl(python, python, *sys.argv)

else:
    print(invert('Slot Race Console is closing. Thanks for playing!'))

if stopped_unexpectedly:
    print('Unfortunately, the game stopped unexpectedly. Typically this is '
          'caused by an exception in one of the threads.\n\n' + underline('Report'))
    print(report)

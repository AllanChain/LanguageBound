import curses
import random
import time
from sys import platform

# from card_collection import Frost, Knight

MLINE = 4
MCOLS = 5
PADDING_TOP = 2
PADDING_LEFT = 1
MAX_DECK = 3
COLOR = {
    'BLUE': curses.COLOR_BLUE,
    'RED': curses.COLOR_RED,
    'NEUTRAL': curses.COLOR_WHITE,
    'PYTHON': curses.COLOR_CYAN,
    'FIRE': curses.COLOR_RED,
    'MAGICIAN': curses.COLOR_MAGENTA,
    'MENA': curses.COLOR_BLUE,
    'SPEED': curses.COLOR_GREEN,
    'STRENGTH': curses.COLOR_RED,
}


class Board:
    def __init__(self, stdscr):
        from teams import teams

        self.data = [[None]*MCOLS for i in range(MLINE)]
        self.turn = 'BLUE'
        self.teams = {k: Team(k, *v) for k, v in teams.items()}
        self.stdscr = stdscr

    def get(self, pos, team=''):
        i, j = pos
        # empty string as mark of omit
        if team == '':
            team = self.turn
        # donnot change for BLUE and None
        if team == 'RED':
            j = MCOLS - 1 - j
        return self.data[i][j]

    def set(self, unit, pos, team=None):
        if unit is not None:
            unit.pos = pos
        i, j = pos
        if team is None:
            if unit is not None:
                # Easy debugging by pre-placing
                team = unit.team
            else:
                team = self.turn
        if team == 'RED':
            j = MCOLS - 1 - j
        self.data[i][j] = unit

    def get_enermy(self):
        return 'BLUE' if self.turn == 'RED' else 'RED'

    def iter_unit(self, team=None):
        for j in range(MCOLS-1, -1, -1):
            for i in range(MLINE):
                unit = self.get((i, j), team)
                if unit is not None and (team is None or unit.team == team):
                    yield i, j, unit

    def visual_frontline(self, team):
        frontline = self.frontline(team)
        return frontline+1 if team == 'BLUE' else MCOLS-1-frontline

    def frontline(self, team):
        for i, j, unit in self.iter_unit(team):
            return min(j, MCOLS-2)
        return 0

    def draw(self):
        stdscr = self.stdscr
        for i in range(MLINE*3-1):
            stdscr.addstr(i+PADDING_TOP, PADDING_LEFT, ' '*4*MCOLS)
        stdscr.addstr(0, 0, "{:<2}{:^17}{:>2}{:>5}".format(
            self.teams['BLUE'].base, self.turn+' turn',
            self.teams['RED'].base, self.teams[self.turn].mena),
            curses.A_BOLD)
        for i, j, unit in self.iter_unit():
            stdscr.addstr(i*3+PADDING_TOP, j*4+PADDING_LEFT,
                          unit.name, COLOR[unit.team])
            # Use addstr to ensure color in linux
            stdscr.addstr(i*3+PADDING_TOP+1, j*4+PADDING_LEFT,
                          '*', COLOR[unit.kingdom])
            strength = str(unit.strength)
            stdscr.addstr(i*3+PADDING_TOP+1,
                          j*4+PADDING_LEFT+3-len(strength), strength)
        for i in range(MLINE+1):
            stdscr.addstr(i*3+PADDING_TOP-1, PADDING_LEFT, '-'*(MCOLS*4-1))
        for j in range(MCOLS+1):
            for i in range(MLINE*3-1):
                stdscr.addstr(i+PADDING_TOP, j*4+PADDING_LEFT-1, '|')
        for i in range(MLINE*3-1):
            stdscr.addstr(i+PADDING_TOP,
                          self.visual_frontline(self.turn)*4+PADDING_LEFT-1,
                          '|', COLOR[self.turn])
        self.teams[self.turn].draw_cards(stdscr)
        stdscr.refresh()

    def play(self, card_id, pos):
        i, j = pos
        # visual to virtual
        if self.turn == 'RED':
            j = MCOLS - 1 - j
        target = self.get((i, j))
        myteam = self.teams[self.turn]
        card = myteam.cards[card_id]
        log(j, self.frontline(self.turn))
        if j > self.frontline(self.turn):
            log('Frontline Error')
            return
        if myteam.mena < card.mena:
            log('Mena Failure')
            return
        if target is None:
            if card.target is not None:
                log('Please Select Target')
                return
            self.set(card, (i, j))
            myteam.mena -= card.mena
            card.onplay(self)
            while card.speed > 0 and card.strength > 0:
                log(card.strength)
                for delta in (1, -1):
                    if not 0 <= i+delta < MLINE:
                        continue
                    eu = self.get((i+delta, j))
                    if eu is not None and eu.team != self.turn:
                        i += delta
                        self.gounit((i-delta, j), (i, j))
                        break
                else:
                    self.gounit((i, j), (i, j+1))
                    j += 1
                card.speed -= 1
            del self.teams[self.turn].cards[card_id]
            return
        if card.target == (target.team == self.turn):
            myteam.mena -= card.mena
            card.onplay(self, target)
            del self.teams[self.turn].cards[card_id]
            return
        log('Target Error')

    def gounit(self, pos0, pos1):
        time.sleep(0.2)
        unit = self.get(pos0)
        # print(pos0, pos1)
        self.set(None, pos0)
        i, j = pos1
        if j >= MCOLS:
            self.teams[self.get_enermy()].base -= unit.strength
            unit.onenter(self)
            return
        enermy_unit = self.get(pos1)
        if enermy_unit is None:
            self.set(unit, pos1)
        elif enermy_unit.team == self.turn:
            unit.speed = 0
            self.set(unit, pos0)
        else:
            unit.onattack(self, enermy_unit)
            if unit.strength < enermy_unit.strength:
                unit.ondeath(self)
                enermy_unit.strength -= unit.strength
                # to help detect death
                unit.strength = 0
            else:
                enermy_unit.ondeath(self)
                self.set(None, pos1)
                unit.strength -= enermy_unit.strength
                if unit.strength > 0:
                    self.set(unit, pos1)
                else:
                    unit.ondeath(self)
        self.draw()

    def proceed(self):
        self.turn = self.get_enermy()
        self.teams[self.turn].new_turn()
        for i, j, unit in self.iter_unit(self.turn):
            self.gounit((i, j), (i, j+1))
        self.draw()

    def surrounding(self, pos):
        i, j = pos
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == dj == 0:
                    continue
                ri, rj = i+di, j+dj
                if 0 <= ri < MLINE and 0 <= rj < MCOLS:
                    yield ri, rj

    def bordering(self, pos):
        i, j = pos
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if abs(di+dj) != 1:
                    continue
                ri, rj = i+di, j+dj
                if 0 <= ri < MLINE and 0 <= rj < MCOLS:
                    yield ri, rj



class Team:
    base = 10
    base_mena = 2

    def __init__(self, name, *deck):
        self.name = name
        self.deck = deck
        self.new_turn()

    def draw_cards(self, stdscr):
        for i in range(MAX_DECK*3):
            stdscr.addstr(i+PADDING_TOP, MCOLS*4+PADDING_LEFT+1, ' '*8)
        for i, card in enumerate(self.cards):
            stdscr.addstr(i*3+PADDING_TOP, MCOLS*4+PADDING_LEFT+1,
                          card.__class__.__name__, COLOR[self.name])
            stdscr.addstr(i*3+PADDING_TOP+1, MCOLS*4+PADDING_LEFT+1,
                          '*', COLOR[card.kingdom])
            stdscr.addstr(i*3+PADDING_TOP+1, MCOLS*4+PADDING_LEFT+2,
                          str(card.mena), COLOR['MENA'])
            stdscr.addstr(i*3+PADDING_TOP+1, MCOLS*4+PADDING_LEFT+4,
                          str(card.speed), COLOR['SPEED'])
            stdscr.addstr(i*3+PADDING_TOP+1, MCOLS*4+PADDING_LEFT+6,
                          str(card.strength), COLOR['STRENGTH'])

    def new_turn(self):
        self.cards = [card(self.name)
                      for card in random.sample(self.deck, MAX_DECK)]
        self.base_mena += 1
        self.mena = self.base_mena


class Logger:
    content = ''

    def __init__(self, stdscr):
        self.stdscr = stdscr

    def write(self, s):
        self.content += s

    def __call__(self, *args, **kargs):
        print(*args, **kargs, file=self)
        self.stdscr.addstr(14, 0, self.content)
        self.content = ''


def mouse_where(len_cards):
    try:
        _, x, y, *__ = curses.getmouse()
    except:
        return 'IGNORE', None
    if y == 0 and x < MCOLS*4:
        return 'END', None
    x -= PADDING_LEFT-1
    y -= PADDING_TOP-1
    if 0 < x < MCOLS*4 and 0 < y < MLINE*3:
        if x % 4 != 0 and y % 3 != 0:
            return 'BOARD', (y//3, x//4)
        return 'IGNORE', None
    if x > MCOLS*4 and 0 < y < len_cards*3:
        if y % 3 != 0:
            return 'DECK', y//3
        return 'IGNORE', None
    return 'ABORT', None


def init_color():
    for i, color_name in enumerate(COLOR.keys()):
        curses.init_pair(i+1, COLOR[color_name], curses.COLOR_BLACK)
        COLOR[color_name] = curses.color_pair(i+1)


def main(stdscr):
    global log
    # help(stdscr)
    stdscr.keypad(True)
    curses.curs_set(0)
    curses.mousemask(curses.BUTTON1_CLICKED)
    if platform == 'win32':
        curses.resize_term(16, 34)
    init_color()
    log = Logger(stdscr)
    board = Board(stdscr)
    # board.set(Knight('BLUE'), (0, 0))
    # board.set(Knight('BLUE'), (0, 1))
    # board.set(Frost('RED'), (2, 2))
    # board.set(Knight('RED'), (2, 3))
    # board.set(Frost('RED'), (0, 2))
    board.draw()
    time.sleep(1)
    card_selected = None
    while True:
        s = stdscr.getch()
        # stdscr.addstr(4, x,curses.keyname(s), curses.A_BOLD)
        cmd = ''
        if 32 <= s <= 127:
            cmd += str(curses.keyname(s))
            stdscr.addstr(curses.keyname(s), curses.A_BOLD)
            if s == ord('q'):  # or x>=curses.LINES-3:
                break
        # else:
            # stdscr.addstr(str(s))
        if s == curses.KEY_MOUSE:
            signal, pos = mouse_where(len(board.teams[board.turn].cards))
            log(signal, pos)
            if signal == 'END':
                board.proceed()
                # board.draw(stdscr)
            elif signal == 'DECK':
                card_selected = pos
            elif signal == 'ABORT':
                card_selected = None
            elif signal == 'BOARD':
                if card_selected is not None:
                    board.play(card_selected, pos)
                    # clear selection no matter play is valid or not
                    card_selected = None
                    board.draw()
            # stdscr.deleteln()
            # stdscr.move(stdscr.getyx()[0], 0)


curses.wrapper(main)

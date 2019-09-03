class Unit:
    name = ''
    kingdom = 'NEUTRAL'
    speed = 0
    mena = 0
    strength = 0
    target = None

    def __init__(self, team):
        self.team = team

    def onplay(self, board, target=None):
        pass

    def onattack(self, board, enermy):
        pass

    def onsurvive(self, board):
        pass

    def ondeath(self, board):
        pass

    def onenter(self, board):
        pass


class Expression(Unit):
    name = 'EXP'
    speed = 0
    mena = 1
    strength = 1


class Lambda(Unit):
    name = 'LMD'
    kingdom = 'PYTHON'
    speed = 2
    mena = 1
    strength = 1

    def onattack(self, board, enermy):
        enermy.strength -= 1


class Class(Unit):
    name = 'CLS'
    speed = 0
    mena = 3
    strength = 3


class Function(Unit):
    name = 'FUC'
    speed = 0
    mena = 2
    strength = 2


class Cmprehensn(Unit):
    name = 'CHS'
    kingdom = 'PYTHON'
    speed = 2
    mena = 1
    strength = 2


class Increment(Unit):
    mena = 1
    strength = 1
    target = True

    def onplay(self, board, target=None):
        target.strength += self.strength


class Decrement(Unit):
    mena = 1
    strength = 1
    target = False

    def onplay(self, board, target=None):
        target.strength -= self.strength
        if target.strength <= 0:
            board.set(None, board.get(target.pos))


class Egg(Unit):
    name = 'EGG'
    kingdom = 'PYTHON'
    speed = 0
    mena = 5
    strength = 2

    def onplay(self, board):
        for pos in board.bordering(self.pos):
            if board.get(pos, self.team) is not None:
                continue
            board.set(Expression(self.team), pos, team=self.team)


ALL_CARDS = (Class, Function, Lambda, Cmprehensn, Expression, Egg, Increment,
             Decrement)

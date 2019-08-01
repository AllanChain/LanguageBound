class Unit:
    name = ''
    kingdom = ''
    speed = 0
    mena = 0
    target = None

    def __init__(self, team):
        self.team = team

    def onplay(self, board):
        pass

    def onattack(self, board, enermy):
        pass

    def onsurvive(self, board):
        pass

    def ondeath(self, board):
        pass

    def onenter(self, board):
        pass


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
    kingdom = 'NEUTRAL'
    speed = 0
    mena = 3
    strength = 3


class Function(Unit):
    name = 'FUC'
    kingdom = 'NEUTRAL'
    speed = 0
    mena = 2
    strength = 2


class Cmphensn(Unit):
    name = 'CHS'
    kingdom = 'PYTHON'
    speed = 2
    mena = 1
    strength = 2

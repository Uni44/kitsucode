copas =  2000

def restasCopas(copasTotaltes, CopasPerdidas):
    global copas
    copas = copasTotaltes - CopasPerdidas

def sumarCopas(copasTotaltes, CopasGanadas):
    global copas
    copas = copasTotaltes + CopasGanadas

def ganarPartida():
    sumarCopas(copas, 8)
    print("Partida ganada, copas totales:" + str(copas))

def perderPartida():
    restasCopas(copas, 10)
    print("Partida perdida, copas totales:" + str(copas))

ganarPartida()
perderPartida()
perderPartida()
perderPartida()
perderPartida()
ganarPartida()
ganarPartida()
ganarPartida()
perderPartida()
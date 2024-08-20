import time
import random
import threading

class Mutex:
    def __init__(self):
        self.travado = False
        self.threadsEsperando = []

    def adquirir(self):
        while True:
            if not self.travado:
                self.travado = True
                break
            time.sleep(0.01)

    def liberar(self):
        self.travado = False

class Bola:
    def __init__(self):
        self.mutex = Mutex()
        self.temBola = True

    def pegarBola(self, pessoaId):
        self.mutex.adquirir()
        try:
            if self.temBola:
                self.temBola = False
                print(f"Pessoa {pessoaId} pegou a bola")
                return True
            else:
                print(f"Pessoa {pessoaId} tentou pegar a bola, mas a bola já estava ocupada")
                return False
        finally:
            self.mutex.liberar()

    def soltarBola(self):
        self.mutex.adquirir()
        try:
            self.temBola = True
            print("Opa, a bola foi liberada")
        finally:
            self.mutex.liberar()

class Semaforo:
    def __init__(self, valor):
        self.mutex = Mutex()
        self.valor = valor

    def adquirir(self):
        self.mutex.adquirir()
        try:
            if self.valor > 0:
                self.valor -= 1
                return True
            return False
        finally:
            self.mutex.liberar()

    def liberar(self):
        self.mutex.adquirir()
        try:
            self.valor += 1
        finally:
            self.mutex.liberar()

class Pessoa(threading.Thread):
    def __init__(self, id, semaforo, bola, eventoTerminado, contagemPegaBola):
        super().__init__()
        self.id = id
        self.semaforo = semaforo
        self.bola = bola
        self.eventoTerminado = eventoTerminado
        self.contagemPegaBola = contagemPegaBola

    def run(self):
        while not self.eventoTerminado.is_set():
            self.atravessarRua()
            self.voltarPonto()
            time.sleep(random.uniform(0.1, 1))
        
    def atravessarRua(self):
        while not self.semaforo.adquirir():
            time.sleep(0.01) 
        try:
            print(f"Pessoa {self.id} está atravessando a rua")
            time.sleep(random.uniform(0.1, 0.5))
            if self.bola.pegarBola(self.id):
                self.contagemPegaBola[self.id] += 1 
                time.sleep(random.uniform(0.5, 2))
                self.bola.soltarBola()
        finally:
            self.semaforo.liberar()

    def voltarPonto(self):
        print(f"Pessoa {self.id} voltou ao ponto inicial")
        time.sleep(random.uniform(0.1, 0.5))

def main():
    semaforo = Semaforo(1)
    bola = Bola()
    eventoTerminado = threading.Event()
    contagemPegaBola = {i: 0 for i in range(1, 4)} 
    pessoas = [Pessoa(id=i, semaforo=semaforo, bola=bola, eventoTerminado=eventoTerminado, contagemPegaBola=contagemPegaBola) for i in range(1, 4)]

    for pessoa in pessoas:
        pessoa.start()

    time.sleep(10)

    eventoTerminado.set()

    for pessoa in pessoas:
        pessoa.join()

    maxPegaBola = max(contagemPegaBola.values())
    vencedores = [pessoaId for pessoaId, contagem in contagemPegaBola.items() if contagem == maxPegaBola]

    if len(vencedores) > 1:
        vencedoresStr = ', '.join(f"Pessoa {id}" for id in vencedores)
        print(f"Fim do jogo! Empate entre {vencedoresStr} com {maxPegaBola} pegadas na bola ambos")
    else:
        vencedor = vencedores[0]
        print(f"Fim do jogo! Pessoa {vencedor} ganhou com um total de {maxPegaBola} pegadas na bola")

if __name__ == "__main__":
    main()

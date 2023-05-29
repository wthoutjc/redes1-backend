class Rules:
    def __init__(self, socket) -> None:
        self.socket = socket
        self.tramas = []
    
    def add_trama(self, trama):
        self.tramas.append(trama)
    
    def verificar_tramas(self):
        for trama in self.tramas:
            # Trama 0 siempre debe ser trama de control
            print(trama)

    def clean_tramas(self):
        self.tramas = []
from src.trama.trama import Trama

class Rules:
    def __init__(self, socket) -> None:
        self.socket = socket

        # RC -  Request Confirmation
        self.rc = 0
        self.secuencia_tramas = []

    def verificar_trama(self, trama:'Trama') -> bool:
        verified = True
        error = None
        type_response = None

        if trama.numero_secuencia == 0:
            # Trama 0 siempre debe ser trama de control
            if not trama.flags["solicitar_confirmacion"]:
                verified = False
                error = "La trama 0 debe ser de control [RC] = 1"
            else:
                self.rc = 1
                type_response = "SC"
        if trama.numero_secuencia > 0:
            if trama.flags["solicitar_confirmacion"]:
                verified = False
                error = "La trama debe ser de datos"
            if trama.numero_secuencia == 1:
                if not trama.flags["es_inicio_mensaje"]:
                    verified = False
                    error = "La trama debe ser de inicio de mensaje"
        
        if verified:
            self.secuencia_tramas.append({
                "message": f"Trama {len(self.secuencia_tramas)} (Tx) {trama.datos}",
            })
            return True, self.generate_response_trama(trama, type_response)
        else:
            self.secuencia_tramas.append({
                "error": error if error else "Trama no válida",
            })        
            return False, None

    def generate_response_trama(self, trama: 'Trama', type: str) -> 'Trama':
        # Crear trama
        inicio = trama.inicio
        numero_secuencia = trama.numero_secuencia
        datos = trama.datos

        if type == "SC":
            flags = {
                "es_inicio_mensaje": False,
                "es_fin_mensaje": False,
                "solicitar_confirmacion": False, # RC	
                "enviar_confirmacion": True, # SC
            }

        trama = Trama(inicio, numero_secuencia, flags, datos)
        return trama

    def add_secuencia_tramas(self, secuencia:dict):
        self.secuencia_tramas.append(secuencia)

    def get_secuencia_tramas(self):
        return self.secuencia_tramas

    def clean_tramas(self):
        self.secuencia_tramas = []
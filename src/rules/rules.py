from src.trama.trama import Trama

class Rules:
    def __init__(self, socket) -> None:
        self.socket = socket

        # RC -  Request Confirmation
        self.rc = 0
        self.sc = 0
        self.frames = 0
        self.secuencia_tramas = []

    def set_num_frames(self, frames: int) -> None:
        self.frames = frames

    def verificar_trama(self, trama:'Trama') -> bool:
        verified = True
        error = None
        type_response = None
        message = None

        if trama.flags["solicitar_confirmacion"] == 1:
            if self.rc == 1 and trama.numero_secuencia == 0:
                verified = False
                error = f"Trama (Rx), ya solicitó permiso para transmitir [RC] = 1"
                message = ""
            else:
                type_response = "SC"
                self.sc = 0
                message = "Otorgar permiso a transmisor"
        else:
            if trama.numero_secuencia == 0:
                verified = False
                error = f"Trama (Rx), la trama no cumple con las reglas"
                message = ""
            else:
                if self.rc == 0:
                    verified = False
                    error = f"Trama (Rx), no ha solicitado permiso para transmitir [RC] = 0"
                    message = ""
                else:
                    if self.sc == 0:
                        verified = False
                        error = f"Trama (Rx), debe responder el receptor para continuar [SC] = 0"
                        message = ""
                    else:
                        if int(trama.numero_secuencia) == int(self.frames) and trama.flags["es_fin_mensaje"] == 0:
                            verified = False
                            error = "Trama (Rx), la última trama debe habilitar el campo EM [EM] = 1"
                            message = ""
                        else:
                            type_response = "SC"
                            self.sc = 0
                            message = "Certificar llegada de datos"

        if verified:
            self.secuencia_tramas.append({
                "message": f"Trama (Tx) {trama.datos}",
            })
            return True, self.generate_response_trama(trama, type_response, message)
        else:
            self.secuencia_tramas.append({
                "error": error if error else "Trama no válida",
            })        
            return False, None


    def generate_response_trama(self, trama: 'Trama', type: str, message: str = None) -> 'Trama':
        # Crear trama
        inicio = trama.inicio
        numero_secuencia = trama.numero_secuencia
        datos = message or trama.datos

        flags = {
            "es_inicio_mensaje": False,
            "es_fin_mensaje": False,
            "solicitar_confirmacion": False, # RC	
            "enviar_confirmacion": False, # SC
        }

        if type == "SC":
            flags["enviar_confirmacion"] = True

        trama = Trama(inicio, numero_secuencia, flags, datos)
        return trama

    def add_secuencia_tramas(self, secuencia:dict):
        self.secuencia_tramas.append(secuencia)

    def get_secuencia_tramas(self):
        return self.secuencia_tramas

    def clean_tramas(self):
        self.secuencia_tramas = []
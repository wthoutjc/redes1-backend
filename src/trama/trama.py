class Trama:
    def __init__(self, inicio, numero_secuencia, flags, datos):
        self.inicio: int = inicio
        self.numero_secuencia: int = numero_secuencia
        self.flags: dict = flags
        self.datos: str = datos

    def es_valida(self) -> bool:
        # Si el número de secuencia = 0, la trama es de control
        if self.numero_secuencia == 0:
            for key, value in self.flags.items():
                if key == "solicitar_confirmacion" and value == 0:
                    return False
                elif key != "solicitar_confirmacion" and value != 0:
                    return False

            return True

        # La trama es de datos
        if not self.datos or self.datos == "":
            return False

        for key, value in self.flags.items():
            if key != "es_inicio_mensaje" and key != "es_fin_mensaje" and value == 1:
                return False
            
        if self.flags["es_inicio_mensaje"] == 0 and self.flags["es_fin_mensaje"] == 0:
            return False
        
        return True
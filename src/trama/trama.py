import crcmod

class Trama:
    def __init__(self, inicio, numero_secuencia, es_inicio_mensaje, es_fin_mensaje, solicitar_confirmacion, datos) -> None:
        self.inicio = inicio
        self.numero_secuencia = numero_secuencia
        self.es_inicio_mensaje = es_inicio_mensaje
        self.es_fin_mensaje = es_fin_mensaje
        self.solicitar_confirmacion = solicitar_confirmacion
        self.datos = datos
    
    def obtener_campos_control(self):
        campos_control = 0
        if self.es_inicio_mensaje:
            campos_control |= 0b10000000
        if self.es_fin_mensaje:
            campos_control |= 0b01000000
        if self.solicitar_confirmacion:
            campos_control |= 0b00100000
        # Puedes agregar otros campos de control aquí según tus necesidades
        return campos_control

    def interpretar_campos_control(self):
        numero_secuencia = self.numero_secuencia
        es_inicio_mensaje = bool(self.obtener_campos_control() & 0b10000000)
        es_fin_mensaje = bool(self.obtener_campos_control() & 0b01000000)
        solicitar_confirmacion = bool(self.obtener_campos_control() & 0b00100000)
        # Puedes interpretar otros campos de control aquí según tus necesidades
        return numero_secuencia, es_inicio_mensaje, es_fin_mensaje, solicitar_confirmacion

    def obtener_trama_completa(self):
        trama_completa = (
            self.inicio.to_bytes(1, 'big') +
            self.numero_secuencia.to_bytes(1, 'big') +
            self.obtener_campos_control().to_bytes(1, 'big') +
            self.datos
        )
        if self.crc is not None:
            trama_completa += self.crc.to_bytes(2, 'big')
        return trama_completa
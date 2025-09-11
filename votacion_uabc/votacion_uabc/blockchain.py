
import hashlib
import json
import time

class Bloque:
    def __init__(self, index, transacciones, timestamp, hash_anterior, nonce=0):
        self.index = index
        self.transacciones = transacciones
        self.timestamp = timestamp
        self.hash_anterior = hash_anterior
        self.nonce = nonce
        self.hash = self.calcular_hash()

    def calcular_hash(self):
        bloque_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(bloque_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.cadena = []
        self.transacciones_pendientes = []
        self.crear_bloque_genesis()

    def crear_bloque_genesis(self):
        genesis = Bloque(0, [], time.time(), "0")
        self.cadena.append(genesis.__dict__)

    def agregar_transaccion(self, transaccion):
        self.transacciones_pendientes.append(transaccion)

    def minar(self):
        if not self.transacciones_pendientes:
            return None
        ultimo_bloque = self.cadena[-1]
        nuevo_bloque = Bloque(
            index=len(self.cadena),
            transacciones=self.transacciones_pendientes,
            timestamp=time.time(),
            hash_anterior=ultimo_bloque["hash"]
        )
        self.cadena.append(nuevo_bloque.__dict__)
        self.transacciones_pendientes = []
        return nuevo_bloque.__dict__

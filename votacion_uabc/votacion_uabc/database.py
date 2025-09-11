from pymongo import MongoClient

cliente = MongoClient("mongodb+srv://andrea:COTwE52tGobKPhSe@cluster0.nds23w1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cliente["votacion_uabc"]
usuarios = db.usuarios
votos = db.votos
bloques = db.bloques

def registrar_usuario(matricula, correo):
    if not usuarios.find_one({"matricula": matricula}):
        usuarios.insert_one({"matricula": matricula, "correo": correo, "ha_votado": False})

def ha_votado(matricula):
    user = usuarios.find_one({"matricula": matricula})
    return user and user.get("ha_votado", False)

def marcar_voto(matricula):
    usuarios.update_one({"matricula": matricula}, {"$set": {"ha_votado": True}})

def guardar_voto(transaccion):
    votos.insert_one(transaccion)

def guardar_bloque(bloque):
    bloques.insert_one(bloque)

def obtener_resultados():
    pipeline = [
        {"$group": {"_id": "$voto", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ]
    return list(votos.aggregate(pipeline))


from flask import Flask, request, render_template, redirect
from blockchain import Blockchain
import database as db
from utils import es_estudiante_uabc
from pymongo import MongoClient

app = Flask(__name__)
blockchain = Blockchain()

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")  # o tu URI de Atlas
db_mongo = client["sistema_votaciones"]
votos_collection = db_mongo["votos_maestro"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/votar", methods=["POST"])
def votar():
    matricula = request.form["matricula"]
    correo = request.form["correo"]
    voto = request.form["voto"]

    if not es_estudiante_uabc(correo):
        return render_template("resultado.html", mensaje="Correo inválido. Debes usar tu cuenta @uabc.edu.mx.")

    if db.ha_votado(matricula):
        return render_template("resultado.html", mensaje="Ya has votado. Solo se permite un voto por estudiante.")

    db.registrar_usuario(matricula, correo)
    db.marcar_voto(matricula)

    transaccion = {"matricula": matricula, "voto": voto}
    blockchain.agregar_transaccion(transaccion)
    db.guardar_voto(transaccion)

    return render_template("resultado.html", mensaje="¡Tu voto ha sido registrado exitosamente!")

# ✅ NUEVA RUTA: Votación de Maestro Favorito
@app.route('/votar_maestro', methods=['POST'])
def votar_maestro():
    correo = request.form['correo']
    maestro = request.form['maestro']

    # Verifica si ya votó en esta categoría
    if votos_collection.find_one({'correo': correo, 'categoria': 'maestro'}):
        return render_template("resultado.html", mensaje="Ya has votado por un maestro favorito.")

    # Agrega el voto al blockchain
    blockchain.add_block({'correo': correo, 'maestro': maestro})
    # Guarda el voto en la base de datos
    votos_collection.insert_one({'correo': correo, 'maestro': maestro, 'categoria': 'maestro'})

    return render_template("resultado.html", mensaje="¡Voto por maestro favorito registrado!")

@app.route("/minar")
def minar():
    bloque = blockchain.minar()
    if bloque:
        db.guardar_bloque(bloque)
        return f"Bloque minado: {bloque['hash']}"
    else:
        return "No hay transacciones para minar."

@app.route("/resultados")
def resultados():
    votos = db.obtener_resultados()
    return render_template("resultados.html", resultados=votos, titulo="Resultados de Candidatos")

@app.route('/resultados_maestro')
def resultados_maestro():
    resultados = votos_collection.aggregate([
        {'$match': {'categoria': 'maestro'}},
        {'$group': {'_id': '$maestro', 'votos': {'$sum': 1}}}
    ])
    return render_template('resultados.html', resultados=resultados, titulo="Resultados: Maestro Favorito")

if __name__ == "__main__":
    app.run(debug=True)



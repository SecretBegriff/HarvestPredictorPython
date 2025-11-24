from flask import Flask, request, jsonify
from flask_cors import CORS
from conexion import guardarUsuario, crearTablaUsuarios

app = Flask(__name__)
CORS(app)

@app.route("/registrar", methods=["POST"])
def registrarusuario():
    datos = request.json
    print(f"Datos recibidos: {datos}")

    nombre = datos.get("Name")
    apellido = datos.get("lastName")
    numero = datos.get("Number")

    if not nombre or not apellido:
        return jsonify({"error": "Nombre y apellidos requeridos"}), 400
    
    ##Llama a la funcion guardarUsuario que esta en conexion
    exito = guardarUsuario(nombre, apellido, numero)

    if exito:
        return jsonify ({"mensaje": "Usuario registrado con exito"}), 200
    else: 
        return jsonify ({"mensaje": "Error al tratar de registrar al usuario"}), 500
    ##Iniciar Servidor
if __name__ == "__main__":
    # 3. LLAMADA CLAVE: Aseguramos que la tabla exista antes de arrancar la API.
    print("Iniciando verificación de la estructura de la base de datos...")
    crearTablaUsuarios()
    print("Verificación de la base de datos terminada.")
    app.run(debug=True, port=5000)
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import oracledb
import os

# Inicia el modo Thick con la ruta al Instant Client
oracledb.init_oracle_client(lib_dir=r"C:\oraclexe\instantclient_23_9")

DB_USER = os.getenv('DB_USER', 'userideam')
DB_PASS = os.getenv('DB_PASS', 'userideam')
DB_DSN  = os.getenv('DB_DSN', 'localhost/XE')


# Configuración de Flask
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'clave-secreta-dev')

# Crear un pool de conexiones (más eficiente)
pool = oracledb.create_pool(
    user=DB_USER,
    password=DB_PASS,
    dsn=DB_DSN,
    min=1,
    max=4,
    increment=1
)


# -------------------------
# RUTAS DE LA APLICACIÓN
# -------------------------
@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    departamentos = [
        "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bolívar", "Boyacá", "Caldas", "Caquetá",
        "Casanare", "Cauca", "Cesar", "Chocó", "Córdoba", "Cundinamarca", "Guainía", "Guaviare",
        "Huila", "La Guajira", "Magdalena", "Meta", "Nariño", "Norte de Santander", "Putumayo",
        "Quindío", "Risaralda", "San Andrés y Providencia", "Santander", "Sucre", "Tolima",
        "Valle del Cauca", "Vaupés", "Vichada"
    ]

    if request.method == 'POST':
        nro_documento = request.form['nro_documento']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        contrasena = request.form['contrasena']
        departamento = request.form['departamento']

        try:
            with pool.acquire() as connection:
                with connection.cursor() as cursor:
                    # Ejecutar INSERT directamente (no un procedimiento almacenado)
                    cursor.execute("""
                        INSERT INTO usuario (nro_documento, nombre, apellido, contrasena, departamento)
                        VALUES (:1, :2, :3, :4, :5)
                    """, (nro_documento, nombre, apellido, contrasena, departamento))
                    connection.commit()

            flash("✅ Usuario registrado exitosamente")
            return redirect(url_for('register'))

        except Exception as e:
            flash(f"⚠️ Error al registrar: {str(e)}")

    return render_template('register.html', departamentos=departamentos)





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nro_documento = request.form['nro_documento']
        contrasena = request.form['contrasena']

        try:
            with pool.acquire() as connection:
                with connection.cursor() as cursor:
                    # Variable de salida (1 si válido, 0 si no)
                    p_valido = cursor.var(int)

                    # Ejecuta tu procedimiento de login
                    cursor.callproc("SP_LOGIN_USUARIO", [nro_documento, contrasena, p_valido])

                    if p_valido.getvalue() == 1:
                        # ✅ Si las credenciales son correctas, obtenemos el nombre
                        cursor.execute("""
                            SELECT NOMBRE 
                            FROM USUARIOS 
                            WHERE NRO_DOCUMENTO = :nro
                        """, nro=nro_documento)
                        result = cursor.fetchone()
                        nombre = result[0].lower() if result else ""

                        flash("✅ Inicio de sesión exitoso")

                        # 🔹 Si el usuario se llama 'admin', redirige a index2
                        if nombre == "admin":
                            return redirect(url_for('index2'))
                        else:
                            return redirect(url_for('index'))
                    else:
                        flash("⚠️ Credenciales incorrectas")
        except Exception as e:
            flash(f"⚠️ Error de base de datos: {str(e)}")

    return render_template('login.html')



@app.route('/index')
def main_index():
    return render_template('index.html')


# ---------------------------
@app.route('/registro-arbol')
def registro_arbol():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('RegistroArbol.html')


@app.route('/registro-plantas')
def registro_plantas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('RegistroPlantas.html')
# ---------------------------
# EJECUCIÓN LOCAL
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


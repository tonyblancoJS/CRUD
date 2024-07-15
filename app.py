#importamos el framework de Flask
from flask import Flask, render_template, request, redirect, send_from_directory
#importamos la funcion que nos permite el render de los templates
from flask import render_template, request, redirect, url_for, flash
#conexion con la based e datos en MySQL
from flask_mysqldb import MySQL
#importamos datetime que nos permitira darle el nombre a la imagen
from datetime import datetime
#importamos paquetes de interfaz con el sistema operativo
import os

#creamos la aplicacion
app = Flask(__name__)
app.secret_key="ClaveSecreta" #necesitario p/ mensajes en caso de no ingresar nombre, director o imagen usado con flash
#Creamos la conexion con la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sistema'
#Inicializamos la extension MySQL
mysql = MySQL(app)

#Guardamos la ruta de la carpeta "uploads" en nuestra app
CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA
#Generamos el acceso a la carpeta uploads
#El metodo uploads que creamos nos dirige a la carpeta(variable CARPETA)
#y nos muestra la foto guardada en la variable nombreFoto.
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

#ruta de la raiz del sitio
@app.route('/')
def index():
#Creamos la variable que va a contner una consulta  
    sql = "SELECT * FROM peliculas;"

    conn = mysql.connect #Nos conectamos a la base de datos
    cursor = conn.cursor() #En cursor vamos a realizar las operaciones
    cursor.execute(sql) #Ejecutamos la sentencia SQL en el cursor
    #conn.commit()          
    db_peliculas = cursor.fetchall() #Copiamos el contenido del cursor a una variable

    print("  #   |   Película    |    Director       |    Imagen")
    print("-"*60) #Mostramos las tuplas por la terminal
    for pelicula in db_peliculas:
        print(pelicula)
        print("-"*60)

    cursor.close() # Cerramos el cursor
    #devolvemos codigo HTML para ser renderizado
    return render_template('peliculas/index.html', peliculas=db_peliculas)

#Funcion para eliminar un registro
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect
    cursor = conn.cursor()
    
    cursor.execute("SELECT foto FROM `peliculas` WHERE id=%s", (id,))
    fila= cursor.fetchall()
    
    try:
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
    except:
        pass
    
    cursor.execute("DELETE FROM `peliculas` WHERE id=%s", (id,))
    conn.commit()
    return redirect('/')

#Funcion para editar un registro
@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `peliculas` WHERE id=%s", (id,))
    peliculas = cursor.fetchall()
    cursor.close()
    return render_template('peliculas/edit.html', peliculas=peliculas)

#Funcion para actualizar los datos de una pelicula
@app.route('/update', methods=['POST'])
def update():
#Recibimos los valores del formulario html y los pasamos a variables locales
    _nombre = request.form['nombre']
    _director = request.form['director']
    _imagen = request.files['imagen']
    _id = request.form['id'] #se puede sacar porque no es actualizable por ser primary key
    
    #Armamos la sentencia SQL que va a almacenar estod datos en la DB:
    sql = "UPDATE `peliculas` SET nombre=%s, director=%s WHERE id=%s"
    params = (_nombre, _director, _id)
    
    #*********************verificar todo el codigo def update() no edita
    conn = mysql.connect
    cursor = conn.cursor()
    cursor.execute(sql, params)
    #Actualizacion de la foto si se proporciona una nueva
    if _imagen.filename != '':
        # Guardamos la foto con un nombre único basado en el tiempo
        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        nuevoNombreFoto = tiempo + '_' + _imagen.filename
        _imagen.save("uploads/" + nuevoNombreFoto)
        #Consultamos la foto anterior para borrarla del servidor DB
        cursor.execute("SELECT foto FROM `peliculas` WHERE id=%s", (_id,))
        fila = cursor.fetchone()

        if fila and fila[0] is not None:
            nombreFotoAnterior = fila[0]
            rutaFotoAnterior = os.path.join(app.config['CARPETA'], nombreFotoAnterior)

            if os.path.exists(rutaFotoAnterior):
                os.remove(rutaFotoAnterior)
        
        #Actualizamos la DB con el nuevo nombre de la foto
        cursor.execute("UPDATE `peliculas` SET foto=%s WHERE id=%s", (nuevoNombreFoto, _id)) #Ejecutamos la sentencia SQL en el cursor
    conn.commit() #Hacemos el commit
    cursor.close()
    #Redirigimos a la ruta principal
    return redirect('/')

@app.route('/create')
def create():
    return render_template('peliculas/create.html')

@app.route('/store', methods=['POST'])
def storage():
#Recibimos los valores del formulario html y los pasamos a variables locales
    _nombre = request.form['nombre']
    _director = request.form['director']
    _imagen = request.files['imagen']
    if _nombre == '' or _director == '' or _imagen.filename =='':
        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))
    #Guardamos en now los datos de la fecha y hora actual
    now = datetime.now()
    #Y en la variable tiempo almacenamos una cadena con Año Hora Minutos Segundos
    tiempo = now.strftime("%Y%H%M%S")
    #Si el nombre de la imagen ha sido proporcionado en el form...
    if _imagen.filename !='':
    #...le cambiamos el nombre
        nuevoNombreImagen = tiempo + '_' + _imagen.filename
        #Guardamos la imagen en la carpeta uploads
        _imagen.save("uploads/"+nuevoNombreImagen)
    else:
        nuevoNombreImagen = ''

    #Y armamos una tupla con esos valores:
    datos = (_nombre,_director,nuevoNombreImagen)
    
    #Armamos la sentencia SQL que va a almacenar estod datos en la DB:
    sql = "INSERT INTO `peliculas`(`id`, `nombre`, `director`, `foto`) VALUES (NULL,%s,%s,%s);"
    conn = mysql.connect #Nos conectamos a la base de datos
    cursor = conn.cursor() #En cursor vamos a realizar las operaciones
    cursor.execute(sql, datos) #Ejecutamos la sentencia SQL en el cursor
    conn.commit() #Hacemos el commit
    #Redirigimos a la ruta principal
    return redirect('/')

#Lineas requeridas por Python para empezar a trabajar con la app **siempre tiene que estar al final**
if __name__=='__main__':
    #corremos la aplicacion en modo debug
    app.run(debug=True)

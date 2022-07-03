import imp
from threading import local
from tkinter.tix import Form
from turtle import delay
from wsgiref.validate import InputWrapper
from flask import Flask, redirect, render_template, request,url_for, session,flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import  InputRequired, length
import pymysql
from flask_mysqldb import MySQL


db = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="Wr654321",db="pagina_web")


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Wr654321'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Wr654321'
app.config['MYSQL_DB'] = 'pagina_web'
mysql = MySQL(app)
app.config['SECRET_KEY'] = 'Wr654321'

#AQUI PREPARÉ LA PARTE INICIAL
#---------------------------------------------------------
@app.route("/")
def index():
    return render_template ("index.html")

@app.route("/contactos")
def contactos():
    return render_template ("contactos.html")

#AQUI PREPARÉ EL LOGIN
#---------------------------------------------------------
@app.route("/login", methods= ['GET','POST'])
def login():
    
    if 'loggedin' in session:
        
        return redirect(url_for('dashboard'))

    return render_template ("login.html")

@app.route("/user_login",methods= ['GET','POST'])
def user_login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        db_user_login = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="Wr654321",db="pagina_web")
        cursor_user_login =db_user_login.cursor(pymysql.cursors.DictCursor)
        cursor_user_login.execute("SELECT * FROM usuarios WHERE username=%s and password=%s", (username,password))
        cuenta = cursor_user_login.fetchone()
    if cuenta:
        session['loggedin'] = True
        session['id'] = cuenta['id']
        session['username'] = cuenta['username']
        return "SESION INICIADA CORRECTAMENTE!!!" ,  {"Refresh": "1.5; url=/dashboard"} 
    
    else:
        db_user_login.commit()
        db_user_login.close()
        return "ERROR: POR FAVOR REVISA EL USUARIO O LA CONTRASEÑA!!!" ,  {"Refresh": "1.5; url=/login"} 

#AQUI PREPARÉ LA CREACION DE USUARIOS, CONSULTA, EDICION Y ELIMINACION
#---------------------------------------------------------------------
@app.route("/registrar")
def registrar():
    if 'loggedin' in session:
        
        return render_template('registrar.html', username=session['username'])

    return redirect(url_for('login'))

@app.route("/user_done",methods= ['POST'])
def user_done():
    if request.method == "POST":
        username=request.form['usuario_txt']
        nombre=request.form['nombre_txt']
        apellido=request.form['apellido_txt']
        correo=request.form['correo_txt']
        password=request.form['clave_txt']
    cursor_user_done =db.cursor(pymysql.cursors.DictCursor)
    cursor_user_done.execute("SELECT * FROM usuarios WHERE username=%s", (username))
    info_registro = cursor_user_done.fetchone()
    if info_registro is not None:
        return "ERROR: ESTE USUARIO YA ESTA EN!!!... REDIRECCIONANDO AUTOMATICAMENTE",  {"Refresh": "1.3; url=/registrar"}
    
    elif info_registro is None:
        cursor = mysql.connection.cursor()
        cursor.execute ("INSERT INTO usuarios(username,nombre,apellido,password,correo) VALUES (%s,%s,%s,%s,%s)",(username,nombre,apellido,password,correo))
        cursor.connection.commit()
        return "USUARIO REGISTRADO CORRECTAMENTE!!!... REDIRECCIONANDO AUTOMATICAMENTE",  {"Refresh": "1.3; url=/dashboard"} 
        
@app.route("/ver_user", methods= ["GET", "POST"])
def ver_user():
    if 'loggedin' in session:
        cursor =mysql.connection.cursor()
        if request.method=="POST" and 'text_buscar' in request.form:
            cursor.execute("SELECT * FROM usuarios WHERE username like '%" + request.form['text_buscar'] + "%'")
            data = cursor.fetchall()
            return render_template ('usuarios.html',usuario = data)
        else:
            cursor.execute("SELECT * FROM usuarios")
            cursor.connection.commit()
            data = cursor.fetchall()
            return render_template ("usuarios.html",usuario = data)

    return redirect(url_for('login'))

@app.route('/editar_usuario/<id>')
def editar_user(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE id = {0}'.format(id))
    usuario = cursor.fetchall()
    return render_template('editar_user.html',usuario = usuario[0])

@app.route('/update_user_done/<id>', methods=['POST'])
def update_user_done(id):
    if request.method == 'POST':
        username = request.form['codigo_user']
        nombre = request.form['nombre_user']
        apellido = request.form['apellido_user']
        password = request.form['clave_user']
        correo = request.form['correo_user']
    cursor = mysql.connection.cursor()
    cursor.execute("""
    UPDATE usuarios set username =%s,
    nombre=%s, apellido =%s, password=%s,correo=%s 
    WHERE id = %s
    """,(username,nombre,apellido,password,correo,id))
    cursor.connection.commit()
    return "USUARIO EDITADO CORRECTAMENTE!!!... REDIRECCIONANDO AUTOMATICAMENTE",  {"Refresh": "1.3; url=/ver_user"} 

@app.route('/delete_user/<string:id>')
def delete_user(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM usuarios WHERE id = {0}'.format(id))
    mysql.connection.commit()
    return "USUARIO ELIMINADO CORRECTAMENTE!!!",  {"Refresh": "1.2; url=/ver_user"}

#AQUI PREPARÉ EL DASHBOARD Y EL LOGOUT
#---------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    if 'loggedin' in session:
        
        return render_template('dashboard.html', username=session['username'])

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login')) 


#AQUI PREPARÉ EL REGISTRO DE ENTRADA Y SALIDA DE PRODUCTOS
#---------------------------------------------------------
@app.route("/registro_entrada", methods= ["GET", "POST",])
def reg_entrada():
    curso =db.cursor()
    if request.method=="POST":
        sql = "insert into productos (id_pro,codigo_pro,nombre_pro, area_pro, precio_pro, cantidad_pro) values ('"+request.form['id']+"','"+request.form['codigo']+"', '"+request.form['nombre']+"','"+request.form['area']+"','"+request.form['precio']+"','"+request.form['cantidad']+"')"
        curso.execute(sql)
        db.commit()
    return render_template ("registro_entrada.html")

@app.route("/registro_salida")
def reg_salida():
    return render_template ("registro_salida.html")


#AQUI PREPARÉ LA CREACION, EDICION, CONSULTA Y ELIMINACION DE PRODUCTOS
#----------------------------------------------------------------

@app.route("/add_pro")
def add_pro():
    return render_template ("add_pro.html")

@app.route('/pro_done',methods= ['POST'])
def pro_done():
    if request.method == "POST":
        codigo_pro=request.form['codigo_pro']
        nombre_pro=request.form['nombre_pro']
        precio_pro=request.form['precio_pro']
        cantidad_pro=request.form['cantidad_pro']
        cursor = mysql.connection.cursor()
        cursor.execute ("INSERT INTO productos(codigo_pro,nombre_pro,precio_pro,cantidad_pro) VALUES (%s,%s,%s,%s)",(codigo_pro,nombre_pro,precio_pro,cantidad_pro))
        cursor.connection.commit()
        return "PRODUCTO CREADO CORRECTAMENTE!!!... REDIRECCIONANDO AUTOMATICAMENTE",  {"Refresh": "1.5; url=/almacen"} 

@app.route('/editar_producto/<id_pro>')
def editar_pro(id_pro):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM productos WHERE id_pro = {0}'.format(id_pro))
    almacen = cursor.fetchall()
    return render_template('editar_pro.html',almacenes=almacen[0])


@app.route('/update_pro/<id_pro>', methods=['POST'])
def update_pro(id_pro):
    if request.method == 'POST':
        codigo_pro = request.form['codigo_pro']
        nombre_pro = request.form['nombre_pro']
        area_pro = request.form['area_pro']
        precio_pro = request.form['precio_pro']
        cantidad_pro = request.form['cantidad_pro']
    cursor = mysql.connection.cursor()
    cursor.execute("""
    UPDATE productos set codigo_pro =%s,
    nombre_pro=%s,area_pro =%s, precio_pro =%s, cantidad_pro=%s 
    WHERE id_pro = %s
    """,(codigo_pro,nombre_pro,area_pro,precio_pro, cantidad_pro,id_pro))
    cursor.connection.commit()
    return "PRODUCTO EDITADO CORRECTAMENTE!!!... REDIRECCIONANDO AUTOMATICAMENTE",  {"Refresh": "2; url=/almacen"} 

@app.route('/almacen', methods= ["GET", "POST"])
def almacen():
    if 'loggedin' in session:
        cursor =mysql.connection.cursor()
        if request.method=="POST" and 'text_buscar' in request.form:
            cursor.execute("SELECT * FROM productos WHERE nombre_pro like '%" + request.form['text_buscar'] + "%'")
            data = cursor.fetchall()
            return render_template ('almacen.html',pro_almacenes = data)
        else:
            cursor.execute("SELECT * FROM productos")
            cursor.connection.commit()
            data = cursor.fetchall()
            return render_template ("almacen.html",pro_almacenes = data)

    return redirect(url_for('login'))

@app.route('/delete/<string:id_pro>')
def delete_pro(id_pro):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM productos WHERE id_pro = {0}'.format(id_pro))
    mysql.connection.commit()
    return "PRODUCTO ELIMINADO CORRECTAMENTE!!!",  {"Refresh": "1.2; url=/almacen"} 

if __name__=="__main__":
    app.run(debug=True)
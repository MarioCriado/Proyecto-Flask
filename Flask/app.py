from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)

class Pelicula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    genero = db.Column(db.String(50), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    calificacion = db.Column(db.Integer, default=0)
    usuario = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

class Serie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    temporadas = db.Column(db.Integer, nullable=False)
    genero = db.Column(db.String(50), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    calificacion = db.Column(db.Integer, default=0)
    usuario = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verificar_email', methods=['POST'])
def verificar_email():
    email = request.json.get('email')
    if Usuario.query.filter_by(email=email).first():
        return jsonify({'exists': True})
    return jsonify({'exists': False})

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        es_admin = 'es_admin' in request.form

        if Usuario.query.filter_by(email=email).first():
            return redirect(url_for('registro'))

        hashed_password = generate_password_hash(password)
        nuevo_usuario = Usuario(nombre=nombre, email=email, password=hashed_password, es_admin=es_admin)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.password, password):
            session['user_id'] = usuario.id
            session['user_name'] = usuario.nombre
            session['es_admin'] = usuario.es_admin
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/peliculas')
def peliculas():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search', '')
    order = request.args.get('order', 'titulo')

    query = Pelicula.query

    if not session.get('es_admin'):
        query = query.filter_by(usuario_id=session['user_id'])

    if search:
        query = query.filter(
            (Pelicula.titulo.ilike(f"%{search}%")) |
            (Pelicula.genero.ilike(f"%{search}%"))
        )

    if order == 'anio':
        peliculas = query.order_by(Pelicula.anio.asc()).all()
    elif order == 'titulo':
        peliculas = query.order_by(Pelicula.titulo.asc()).all()
    else:
        peliculas = query.all()

    return render_template('peliculas.html', peliculas=peliculas, order=order)


@app.route('/nueva_pelicula', methods=['GET', 'POST'])
def nueva_pelicula():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        director = request.form['director']
        genero = request.form['genero']
        anio = request.form['anio']
   
        pelicula = Pelicula(
            titulo=titulo,
            director=director,
            genero=genero,
            anio=anio,
            usuario=session['user_name'],
            usuario_id=session['user_id']
        )
        db.session.add(pelicula)
        db.session.commit()
        flash('Película agregada exitosamente', 'success')
        return redirect(url_for('peliculas'))

    return render_template('nueva_pelicula.html')

@app.route('/calificar_pelicula/<int:id>', methods=['POST'])
def calificar_pelicula(id):
    if 'user_id' not in session:
        flash('No estás autorizado para calificar películas', 'error')
        return redirect(url_for('peliculas'))
    
    pelicula = Pelicula.query.get_or_404(id)

    if pelicula.usuario_id != session['user_id']:
        flash('No estás autorizado para calificar esta película', 'error')
        return redirect(url_for('peliculas'))

    calificacion = int(request.form.get('calificacion'))
    if 0 <= calificacion <= 5:
        pelicula.calificacion = calificacion
        db.session.commit()
        flash('Calificación actualizada', 'success')
    
    return redirect(url_for('peliculas'))

@app.route('/editar_pelicula/<int:id>', methods=['GET', 'POST'])
def editar_pelicula(id):
    pelicula = Pelicula.query.get_or_404(id)

    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['user_id'])

    if not usuario.es_admin and pelicula.usuario_id != usuario.id:
        flash('No estás autorizado para editar esta película', 'error')
        return redirect(url_for('peliculas'))

    if request.method == 'POST':
        pelicula.titulo = request.form['titulo']
        pelicula.director = request.form['director']
        pelicula.genero = request.form['genero']
        pelicula.anio = request.form['anio']

        db.session.commit()
        flash('Película actualizada exitosamente', 'success')
        return redirect(url_for('peliculas'))

    return render_template('editar_pelicula.html', pelicula=pelicula)

@app.route('/eliminar_pelicula/<int:id>', methods=['POST'])
def eliminar_pelicula(id):
    if 'user_id' not in session:
        flash('No estás autorizado para eliminar películas', 'error')
        return redirect(url_for('peliculas'))

    pelicula = Pelicula.query.get_or_404(id)

    if pelicula.usuario_id != session['user_id']:
        flash('No estás autorizado para eliminar esta película', 'error')
    else:
        db.session.delete(pelicula)
        db.session.commit()
        flash('Película eliminada exitosamente', 'success')

    return redirect(url_for('peliculas'))


@app.route('/usuario')
def usuario():
    usuario = Usuario.query.get(session['user_id'])
    return render_template('usuario.html', usuario=usuario)

@app.route('/series')
def series():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search', '')
    order = request.args.get('order', 'titulo')

    query = Serie.query

    if not session.get('es_admin'):
        query = query.filter_by(usuario_id=session['user_id'])

    if search:
        query = query.filter(
            (Serie.titulo.ilike(f"%{search}%")) |
            (Serie.genero.ilike(f"%{search}%"))
        )

    if order == 'anio':
        series = query.order_by(Serie.anio.asc()).all()
    elif order == 'titulo':
        series = query.order_by(Serie.titulo.asc()).all()
    else:
        series = query.all()

    return render_template('series.html', series=series, order=order)

@app.route('/nueva_serie', methods=['GET', 'POST'])
def nueva_serie():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        temporadas = request.form['temporadas']
        genero = request.form['genero']
        anio = request.form['anio']
   
        serie = Serie(
            titulo=titulo,
            temporadas=temporadas,
            genero=genero,
            anio=anio,
            usuario=session['user_name'],
            usuario_id=session['user_id']
        )
        db.session.add(serie)
        db.session.commit()
        flash('Serie agregada exitosamente', 'success')
        return redirect(url_for('series'))

    return render_template('nueva_serie.html')

@app.route('/calificar_serie/<int:id>', methods=['POST'])
def calificar_serie(id):
    if 'user_id' not in session:
        flash('No estás autorizado para calificar series', 'error')
        return redirect(url_for('series'))
    
    serie = Serie.query.get_or_404(id)

    if serie.usuario_id != session['user_id']:
        flash('No estás autorizado para calificar esta serie', 'error')
        return redirect(url_for('series'))

    calificacion = int(request.form.get('calificacion'))
    if 0 <= calificacion <= 5:
        serie.calificacion = calificacion
        db.session.commit()
        flash('Calificación actualizada', 'success')
    
    return redirect(url_for('series'))

@app.route('/editar_serie/<int:id>', methods=['GET', 'POST'])
def editar_serie(id):
    serie = Serie.query.get_or_404(id)

    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['user_id'])

    if not usuario.es_admin and serie.usuario_id != usuario.id:
        flash('No estás autorizado para editar esta serie', 'error')
        return redirect(url_for('series'))

    if request.method == 'POST':
        serie.titulo = request.form['titulo']
        serie.temporadas = request.form['temporadas']
        serie.genero = request.form['genero']
        serie.anio = request.form['anio']

        db.session.commit()
        flash('Serie actualizada exitosamente', 'success')
        return redirect(url_for('series'))

    return render_template('editar_serie.html', serie=serie)

@app.route('/eliminar_serie/<int:id>', methods=['POST'])
def eliminar_serie(id):
    if 'user_id' not in session:
        flash('No estás autorizado para eliminar series', 'error')
        return redirect(url_for('series'))

    serie = Serie.query.get_or_404(id)

    if serie.usuario_id != session['user_id']:
        flash('No estás autorizado para eliminar esta serie', 'error')
    else:
        db.session.delete(serie)
        db.session.commit()
        flash('Serie eliminada exitosamente', 'success')

    return redirect(url_for('series'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

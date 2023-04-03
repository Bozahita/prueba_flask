import googlemaps
from flask import Flask, jsonify, request
from datetime import date, datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

# Configuracion del proyecto.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/flask_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

gmaps = googlemaps.Client(key='You Key')

# Creacion e tablas y sus relaciones.
class Institucion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.Date, default=datetime.today)
    proyectos = db.relationship('Proyecto', backref='institucion', lazy=True)

    def __init__(self, nombre, descripcion, direccion, fecha_creacion):
        self.nombre = nombre
        self.descripcion = descripcion
        self.direccion = direccion
        self.fecha_creacion = fecha_creacion

class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(100), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_termino = db.Column(db.Date, nullable=False)
    responsable_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    institucion_id = db.Column(db.Integer, db.ForeignKey('institucion.id'), nullable=False)

    def __init__(self, nombre, descripcion, fecha_inicio, fecha_termino):
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_termino = fecha_termino

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    rut = db.Column(db.String(10), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    proyectos = db.relationship('Proyecto', backref='responsable', lazy=True)

    def __init__(self, nombre, apellidos, direccion, rut,fecha_nacimiento,cargo,edad):
        self.nombre = nombre
        self.apellidos = apellidos
        self.direccion = direccion
        self.rut = rut
        self.fecha_nacimiento = fecha_nacimiento
        self.cargo = cargo
        self.edad = edad

with app.app_context():
    db.create_all()

# CRUD Instituciones.
@app.route('/institucion', methods=['POST'])
def crear_institucion():
    # Obtenemos los datos del request
    nombre = request.json['nombre']
    descripcion = request.json['descripcion']
    direccion = request.json['direccion']
    fecha_creacion = request.json['fecha_creacion']

    # Creamos una nueva institucion y la enviamos a la base de datos.
    nueva_institucion = Institucion(nombre, descripcion, direccion, fecha_creacion)

    db.session.add(nueva_institucion)
    db.session.commit()

    return jsonify({'mensaje': 'Nueva institución creada con éxito.'}),201

# Obtener todas las instituciones.
@app.route('/institucion', methods=['GET'])
def obtener_instituciones():
    instituciones = Institucion.query.all()
    resultado = []
    for institucion in instituciones:
        dict_inst = {
            'id': institucion.id,
            'nombre': institucion.nombre,
            'descripcion': institucion.descripcion,
            'direccion': institucion.direccion,
            'fecha_creacion': institucion.fecha_creacion
        }
        resultado.append(dict_inst)
    return jsonify(resultado)

@app.route('/institucion/<int:id>')
def get_institucion(id):
    # Obtener información de la institución.
    institucion = Institucion.query.filter_by(id=id).first()
    
    if not institucion:
        return "error", 404
    
    # Obtener información de los proyectos de la institución.
    proyectos = db.session.query(Proyecto, Usuario).join(Usuario, Proyecto.responsable_id == Usuario.id).filter(Proyecto.institucion_id == id).all()

    proyectos_data = []
    for proyecto, responsable in proyectos:
        proyecto_data = {
            'id': proyecto.id,
            'nombre': proyecto.nombre,
            'descripcion': proyecto.descripcion,
            'fecha_inicio': proyecto.fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_termino': proyecto.fecha_termino.strftime('%Y-%m-%d'),
            'responsable': {
                'nombre': responsable.nombre,
                'apellidos': responsable.apellidos,
                'rut': responsable.rut,
                'fecha_nacimiento': responsable.fecha_nacimiento.strftime('%Y-%m-%d'),
                'cargo': responsable.cargo,
                'edad': responsable.edad
            }
        }
        proyectos_data.append(proyecto_data)

    institucion_data = {
        'id': institucion.id,
        'nombre': institucion.nombre,
        'descripcion': institucion.descripcion,
        'direccion': institucion.direccion,
        'fecha_creacion': institucion.fecha_creacion.strftime('%Y-%m-%d'),
        'proyectos': proyectos_data
    }

    return jsonify(institucion_data),200

# Actualizar una institución existente.
@app.route('/institucion/<int:id>', methods=['PUT'])
def actualizar_institucion(id):
    institucion = Institucion.query.get_or_404(id)
    if 'nombre' in request.json:
        institucion.nombre = request.json['nombre']
    if 'descripcion' in request.json:
        institucion.descripcion = request.json['descripcion']
    if 'direccion' in request.json:
        institucion.direccion = request.json['direccion']
    if 'fecha_creacion' in request.json:
        institucion.fecha_creacion = request.json['fecha_creacion']

    db.session.commit()

    return jsonify({'mensaje': 'Institución actualizada con éxito.'}) 

# Eliminar una institución existente.
@app.route('/institucion/<int:id>', methods=['DELETE'])
def eliminar_institucion(id):
    institucion = Institucion.query.get_or_404(id)
    db.session.delete(institucion)
    db.session.commit()

    return jsonify({'mensaje': 'Institución eliminada con éxito.'}), 202


# Listar un usuario (filtro por Rut) con sus respectivos proyectos.
@app.route('/usuario/<int:id>',methods=['GET'])
def listar_usuarios(id):
    # Obtenemos el usuario y sus proyectos
    usuario = Usuario.query.get_or_404(id)
    proyectos = Proyecto.query.filter_by(responsable_id=usuario.id)

    # Formateamos a un diccionario la informacion de los proyectos
    proyectos_data = []
    for proyecto in proyectos:
        proyecto_data = {
            "id": proyecto.id,
            "nombre": proyecto.nombre,
            "descripcion": proyecto.descripcion,
            "fecha_inicio": proyecto.fecha_inicio.strftime('%d-%m-%Y'),
            "fecha_termino": proyecto.fecha_termino.strftime('%d-%m-%Y'),
        }
        proyectos_data.append(proyecto_data)

    # Creamos un diccionario con la informacion del usuario junto a sus proyectos.
    usuario_data = {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "apellidos": usuario.apellidos,
        "rut": usuario.rut,
        "fecha_nacimiento": usuario.fecha_nacimiento.strftime('%d-%m-%Y'),
        "cargo": usuario.cargo,
        "edad": usuario.edad,
        "proyectos": proyectos_data
    }
 
    return jsonify(usuario_data)

# Crear lista de instituciones con ubicación de Google Maps
@app.route('/instituciones/maps')
def listar_instituciones_mapped():
    instituciones = Institucion.query.all()

    instituciones_mapped = []
    for institucion in instituciones:
        direccion = institucion.direccion
        # obtener ubicación de Google Maps correspondiente a la dirección
        geocode_result = gmaps.geocode(direccion)
        latitud = geocode_result[0]['geometry']['location']['lat']
        longitud = geocode_result[0]['geometry']['location']['lng']
        # generar URL de Google Maps con la ubicación y la abreviación del nombre
        nombre_abreviado = institucion.nombre[:3]
        url_maps = f'https://www.google.com/maps/search/{latitud},{longitud}/{nombre_abreviado}'
        # crear diccionario con la institución y su URL de Google Maps
        institucion_mapped = {
            'id': institucion.id,
            'nombre': institucion.nombre,
            'descripcion': institucion.descripcion,
            'direccion': direccion,
            'url_maps': url_maps
        }
        instituciones_mapped.append(institucion_mapped)

    return jsonify(instituciones_mapped)

#Lista los proyectos. 
@app.route('/proyectos')
def listar_proyectos():
    #Obtenemos todos los proyectos
    proyectos = Proyecto.query.all()

    proyectos_data = []
    for proyecto in proyectos:
        # Obtenemos la fecha de hoy
        today = datetime.now().date()
        # calculamos los dias restantes
        dias_faltantes = (proyecto.fecha_termino - today).days
        # Validamos que los dias restantes no sean negativos
        if dias_faltantes <=0:
            dias_faltantes = 0
        # Creamos el diccionario de proyectos
        proyecto_data = {
            "nombre": proyecto.nombre,
            "dias_faltantes": dias_faltantes,
        }
        proyectos_data.append(proyecto_data)
    
    return jsonify(proyectos_data)

if __name__ == "__main__":
    app.run(debug=True)
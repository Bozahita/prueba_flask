import unittest
from app import app, db, Institucion

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bozaha:bozaha1603@localhost/flask_test'

    def test_get_institucion(self):

        # Creamos una institución para probar
        institucion1 = Institucion(nombre='Institucion 1', descripcion='Descripción 1', direccion='Dirección 1', fecha_creacion='2022-03-30')
        institucion2 = Institucion(nombre='Institucion 2', descripcion='Descripción 2', direccion='Dirección 2', fecha_creacion='2022-03-29')
            
        with app.app_context():
            db.session.add(institucion1)
            db.session.add(institucion2)
            db.session.commit()

        # Llamamos a la función get_institucion con el id de la institución creada
        with app.test_client() as client:
             with app.app_context():
                institucion_creada = Institucion.query.filter_by(nombre='Institucion 1').first()
                response = client.get(f'/institucion/{institucion_creada.id}')
                data = response.json

        # Verificamos que el status code sea 200 y que la institución tenga el nombre "Institucion 1"
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["nombre"],"Institucion 1")
    
    def test_actualizar_institucion(self):
        institucion1 = Institucion(nombre='Institucion 1', descripcion='Descripción 1', direccion='Dirección 1', fecha_creacion='2022-03-30')
        with app.test_client() as client:
            with app.app_context():
                db.session.add(institucion1)
                db.session.commit()

                institucion = Institucion.query.filter_by(nombre='Institucion 1').first()
                institucion_update = {
                "nombre": "Cambio test",
            }
                response = client.put(f"/institucion/{institucion.id}", json=institucion_update)
                data = response.json

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json, {'mensaje': 'Institución actualizada con éxito.'})

    def test_get_instituciones(self):
        with app.test_client() as client:
            response = client.get('/institucion')
            self.assertEqual(response.status_code, 200)

    def test_post_institucion(self):
        with app.test_client() as client:
            institucion = {
                "id": 3,
                "nombre": "test",
                "descripcion": "descripcion test",
                "direccion": "direccion test",
                "fecha_creacion": "2023-03-31",
            }
            response = client.post("/institucion",json=institucion)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json, {'mensaje': 'Nueva institución creada con éxito.'})
    
    def test_eliminar_institucion(self):
        with app.test_client() as client:
            with app.app_context():
                institucion = Institucion.query.filter_by(nombre='Cambio test').first()

                response = client.delete(f"/institucion/{institucion.id}")
                self.assertEqual(response.status_code, 202)
                self.assertEqual(response.json, {'mensaje': 'Institución eliminada con éxito.'})

    def test_listar_usuarios(self):
        with app.test_client() as client:
            with app.app_context():
                response = client.get(f'/usuario/1')

                self.assertEqual(response.status_code, 200)
    
    def test_listar_instituciones_mapped(self):
        with app.test_client() as client:
            with app.app_context():
                response = client.get(f'/instituciones/maps')
                self.assertEqual(response.status_code, 200)

    
    def test_listar_proyectos(self):
        with app.test_client() as client:
            with app.app_context():
                response = client.get(f'/proyectos')
                self.assertEqual(response.status_code, 200)
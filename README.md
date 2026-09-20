# Quality Farma en Django

Migración del sistema PHP/MySQL a Django. La configuración inicial usa SQLite para funcionar sin XAMPP; el archivo `quality_farma/settings.py` puede cambiarse a MySQL cuando se necesite conservar la base existente.

## Puesta en marcha

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/`.

Usuario demo: `raczooscar172212@gmail.com`  
Contraseña demo: `admin`

Módulos migrados: usuarios, documentos de calidad, hallazgos, CAPA, capacitaciones, dashboard y reportes.

## Roles y permisos

- `Administrador`: acceso completo a todos los módulos y operaciones.
- `Analista`: puede consultar, registrar y modificar información, pero no eliminarla.
- `Consultor`: puede consultar la información y descargar informes.

Los permisos se validan en el servidor, por lo que acceder directamente a una URL no permite superar las restricciones del rol.


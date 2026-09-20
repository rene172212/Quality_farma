from .views import PERMISOS_ROL, rol_actual, tiene_permiso


def permisos(request):
    rol = rol_actual(request)
    return {
        'permisos': PERMISOS_ROL.get(rol, PERMISOS_ROL['Consultor']),
        'rol_usuario': rol,
        'modulos_visibles': [modulo for modulo in ('usuarios', 'documentos', 'hallazgos', 'capa', 'capacitaciones') if tiene_permiso(request, modulo)],
        'puede_reportes': tiene_permiso(request, 'reportes'),
        'puede_descargar_reportes': tiene_permiso(request, 'reportes', 'descargar'),
    }

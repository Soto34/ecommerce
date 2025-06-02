from django.http import HttpResponseForbidden

def rol_en_sesion_requerido(roles_permitidos):
    def decorador(view_func):
        def _wrapped(request, *args, **kwargs):
            rol = request.session.get('rol')
            if rol not in roles_permitidos:
                return HttpResponseForbidden("Acceso denegado.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorador

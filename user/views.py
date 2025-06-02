import requests
from django.shortcuts import render, redirect
from django.contrib import messages
import jwt

def register_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'register.html')

        data = {
            "email": request.POST.get('email'),
            "nombre": request.POST.get('nombre'),
            "apellido": request.POST.get('apellido'),
            "rut": request.POST.get('rut'),
            "password": password,
            "rol": "cliente"
        }

        try:
            response = requests.post("http://localhost:8003/users/", json=data)
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error de conexión con la API: {str(e)}")
            return render(request, 'register.html')

        if response.status_code == 201:
            messages.success(request, "Usuario registrado correctamente.")
            return redirect('user:login')
        else:
            try:
                error_detail = response.json().get('detail', 'Error desconocido')
            except Exception:
                error_detail = f"Respuesta no JSON: {response.text}"
            messages.error(request, f"Error: {error_detail}")

    return render(request, 'register.html')
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            response = requests.post(
                "http://localhost:8003/token",
                data={"username": email, "password": password}
            )
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error al conectar con la API: {e}")
            return render(request, 'login.html')

        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            rol = data['user']['rol'].lower()

            # Guardar en sesión
            request.session['access_token'] = token
            request.session['user_email'] = data['user']['email']
            request.session['user_rol'] = rol

            # Redirigir por rol
            if rol == 'contador':
                return redirect('vista_contador')
            elif rol == 'repartidor':
                return redirect('lista_repartidor')
            elif rol == 'bodeguero':
                return redirect('lista_bodegueroecommerce')
            else:  # cliente o admin
                return redirect('home')
        else:
            try:
                error_detail = response.json().get("detail", "Error al iniciar sesión.")
            except:
                error_detail = response.text
            messages.error(request, error_detail)

    return render(request, 'login.html')


def recover_view(request):
    return render(request, 'recover.html')



def profile_view(request):
    token = request.session.get('jwt_token')
    if not token:
        messages.error(request, "Debes iniciar sesión para ver tu perfil.")
        return redirect('user:login')

    headers = {
        'Authorization': f'Bearer {token}',
    }

    try:
        response = requests.get('http://localhost:8003/users/me', headers=headers)
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error de conexión con la API: {str(e)}")
        return redirect('user:login')

    if response.status_code == 200:
        user_data = response.json()
        return render(request, 'profile.html', {'user': user_data})
    else:
        messages.error(request, "No autorizado o sesión expirada.")
        return redirect('user:login')
    

def logout_view(request):
    # Eliminar token JWT de sesión para "cerrar sesión"
    request.session.pop('jwt_token', None)
    # Opcional: también limpiar sesión completa con request.session.flush()
    return redirect('user:login')


# 🥐 PanZon - Ecommerce y Postventa

**PanZon** es una panadería y pastelería tradicional que nos contactó para desarrollar una plataforma web que integre funcionalidades de **Ecommerce** (venta en línea de productos de panadería) y un módulo de **Postventa**, permitiendo a los usuarios hacer seguimiento de sus pedidos, cargar comprobantes, validar pagos y más.

Este proyecto se compone de:
- Una aplicación web desarrollada en **Django**
- Una API REST en **FastAPI** (gestión de **productos** y **usuarios**)
- Una API REST en **Express.js** (gestión de **categorías**)

---

## 🚀 Requisitos del sistema

- Python 3.10+
- Node.js y NPM
- MySQL y MySQL Workbench
- Git

---

## 📦 Clonar y configurar el proyecto principal (Django)

1. Clona el repositorio:

```bash
git clone https://github.com/Soto34/ecommerce.git
cd ecommerce
```

2. Cambia a la rama correcta:

```bash
git fetch
git checkout fusion_postventa_api
```

3. Instala [MySQL](https://dev.mysql.com/downloads/installer/) y [MySQL Workbench](https://dev.mysql.com/downloads/workbench/)

4. Crea una conexión en MySQL Workbench, luego ejecuta:

```sql
CREATE DATABASE ejemplo;
```

5. Regresa al proyecto Django. Instala las dependencias:

```bash
pip install -r requirements.txt
```

6. Crea un archivo `.env` con tu configuración de base de datos. Puedes guiarte por el archivo `.env.example` incluido.

Ejemplo de `.env`:

```env
DB_NAME=ejemplo
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3306
```

7. Aplica las migraciones:

```bash
python manage.py migrate
```

8. Levanta el servidor:

```bash
python manage.py runserver
```

---

## ⚙️ Clonar y ejecutar la API FastAPI (productos y usuarios)

1. Clona el repositorio:

```bash
git clone https://github.com/Mnoxie/api_fastapv2.git
cd api_fastapv2
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Levanta el servidor FastAPI:

```bash
uvicorn main:app --reload --port 8003
```

4. Accede a la documentación automática:

👉 [http://127.0.0.1:8003/docs](http://127.0.0.1:8003/docs)

---

## ⚙️ Clonar y ejecutar la API Express.js (categorías)

1. Clona el repositorio:

```bash
git clone https://github.com/Mnoxie/api_express.git
cd api_express
```

2. Instala las dependencias:

```bash
npm install
```

3. Levanta el servidor Express:

```bash
node index.js
```

---

## ✅ Credenciales de prueba PayPal (Sandbox)

Para realizar pruebas de pago con PayPal, puedes usar la siguiente cuenta sandbox:

- **Email:** `sb-472igd43134992@personal.example.com`
- **Contraseña:** `D*!-Y7sj`

---

## ✅ Proyecto listo para funcionar

Una vez levantados los 3 servidores:

- 🧁 Django (sitio web): [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📦 FastAPI (productos y usuarios): [http://127.0.0.1:8003/docs](http://127.0.0.1:8003/docs)
- 🗂️ Express (categorías): revisa el puerto en consola

¡El sistema estará completamente funcional! 🎉

---

## 📌 Notas adicionales

- Los pagos pueden realizarse vía PayPal o transferencia, con carga obligatoria de comprobante.
- Toda la lógica de productos y usuarios se gestiona vía API REST FastAPI.
- Las categorías se gestionan vía API REST Express.js.

---

Desarrollado con ❤️ para **PanZon** por el equipo de desarrollo.
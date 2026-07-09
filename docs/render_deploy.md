# Despliegue en Render

## 1. Crear repositorio en GitHub

1. Cree un repositorio nuevo en GitHub.
2. No agregue archivos iniciales si el proyecto ya existe localmente.

## 2. Inicializar Git localmente

En la carpeta del proyecto ejecute:

```powershell
cd "C:\Users\cuate\OneDrive\Documents\New project\goto-reportes-ciudadanos"
git init
git add .
git commit -m "Preparar proyecto para Render"
```

## 3. Conectar el repositorio remoto

Reemplace la URL por la de su repositorio:

```powershell
git remote add origin https://github.com/USUARIO/goto-reportes-ciudadanos.git
git branch -M main
git push -u origin main
```

## 4. Crear el servicio en Render

1. Inicie sesion en [Render](https://render.com/).
2. Seleccione `New +`.
3. Elija `Web Service`.
4. Conecte su cuenta de GitHub si aun no esta conectada.
5. Seleccione el repositorio `goto-reportes-ciudadanos`.

## 5. Confirmar configuracion del despliegue

Render debe detectar estos archivos:

- `render.yaml`
- `Procfile`
- `requirements.txt`
- `runtime.txt`

Configuracion esperada:

- Build Command: `pip install -r requirements.txt`
- Start Command: `python app.py`
- Runtime: `python-3.11.9`

## 6. Ejecutar Deploy

1. Confirme la creacion del servicio.
2. Espere a que Render instale dependencias.
3. Espere a que el servicio termine el primer deploy.
4. Abra la URL publica generada por Render.

## 7. Verificar la aplicacion desplegada

Pruebe estas rutas:

- `/`
- `/dashboard`
- `/consulta`
- `/api/ivr/reporte?telefono=5527295528`
- `/api/ivr/reporte/folio?folio=20260001`

## 8. Notas importantes

- Localmente la aplicacion sigue usando `5055` por defecto.
- En Render el puerto se toma desde la variable de entorno `PORT`.
- El servidor se publica con `host="0.0.0.0"` para ser accesible en Render.

# goto-reportes-ciudadanos

Aplicacion Flask local para demo de reportes ciudadanos, pensada para integrarse despues con flujos GoTo como IVR y atencion automatizada.

## Objetivo del proyecto

- Registrar nuevos reportes ciudadanos desde una interfaz web.
- Consultar el estado mas reciente de un reporte por telefono o por folio.
- Permitir a funcionarios actualizar estatus y observaciones desde un dashboard.
- Exponer endpoints HTTP listos para pruebas de IVR con GoTo.

## Como instalar

1. Crear o activar el entorno virtual:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Instalar dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno para Gmail:

   ```powershell
   copy .env.example .env
   ```

   Luego ajuste:

   - `GMAIL_USER`
   - `GMAIL_APP_PASSWORD`

4. Cargar datos demo:

   ```powershell
   python seed_data.py
   ```

## Como ejecutar

```powershell
python app.py
```

Puerto usado por defecto: `5055`

Al iniciar debe mostrarse:

```text
Servidor iniciado:
http://127.0.0.1:5055
```

## Rutas principales

- `/`
- `/nuevo`
- `/consulta`
- `/dashboard`
- `/reporte/<id>`
- `POST /importar-correos-goto`

## Endpoints IVR

- `/api/ivr/reporte?telefono=5527295528`
- `/api/ivr/reporte/folio?folio=20260001`

## Importacion manual de correos GoTo

- Requiere `GMAIL_USER` y `GMAIL_APP_PASSWORD`.
- Busca correos de `noreply@dwf.goto.com` con asunto `Reporte de servicio`.
- El dashboard incluye el boton `Importar correos GoTo`.
- Evita duplicados por `email_message_id`.

## Datos demo

- `20260001` | Juan Perez | `5527295528` | Bache | `Nuevo`
- `20260002` | Maria Lopez | `5512345678` | Alumbrado | `En proceso`
- `20260003` | Carlos Ruiz | `5598765432` | Fuga de agua | `Programado`
- `20260004` | Juan Perez | `5527295528` | Basura | `Terminado`

Si un telefono tiene varios reportes, la consulta devuelve el mas reciente.

# Proyecto: Reportes Ciudadanos GoTo

## Descripcion funcional

La aplicacion permite registrar incidencias ciudadanas, consultarlas por telefono o folio y mantenerlas actualizadas desde un dashboard operativo. La base local usa SQLite y queda preparada para una integracion posterior con GoTo.

## Flujo GoTo

1. GoTo IVR envia una solicitud HTTP a `/api/ivr/reporte?telefono=...`.
2. La aplicacion normaliza el telefono y busca el reporte mas reciente.
3. El endpoint responde con un mensaje listo para Text-to-Speech.
4. Para consultas por folio, GoTo puede usar `/api/ivr/reporte/folio?folio=...`.

## Flujo ciudadano

1. El ciudadano registra un reporte desde `/nuevo`.
2. El sistema genera un folio numerico automatico.
3. El ciudadano puede consultar por telefono o folio desde `/consulta`.
4. La respuesta muestra estatus, fecha, direccion y un mensaje claro de seguimiento.

## Flujo funcionario

1. El funcionario abre `/dashboard`.
2. Revisa reportes recientes y entra al detalle de un caso.
3. Actualiza estatus y observaciones desde `/reporte/<id>`.
4. Los cambios quedan disponibles tanto en la web como en los endpoints IVR.

## Pendiente para fase Render

- Definir variables de entorno para despliegue.
- Ajustar configuracion de base de datos para entorno hospedado.
- Preparar archivo de arranque para despliegue administrado.
- Revisar persistencia de SQLite o migrar a una base externa.

## Pendiente para lectura automatica de correos GoTo

- Definir formato de correos entrantes.
- Crear parser de bandeja de entrada.
- Mapear incidentes a tipos de reporte.
- Registrar evidencia adjunta y observaciones automaticamente.

## Fuera de alcance en esta fase

- Conexion con correo real.
- Despliegue en Render.
- Integracion con WhatsApp o SMS.
- Login o control de acceso.

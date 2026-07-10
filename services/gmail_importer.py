import email
import imaplib
import os
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from email.header import decode_header
from email.message import Message
from email.policy import default
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup

from database import db
from models import (
    CANAL_RECEPCIONISTA_IA_GOTO,
    ORIGEN_IMPORTACION_CORREO_GOTO,
    Reporte,
    normalizar_telefono,
)

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
GOTO_SENDER = "noreply@dwf.goto.com"
GOTO_SUBJECT = "Reporte de servicio"


class GmailImportError(Exception):
    pass


@dataclass
class CorreoGoToParseado:
    descripcion: str
    direccion: str
    nombre_completo: str
    telefono_capturado: str
    referencia_adicional: str
    tipo_reporte: str
    telefono_origen: str
    email_message_id: str
    fecha_correo: datetime | None


def _normalizar_etiqueta(valor: str) -> str:
    base = unicodedata.normalize("NFKD", valor or "")
    sin_acentos = "".join(ch for ch in base if not unicodedata.combining(ch))
    limpio = re.sub(r"\s+", " ", sin_acentos).strip().lower()
    return limpio.rstrip(":")


def normalizar_telefono_origen(valor: str) -> str:
    texto = (valor or "").strip()
    digitos = re.sub(r"\D", "", texto)
    if not digitos:
        return ""
    if texto.lstrip().startswith("+"):
        return f"+{digitos}"
    return digitos


def _extraer_html_del_mensaje(mensaje: Message) -> str:
    if mensaje.is_multipart():
        for parte in mensaje.walk():
            if parte.get_content_type() != "text/html":
                continue
            if parte.get_content_disposition() == "attachment":
                continue
            return parte.get_content()
    elif mensaje.get_content_type() == "text/html":
        return mensaje.get_content()
    raise GmailImportError("El correo no contiene contenido HTML utilizable.")


def _decodificar_asunto(mensaje: Message) -> str:
    encabezado = mensaje.get("Subject", "")
    fragmentos = []
    for valor, encoding in decode_header(encabezado):
        if isinstance(valor, bytes):
            fragmentos.append(valor.decode(encoding or "utf-8", errors="replace"))
        else:
            fragmentos.append(valor)
    return "".join(fragmentos).strip()


def _extraer_campos_tabla(html: str) -> dict[str, list[str]]:
    soup = BeautifulSoup(html, "html.parser")
    campos: dict[str, list[str]] = {}

    for fila in soup.find_all("tr"):
        celdas = fila.find_all(["th", "td"])
        if len(celdas) < 2:
            continue
        etiqueta = _normalizar_etiqueta(celdas[0].get_text(" ", strip=True))
        valor = celdas[1].get_text(" ", strip=True)
        if not etiqueta or not valor:
            continue
        campos.setdefault(etiqueta, []).append(valor)
    return campos


def parsear_correo_goto_html(
    html: str,
    *,
    email_message_id: str,
    fecha_correo: datetime | None,
) -> CorreoGoToParseado:
    campos = _extraer_campos_tabla(html)

    telefonos = campos.get("numero de telefono", [])
    if len(telefonos) < 2:
        raise GmailImportError("El correo no contiene los dos telefonos esperados.")

    def valor_obligatorio(nombre: str) -> str:
        valores = campos.get(nombre, [])
        if not valores or not valores[0].strip():
            raise GmailImportError(f"Falta el campo requerido: {nombre}.")
        return valores[0].strip()

    return CorreoGoToParseado(
        descripcion=valor_obligatorio("descripcion del problema"),
        direccion=valor_obligatorio("direccion"),
        nombre_completo=valor_obligatorio("nombre completo"),
        telefono_capturado=telefonos[0].strip(),
        referencia_adicional=valor_obligatorio("referencia adicional"),
        tipo_reporte=valor_obligatorio("tipo de reporte"),
        telefono_origen=telefonos[1].strip(),
        email_message_id=email_message_id,
        fecha_correo=fecha_correo,
    )


def _obtener_message_id(mensaje: Message) -> str:
    message_id = (mensaje.get("Message-ID") or "").strip()
    return message_id.strip("<>").strip()


def _obtener_fecha_correo(mensaje: Message) -> datetime | None:
    encabezado = mensaje.get("Date")
    if not encabezado:
        return None
    try:
        fecha = parsedate_to_datetime(encabezado)
    except (TypeError, ValueError):
        return None
    if fecha.tzinfo is not None:
        return fecha.astimezone().replace(tzinfo=None)
    return fecha


def _crear_reporte_desde_correo(correo: CorreoGoToParseado) -> bool:
    if not correo.email_message_id:
        raise GmailImportError("El correo no contiene Message-ID.")

    if Reporte.query.filter_by(email_message_id=correo.email_message_id).first():
        return False

    telefono_capturado = normalizar_telefono(correo.telefono_capturado)
    telefono_origen = normalizar_telefono_origen(correo.telefono_origen)

    reporte = Reporte(
        folio=Reporte.generar_siguiente_folio(),
        fecha_reporte=correo.fecha_correo or datetime.utcnow(),
        nombre=correo.nombre_completo,
        telefono=telefono_capturado,
        telefono_capturado=telefono_capturado,
        telefono_origen=telefono_origen,
        direccion=correo.direccion,
        tipo_reporte=correo.tipo_reporte,
        descripcion=correo.descripcion,
        referencia=correo.referencia_adicional,
        estatus="Nuevo",
        observaciones="Reporte importado desde correo GoTo",
        canal_origen=CANAL_RECEPCIONISTA_IA_GOTO,
        email_message_id=correo.email_message_id,
        fecha_importacion=datetime.utcnow(),
        origen_importacion=ORIGEN_IMPORTACION_CORREO_GOTO,
        fecha_actualizacion=datetime.utcnow(),
    )
    db.session.add(reporte)
    db.session.commit()
    return True


def importar_reportes_desde_correos(correos: list[CorreoGoToParseado]) -> dict[str, int]:
    resumen = {
        "reviewed": len(correos),
        "created": 0,
        "duplicates": 0,
        "errors": 0,
    }

    for correo in correos:
        try:
            creado = _crear_reporte_desde_correo(correo)
        except GmailImportError:
            resumen["errors"] += 1
            db.session.rollback()
            continue

        if creado:
            resumen["created"] += 1
        else:
            resumen["duplicates"] += 1

    return resumen


def importar_correos_goto_desde_gmail() -> dict[str, int]:
    gmail_user = os.getenv("GMAIL_USER", "").strip()
    gmail_password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
    if not gmail_user or not gmail_password:
        raise GmailImportError("Faltan credenciales de Gmail.")

    try:
        imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        imap.login(gmail_user, gmail_password)
        imap.select("INBOX")
        estado, data = imap.search(
            None,
            f'(UNSEEN FROM "{GOTO_SENDER}" SUBJECT "{GOTO_SUBJECT}")',
        )
    except imaplib.IMAP4.error as exc:
        raise GmailImportError("No fue posible conectarse a Gmail.") from exc

    if estado != "OK":
        imap.logout()
        raise GmailImportError("No fue posible consultar los correos de Gmail.")

    correos_ids = data[0].split() if data and data[0] else []
    correos_parseados: list[CorreoGoToParseado] = []
    resumen = {
        "reviewed": 0,
        "created": 0,
        "duplicates": 0,
        "errors": 0,
    }

    try:
        for correo_id in correos_ids:
            resumen["reviewed"] += 1
            estado_fetch, payload = imap.fetch(correo_id, "(RFC822)")
            if estado_fetch != "OK" or not payload or not payload[0]:
                resumen["errors"] += 1
                continue

            mensaje = email.message_from_bytes(payload[0][1], policy=default)
            try:
                if _decodificar_asunto(mensaje) != GOTO_SUBJECT:
                    continue
                html = _extraer_html_del_mensaje(mensaje)
                correo = parsear_correo_goto_html(
                    html,
                    email_message_id=_obtener_message_id(mensaje),
                    fecha_correo=_obtener_fecha_correo(mensaje),
                )
                correos_parseados.append(correo)
            except GmailImportError:
                resumen["errors"] += 1
                continue

        if correos_parseados:
            resultado = importar_reportes_desde_correos(correos_parseados)
            resumen["created"] = resultado["created"]
            resumen["duplicates"] = resultado["duplicates"]
            resumen["errors"] += resultado["errors"]

        for correo_id in correos_ids:
            imap.store(correo_id, "+FLAGS", "\\Seen")
    finally:
        imap.logout()

    return resumen

import re
from datetime import datetime

from database import db

ESTATUS_PERMITIDOS = [
    "Nuevo",
    "En proceso",
    "Programado",
    "Terminado",
    "Cancelado",
]

CANALES_PERMITIDOS = [
    "Telefono",
    "WhatsApp",
    "WebChat",
    "Correo",
    "Presencial",
]


def normalizar_telefono(valor: str) -> str:
    digitos = re.sub(r"\D", "", valor or "")
    if len(digitos) >= 10:
        return digitos[-10:]
    return digitos


class Reporte(db.Model):
    __tablename__ = "reportes"

    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True, nullable=False, index=True)
    fecha_reporte = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(10), nullable=False, index=True)
    direccion = db.Column(db.String(255), nullable=False)
    tipo_reporte = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    referencia = db.Column(db.String(255), nullable=True)
    estatus = db.Column(db.String(30), nullable=False, default="Nuevo")
    observaciones = db.Column(db.Text, nullable=True)
    canal_origen = db.Column(db.String(30), nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def actualizar(self, **campos) -> None:
        for clave, valor in campos.items():
            setattr(self, clave, valor)
        self.fecha_actualizacion = datetime.utcnow()

    def mensaje_ciudadano(self) -> str:
        return (
            f"Su reporte con folio {self.folio} para {self.tipo_reporte} "
            f"se encuentra en estado: {self.estatus}."
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "folio": self.folio,
            "fecha_reporte": self.fecha_reporte.strftime("%Y-%m-%d %H:%M"),
            "nombre": self.nombre,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "tipo_reporte": self.tipo_reporte,
            "descripcion": self.descripcion,
            "referencia": self.referencia,
            "estatus": self.estatus,
            "observaciones": self.observaciones,
            "canal_origen": self.canal_origen,
            "fecha_actualizacion": self.fecha_actualizacion.strftime("%Y-%m-%d %H:%M"),
        }

    @classmethod
    def generar_siguiente_folio(cls) -> str:
        prefijo = str(datetime.utcnow().year)
        ultimo = (
            cls.query.filter(cls.folio.like(f"{prefijo}%"))
            .order_by(cls.folio.desc())
            .first()
        )
        if ultimo:
            consecutivo = int(ultimo.folio[-4:]) + 1
        else:
            consecutivo = 1
        return f"{prefijo}{consecutivo:04d}"

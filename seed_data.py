from datetime import datetime

from database import db
from models import Reporte, normalizar_telefono


def cargar_datos_demo() -> int:
    registros = [
        {
            "folio": "20260001",
            "fecha_reporte": datetime(2026, 1, 10, 9, 0),
            "nombre": "Juan Pérez",
            "telefono": "5527295528",
            "direccion": "Av. Central 123",
            "tipo_reporte": "Bache",
            "descripcion": "Bache profundo que afecta el paso de vehiculos.",
            "referencia": "Frente a la tienda",
            "estatus": "Nuevo",
            "observaciones": "Pendiente de asignacion.",
            "canal_origen": "Telefono",
            "fecha_actualizacion": datetime(2026, 1, 10, 9, 0),
        },
        {
            "folio": "20260002",
            "fecha_reporte": datetime(2026, 1, 11, 10, 15),
            "nombre": "María López",
            "telefono": "5512345678",
            "direccion": "Calle Norte 45",
            "tipo_reporte": "Alumbrado",
            "descripcion": "Lampara apagada desde hace varios dias.",
            "referencia": "Poste sin luz",
            "estatus": "En proceso",
            "observaciones": "Cuadrilla asignada para revision.",
            "canal_origen": "Telefono",
            "fecha_actualizacion": datetime(2026, 1, 12, 8, 30),
        },
        {
            "folio": "20260003",
            "fecha_reporte": datetime(2026, 1, 12, 12, 20),
            "nombre": "Carlos Ruiz",
            "telefono": "5598765432",
            "direccion": "Calle Sur 88",
            "tipo_reporte": "Fuga de agua",
            "descripcion": "Fuga continua en la via publica.",
            "referencia": "Cerca del mercado",
            "estatus": "Programado",
            "observaciones": "Atencion programada para manana.",
            "canal_origen": "Telefono",
            "fecha_actualizacion": datetime(2026, 1, 13, 9, 10),
        },
        {
            "folio": "20260004",
            "fecha_reporte": datetime(2026, 1, 13, 16, 45),
            "nombre": "Juan Pérez",
            "telefono": "5527295528",
            "direccion": "Av. Central 123",
            "tipo_reporte": "Basura",
            "descripcion": "Acumulacion de basura en la esquina principal.",
            "referencia": "Esquina principal",
            "estatus": "Terminado",
            "observaciones": "Servicio concluido por limpieza urbana.",
            "canal_origen": "Telefono",
            "fecha_actualizacion": datetime(2026, 1, 14, 11, 0),
        },
    ]

    insertados = 0
    for registro in registros:
        if Reporte.query.filter_by(folio=registro["folio"]).first():
            continue
        reporte = Reporte(
            **{
                **registro,
                "telefono": normalizar_telefono(registro["telefono"]),
            }
        )
        db.session.add(reporte)
        insertados += 1

    if insertados:
        db.session.commit()
    return insertados


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        db.create_all()
        total = cargar_datos_demo()
        print(f"Registros insertados: {total}")

from flask import Blueprint, jsonify, request

from models import Reporte, normalizar_telefono

ivr_bp = Blueprint("ivr", __name__, url_prefix="/api/ivr")


@ivr_bp.get("/reporte")
def consultar_por_telefono():
    telefono = normalizar_telefono(request.args.get("telefono", ""))
    if not telefono:
        return (
            jsonify(
                {
                    "encontrado": False,
                    "telefono": "",
                    "mensaje": "Debe proporcionar un numero telefonico valido.",
                }
            ),
            400,
        )

    reporte = (
        Reporte.query.filter_by(telefono=telefono)
        .order_by(Reporte.fecha_reporte.desc(), Reporte.id.desc())
        .first()
    )
    if not reporte:
        return jsonify(
            {
                "encontrado": False,
                "telefono": telefono,
                "mensaje": (
                    "No encontre reportes asociados a este numero telefonico. "
                    "Por favor verifique el numero o comuniquese con un asesor."
                ),
            }
        )

    return jsonify(
        {
            "encontrado": True,
            "telefono": telefono,
            "folio": reporte.folio,
            "estatus": reporte.estatus,
            "mensaje": (
                "Encontre su reporte mas reciente. "
                f"Folio {reporte.folio}. Estado actual: {reporte.estatus}."
            ),
        }
    )


@ivr_bp.get("/reporte/folio")
def consultar_por_folio():
    folio = "".join(ch for ch in request.args.get("folio", "") if ch.isdigit())
    if not folio:
        return (
            jsonify(
                {
                    "encontrado": False,
                    "folio": "",
                    "mensaje": "Debe proporcionar un folio numerico valido.",
                }
            ),
            400,
        )

    reporte = Reporte.query.filter_by(folio=folio).first()
    if not reporte:
        return jsonify(
            {
                "encontrado": False,
                "folio": folio,
                "mensaje": f"No encontre el reporte con folio {folio}.",
            }
        )

    return jsonify(
        {
            "encontrado": True,
            "folio": reporte.folio,
            "telefono": reporte.telefono,
            "estatus": reporte.estatus,
            "mensaje": f"El reporte con folio {reporte.folio} tiene estado actual: {reporte.estatus}.",
        }
    )

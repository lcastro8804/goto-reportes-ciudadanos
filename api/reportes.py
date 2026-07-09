from flask import Blueprint, jsonify

from models import Reporte

reportes_api_bp = Blueprint("reportes_api", __name__, url_prefix="/api/reportes")


@reportes_api_bp.get("")
def listar_reportes():
    reportes = Reporte.query.order_by(Reporte.fecha_reporte.desc(), Reporte.id.desc()).all()
    return jsonify([reporte.to_dict() for reporte in reportes])


@reportes_api_bp.get("/<int:reporte_id>")
def detalle_reporte(reporte_id: int):
    reporte = Reporte.query.get_or_404(reporte_id)
    return jsonify(reporte.to_dict())

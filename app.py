import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from api import ivr_bp, reportes_api_bp
from config import Config
from database import db
from models import CANALES_PERMITIDOS, ESTATUS_PERMITIDOS, Reporte, normalizar_telefono


def create_app() -> Flask:
    app = Flask(__name__, instance_path=str(Path(__file__).resolve().parent / "instance"))
    app.config.from_object(Config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(ivr_bp)
    app.register_blueprint(reportes_api_bp)
    register_routes(app)
    return app


def register_routes(app: Flask) -> None:
    @app.get("/")
    def index():
        return render_template("index.html")

    @app.route("/nuevo", methods=["GET", "POST"])
    def nuevo_reporte():
        if request.method == "POST":
            nombre = (request.form.get("nombre") or "").strip()
            telefono = normalizar_telefono(request.form.get("telefono") or "")
            direccion = (request.form.get("direccion") or "").strip()
            tipo_reporte = (request.form.get("tipo_reporte") or "").strip()
            descripcion = (request.form.get("descripcion") or "").strip()
            referencia = (request.form.get("referencia") or "").strip()
            canal_origen = (request.form.get("canal_origen") or "").strip()

            errores = []
            if not nombre:
                errores.append("El nombre es obligatorio.")
            if len(telefono) != 10:
                errores.append("El telefono debe tener 10 digitos.")
            if not direccion:
                errores.append("La direccion es obligatoria.")
            if not tipo_reporte:
                errores.append("El tipo de reporte es obligatorio.")
            if not descripcion:
                errores.append("La descripcion es obligatoria.")
            if canal_origen not in CANALES_PERMITIDOS:
                errores.append("Seleccione un canal de origen valido.")

            if errores:
                for error in errores:
                    flash(error, "error")
                return render_template(
                    "nuevo_reporte.html",
                    canales=CANALES_PERMITIDOS,
                    form_data=request.form,
                )

            reporte = Reporte(
                folio=Reporte.generar_siguiente_folio(),
                nombre=nombre,
                telefono=telefono,
                direccion=direccion,
                tipo_reporte=tipo_reporte,
                descripcion=descripcion,
                referencia=referencia,
                estatus="Nuevo",
                observaciones="Reporte recibido y pendiente de atencion.",
                canal_origen=canal_origen,
            )
            db.session.add(reporte)
            db.session.commit()
            flash("Reporte registrado correctamente.", "success")
            return redirect(url_for("detalle_reporte", reporte_id=reporte.id))

        return render_template(
            "nuevo_reporte.html",
            canales=CANALES_PERMITIDOS,
            form_data={},
        )

    @app.route("/consulta", methods=["GET", "POST"])
    def consulta():
        resultado = None
        criterio = ""
        valor = ""

        if request.method == "POST":
            criterio = request.form.get("criterio", "telefono")
            valor = (request.form.get("valor") or "").strip()

            if criterio == "folio":
                folio = "".join(ch for ch in valor if ch.isdigit())
                resultado = Reporte.query.filter_by(folio=folio).first()
            else:
                telefono = normalizar_telefono(valor)
                resultado = (
                    Reporte.query.filter_by(telefono=telefono)
                    .order_by(Reporte.fecha_reporte.desc(), Reporte.id.desc())
                    .first()
                )

            if not resultado:
                flash("No se encontro un reporte con los datos proporcionados.", "error")

        return render_template(
            "consulta.html",
            resultado=resultado,
            criterio=criterio or "telefono",
            valor=valor,
        )

    @app.get("/dashboard")
    def dashboard():
        reportes = Reporte.query.order_by(Reporte.fecha_reporte.desc(), Reporte.id.desc()).all()
        return render_template("dashboard.html", reportes=reportes)

    @app.route("/reporte/<int:reporte_id>", methods=["GET", "POST"])
    def detalle_reporte(reporte_id: int):
        reporte = Reporte.query.get_or_404(reporte_id)

        if request.method == "POST":
            estatus = (request.form.get("estatus") or "").strip()
            observaciones = (request.form.get("observaciones") or "").strip()

            if estatus not in ESTATUS_PERMITIDOS:
                flash("Seleccione un estatus valido.", "error")
            else:
                reporte.actualizar(estatus=estatus, observaciones=observaciones)
                db.session.commit()
                flash("Reporte actualizado correctamente.", "success")
                return redirect(url_for("detalle_reporte", reporte_id=reporte.id))

        return render_template(
            "detalle_reporte.html",
            reporte=reporte,
            estatus_permitidos=ESTATUS_PERMITIDOS,
        )


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5055))
    print("Servidor iniciado:")
    print("http://127.0.0.1:5055")
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )

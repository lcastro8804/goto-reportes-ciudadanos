import tempfile
import unittest
from datetime import datetime
from pathlib import Path
import sys

from flask import Flask, render_template

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import db
from models import Reporte
from services.gmail_importer import (
    CorreoGoToParseado,
    importar_reportes_desde_correos,
    parsear_correo_goto_html,
)


def construir_html_correo(primer_telefono: str, segundo_telefono: str) -> str:
    return f"""
    <html>
      <body>
        <table>
          <tr><th>Descripci&oacute;n del problema</th><td>Bache frente a escuela</td></tr>
          <tr><th>Direcci&oacute;n</th><td>Av. Central 123</td></tr>
          <tr><th>Nombre completo</th><td>Juan P&eacute;rez</td></tr>
          <tr><th>N&uacute;mero de tel&eacute;fono</th><td>{primer_telefono}</td></tr>
          <tr><th>Referencia adicional</th><td>Frente a la tienda</td></tr>
          <tr><th>Tipo de Reporte</th><td>Bache</td></tr>
          <tr><th>N&uacute;mero de tel&eacute;fono</th><td>{segundo_telefono}</td></tr>
        </table>
      </body>
    </html>
    """


class GmailImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test_reportes.db"
        self.app = Flask(
            __name__,
            template_folder=str(Path(__file__).resolve().parents[1] / "templates"),
        )
        self.app.config.update(
            SECRET_KEY="test-secret",
            SQLALCHEMY_DATABASE_URI=f"sqlite:///{self.database_path.as_posix()}",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        db.init_app(self.app)

        @self.app.get("/")
        def index():
            return "ok"

        @self.app.get("/nuevo")
        def nuevo_reporte():
            return "ok"

        @self.app.post("/importar-correos-goto")
        def importar_correos_goto():
            return "ok"

        @self.app.get("/reporte/<int:reporte_id>")
        def detalle_reporte(reporte_id: int):
            return str(reporte_id)

        @self.app.get("/dashboard")
        def dashboard():
            reportes = Reporte.query.order_by(Reporte.fecha_reporte.desc(), Reporte.id.desc()).all()
            return render_template("dashboard.html", reportes=reportes)

        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self) -> None:
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()
        self.temp_dir.cleanup()

    def test_parsea_dos_campos_de_telefono_en_orden(self) -> None:
        correo = parsear_correo_goto_html(
            construir_html_correo("54-88-100", "1012"),
            email_message_id="msg-1",
            fecha_correo=datetime(2026, 7, 10, 8, 0),
        )

        self.assertEqual(correo.telefono_capturado, "54-88-100")
        self.assertEqual(correo.telefono_origen, "1012")

    def test_importa_correo_y_evitar_duplicado(self) -> None:
        correo = parsear_correo_goto_html(
            construir_html_correo("54881001", "+525527295528"),
            email_message_id="msg-2",
            fecha_correo=datetime(2026, 7, 10, 9, 0),
        )

        with self.app.app_context():
            primer_resultado = importar_reportes_desde_correos([correo])
            segundo_resultado = importar_reportes_desde_correos([correo])

            self.assertEqual(primer_resultado["created"], 1)
            self.assertEqual(primer_resultado["duplicates"], 0)
            self.assertEqual(segundo_resultado["created"], 0)
            self.assertEqual(segundo_resultado["duplicates"], 1)

            reporte = Reporte.query.filter_by(email_message_id="msg-2").first()
            self.assertIsNotNone(reporte)
            self.assertEqual(reporte.telefono, "54881001")
            self.assertEqual(reporte.telefono_capturado, "54881001")
            self.assertEqual(reporte.telefono_origen, "+525527295528")
            self.assertTrue(reporte.folio.isdigit())

            cliente = self.app.test_client()
            respuesta = cliente.get("/dashboard")
            html = respuesta.get_data(as_text=True)
            self.assertEqual(respuesta.status_code, 200)
            self.assertIn("54881001", html)
            self.assertIn(reporte.folio, html)


if __name__ == "__main__":
    unittest.main()

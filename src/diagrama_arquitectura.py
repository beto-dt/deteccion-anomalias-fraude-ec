"""Genera el diagrama de flujo de la arquitectura de streaming (Fase 3).
Uso: python src/diagrama_arquitectura.py  ->  figures/11_arquitectura_streaming.png
"""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "figures", "11_arquitectura_streaming.png")

C = {"src": "#E8EEF7", "kafka": "#FDEBD3", "flink": "#E3F1E4", "ml": "#F3E5F5", "out": "#FCE4E4", "ops": "#EEEEEE"}
fig, ax = plt.subplots(figsize=(16, 9.2))
ax.set_xlim(0, 160); ax.set_ylim(0, 92); ax.axis("off")


def box(x, y, w, h, title, body="", color="#fff", fs=8.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                                fc=color, ec="#444", lw=1))
    ax.text(x + w / 2, y + h - 2.2, title, ha="center", va="top", fontsize=fs + .5, weight="bold")
    if body:
        ax.text(x + w / 2, y + h - 5.6, body, ha="center", va="top", fontsize=fs - 1, linespacing=1.35)


def arrow(x1, y1, x2, y2, label="", style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=12, lw=1.2,
                                 color="#333", linestyle=ls, connectionstyle="arc3,rad=0"))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 1.2, label, ha="center", fontsize=6.8, style="italic")


def group(x, y, w, h, label, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=2", fc=color,
                                ec="#999", lw=1, ls="--", alpha=.45))
    ax.text(x + 1.2, y + h - 1.2, label, fontsize=9.5, weight="bold", va="top", color="#333")


ax.text(80, 90.5, "Pipeline de detección de anomalías en tiempo real – Kafka + Flink", ha="center",
        fontsize=14, weight="bold")

# 1. Fuentes
group(1, 14, 22, 70, "1 · Canales (productores)", C["src"])
for i, (t, b) in enumerate([("App móvil", "SDK + device fingerprint"), ("Banca web", "sesión, IP"),
                            ("Switch POS / ATM", "ISO 8583 → JSON"), ("Pasarela e-commerce", "3-D Secure"),
                            ("Transferencias SPI", "BCE interbancario")]):
    box(3, 70 - i * 12.5, 18, 9, t, b, "#fff")
    arrow(21.4, 74.5 - i * 12.5, 29.6, 62)

# 2. Kafka
group(28, 14, 24, 70, "2 · Ingesta (Apache Kafka)", C["kafka"])
box(30, 56, 20, 18, "topic tx.raw", "key = cliente_id\n24 particiones, RF = 3\nacks = all, idempotente\nretención 7 días", "#fff")
box(30, 38, 20, 13, "Schema Registry", "contrato Avro versionado\n(compatibilidad BACKWARD)", "#fff")
box(30, 18, 20, 15, "clientes.cdc", "Debezium desde core\nbancario (perfil, límites,\nprovincia de domicilio)", "#fff")
arrow(50.4, 65, 58, 65, "consume")
arrow(50.4, 25, 58, 33, "broadcast")

# 3. Flink
group(56, 6, 52, 78, "3 · Procesamiento (Apache Flink, exactly-once)", C["flink"])
box(58, 66, 22, 13, "① Validación + DLQ", "deserializa, valida esquema\ninválidos → tx.dlq", "#fff")
box(83, 66, 23, 13, "② keyBy(cliente_id)", "estado RocksDB: últimas 8 tx,\nmedia de monto, último ts", "#fff")
box(83, 46, 23, 16, "③ Ventanas", "deslizante 1 h / paso 1 min:\nvelocidad (n_tx_1h)\ntumbling 24 h: perfil diario", "#fff")
box(58, 46, 22, 16, "④ Micro-lote de inferencia", "dispara con 10.000 tx\nO cada 200 ms (lo primero)\n→ vector de 51 variables", "#fff")
box(58, 26, 22, 16, "⑤ Inferencia paralela", "IF · OC-SVM · AE · LSTM-AE\n(ONNX Runtime embebido)\nensamble por percentiles", C["ml"])
box(83, 26, 23, 16, "⑥ Umbral adaptativo", "percentil móvil por\nsegmento × canal (24 h)\n+ retroalimentación analistas", C["ml"])
box(58, 9, 48, 13, "⑦ Motor de decisión", "reglas regulatorias duras (perfil transaccional, límites) + puntaje\n"
    "≥ umbral alto → bloquear · zona gris → OTP (step-up) · resto → aprobar", "#fff")
arrow(80.4, 72.5, 82.6, 72.5); arrow(94.5, 65.6, 94.5, 62.4); arrow(82.6, 54, 80.4, 54, "variables")
arrow(69, 45.6, 69, 42.4); arrow(80.4, 34, 82.6, 34, "puntaje"); arrow(94.5, 25.6, 94.5, 22.4)

# 4. Salidas
group(112, 30, 46, 54, "4 · Salidas y alertas", C["out"])
box(114, 68, 20, 11, "topic tx.scored", "puntaje + decisión\n+ top-3 SHAP", "#fff")
box(136, 68, 20, 11, "topic fraude.alertas", "prioridad P1–P3", "#fff")
box(114, 52, 20, 12, "Autorizador", "respuesta al canal\n< 300 ms (p99)", "#fff")
box(136, 52, 20, 12, "Gestión de casos", "cola de analistas\nde Prevención de Fraude", "#fff")
box(114, 34, 20, 13, "Notificación cliente", "push / SMS / correo\n(≥ 2 canales)", "#fff")
box(136, 34, 20, 13, "SIEM / UAFE", "correlación seguridad;\nreporte de inusuales", "#fff")
arrow(106.4, 18, 113.6, 72, "")
arrow(134.4, 73.5, 135.6, 73.5); arrow(124, 67.6, 124, 64.4); arrow(146, 67.6, 146, 64.4)
arrow(146, 51.6, 146, 47.4); arrow(140, 51.6, 128, 47.4)

# 5. MLOps
group(112, 2, 46, 24, "5 · MLOps y gobierno", C["ops"])
box(113.5, 5, 13.5, 16, "Data lake", "Iceberg / S3\nhistórico +\netiquetas", "#fff", fs=7.8)
box(128.5, 5, 13.5, 16, "Registro", "MLflow:\nversión,\nmétricas, EIPD", "#fff", fs=7.8)
box(143.5, 5, 13.5, 16, "Monitoreo", "Prometheus /\nGrafana: p99,\nPSI de drift", "#fff", fs=7.8)
arrow(146, 33.6, 120, 21.4, "etiquetas confirmadas", ls="--")
arrow(135, 21.4, 80.4, 27, "despliegue (A/B, shadow)", ls="--")

plt.savefig(OUT, dpi=170, bbox_inches="tight")
print("Diagrama guardado en", OUT)

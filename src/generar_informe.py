import json, os, re
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image, Table,
                                TableStyle, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(f"{REPO}/results/resultados.json", encoding="utf-8"))
LAT = pd.read_csv(f"{REPO}/results/latencia_vs_batch.csv")
FD = "/usr/share/fonts/truetype/dejavu/"
for n, f in [("Serif", "DejaVuSerif.ttf"), ("Serif-B", "DejaVuSerif-Bold.ttf"), ("Serif-I", "DejaVuSerif-Italic.ttf"),
             ("Serif-BI", "DejaVuSerif-BoldItalic.ttf"), ("Sans", "DejaVuSans.ttf"), ("Sans-B", "DejaVuSans-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(n, FD + f))
addMapping("Serif", 0, 0, "Serif"); addMapping("Serif", 1, 0, "Serif-B"); addMapping("Serif", 0, 1, "Serif-I"); addMapping("Serif", 1, 1, "Serif-BI")
addMapping("Sans", 1, 0, "Sans-B"); addMapping("Sans", 0, 0, "Sans")

AZUL = colors.HexColor("#2E2A6E")
sty = {
    "body": ParagraphStyle("body", fontName="Serif", fontSize=10.3, leading=15.2, alignment=TA_JUSTIFY, spaceAfter=7),
    "h1": ParagraphStyle("h1", fontName="Sans-B", fontSize=14.5, leading=18, textColor=AZUL, spaceBefore=12, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="Sans-B", fontSize=11.5, leading=15, textColor=AZUL, spaceBefore=9, spaceAfter=5),
    "cap": ParagraphStyle("cap", fontName="Serif-I", fontSize=8.6, leading=11.5, alignment=TA_LEFT, spaceAfter=10, textColor=colors.HexColor("#333")),
    "cell": ParagraphStyle("cell", fontName="Sans", fontSize=7.8, leading=9.6),
    "cellb": ParagraphStyle("cellb", fontName="Sans-B", fontSize=7.8, leading=9.6, textColor=colors.white),
    "ref": ParagraphStyle("ref", fontName="Serif", fontSize=9.4, leading=13, leftIndent=0.9 * cm, firstLineIndent=-0.9 * cm, spaceAfter=5, alignment=TA_LEFT),
    "title": ParagraphStyle("title", fontName="Sans-B", fontSize=19, leading=25, alignment=TA_CENTER, textColor=AZUL),
    "center": ParagraphStyle("center", fontName="Serif", fontSize=11, leading=16, alignment=TA_CENTER),
    "abs": ParagraphStyle("abs", fontName="Serif", fontSize=9.8, leading=14, alignment=TA_JUSTIFY, leftIndent=1 * cm, rightIndent=1 * cm),
}
story, WORDS = [], []
nfig = [0]; ntab = [0]


def P(t, s="body"):
    if s in ("body", "abs"):
        WORDS.append(re.sub(r"<[^>]+>", "", t))
    story.append(Paragraph(t, sty[s]))


def H1(t): story.append(Paragraph(t, sty["h1"])); WORDS.append(t)
def H2(t): story.append(Paragraph(t, sty["h2"])); WORDS.append(t)


def FIG(name, cap, w=16):
    from PIL import Image as PI
    path = f"{REPO}/figures/{name}"
    iw, ih = PI.open(path).size
    nfig[0] += 1
    story.append(KeepTogether([Image(path, width=w * cm, height=w * cm * ih / iw),
                               Paragraph(f"<b>Figura {nfig[0]}.</b> {cap}", sty["cap"])]))
    return nfig[0]


def TAB(title, rows, widths, nota=None):
    ntab[0] += 1
    data = [[Paragraph(str(c), sty["cellb"]) for c in rows[0]]] + [[Paragraph(str(c), sty["cell"]) for c in r] for r in rows[1:]]
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F0F8")]),
                           ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#BBBBBB")),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    items = [Paragraph(f"<b>Tabla {ntab[0]}.</b> <i>{title}</i>", sty["cap"]), t]
    if nota:
        items.append(Paragraph(f"<i>Nota.</i> {nota}", sty["cap"]))
    else:
        items.append(Spacer(1, 8))
    story.append(KeepTogether(items))
    return ntab[0]


def f2(x, d=3): return f"{x:.{d}f}".replace(".", ",")
def pct(x, d=1): return f"{100 * x:.{d}f}".replace(".", ",") + " %"
def ms(x): return f"{x:,.0f}".replace(",", ".") + " ms"
def num(x): return f"{x:,.0f}".replace(",", ".")


E, S, T, ENS, SUP = R["eda"], R["split"], R["tabla"], R["ensamble"], R["supervisado_referencia"]
RT = R["recall_tipologia"]
IF, LOF, AE, LS, OC = T["Isolation Forest"], T["LOF"], T["Autoencoder denso"], T["LSTM-Autoencoder"], T["One-Class SVM (Nyström)"]
ENSN = "Ensamble (IF + OC-SVM + AE + LSTM-AE)"
CM = R["cm_mejor"]
lat10k = LAT.loc[LAT.batch == 10000].iloc[0]
lat1k = LAT.loc[LAT.batch == 1000].iloc[0]
lat2500 = LAT.loc[LAT.batch == 2500].iloc[0]
lat50k = LAT.loc[LAT.batch == 50000].iloc[0]

# ------------------------------------------------------------------ PORTADA
story += [Spacer(1, 2.2 * cm), Paragraph("UNIVERSIDAD REGIONAL AUTÓNOMA DE LOS ANDES – UNIANDES", sty["center"]),
          Paragraph("Maestría en Big Data y Ciencia de Datos (mención Inteligencia Artificial)", sty["center"]),
          Spacer(1, 2 * cm),
          Paragraph("Implementación y evaluación de un sistema de detección de anomalías con aprendizaje automático "
                    "en flujos de datos financieros del contexto ecuatoriano", sty["title"]),
          Spacer(1, .8 * cm), Paragraph("Informe técnico · Actividad sumativa 1 – Semana 2", sty["center"]),
          Spacer(1, 3 * cm), Paragraph("<b>Autor:</b> Luis Alberto De La Torre Durán", sty["center"]),
          Paragraph("<b>Repositorio:</b> https://github.com/beto-dt/deteccion-anomalias-fraude-ec", sty["center"]),
          Spacer(1, .5 * cm), Paragraph("Quito, noviembre de 2026", sty["center"]), PageBreak()]

# ------------------------------------------------------------------ RESUMEN
H1("Resumen")
P(f"Este informe desarrolla un sistema de detección de anomalías para las transacciones digitales de un banco ecuatoriano "
  f"que procesa en promedio 3,5 millones de operaciones diarias y exige una latencia máxima de 500 ms por lote de 10.000 "
  f"transacciones. Se construyó un conjunto de datos sintético de {num(E['n_total'])} transacciones de {num(E['n_clientes'])} "
  f"clientes con patrones bancarios locales y cuatro tipologías de fraude (toma de cuenta, <i>card testing</i>, <i>SIM swap</i> "
  f"y clonación en cajeros), con una tasa de fraude de {pct(E['tasa_fraude'], 2)}. Se implementaron y compararon cinco "
  f"detectores no supervisados (Isolation Forest, Local Outlier Factor, Autoencoder denso, LSTM-Autoencoder y One-Class SVM "
  f"aproximado con Nyström) bajo una partición temporal y un protocolo de aprendizaje de una clase. El mejor detector individual "
  f"que cumple el acuerdo de nivel de servicio fue Isolation Forest (AUC-PR = {f2(IF['AUC_PR'])}; {ms(IF['Latencia_ms_10k'])} por "
  f"lote), mientras que LOF obtuvo el mayor AUC-PR individual ({f2(LOF['AUC_PR'])}) pero incumplió la latencia. Un ensamble por "
  f"promedio de percentiles de cuatro detectores alcanzó AUC-PR = {f2(ENS['AUC_PR'])} y F1 = {f2(ENS['F1_fraude'])}, manteniéndose "
  f"bajo el límite si sus componentes se ejecutan en paralelo. Se diseñó un <i>pipeline</i> de <i>streaming</i> con Apache Kafka y "
  f"Apache Flink y se mostró que el factor dominante de la latencia percibida no es la inferencia sino el tiempo de llenado del "
  f"lote. La explicabilidad con SHAP permitió traducir las alertas a variables de negocio, base para atender el derecho previsto "
  f"en el artículo 20 de la Ley Orgánica de Protección de Datos Personales.", "abs")
story.append(Spacer(1, 6))
P("<b>Palabras clave:</b> detección de anomalías, fraude electrónico, Isolation Forest, autoencoder, Apache Flink, SHAP, LOPDP.", "abs")

# ------------------------------------------------------------------ 1. INTRODUCCIÓN
H1("1. Introducción")
P("La detección de anomalías en flujos continuos es uno de los problemas más exigentes en la intersección entre inteligencia "
  "artificial y <i>big data</i>: los eventos llegan sin pausa, las clases están extremadamente desbalanceadas, el comportamiento "
  "de los defraudadores cambia para evadir los controles y cada decisión debe tomarse en milisegundos (Chandola et al., 2009; "
  "Pang et al., 2021). En el sector financiero el problema añade una dimensión regulatoria: las entidades controladas por la "
  "Superintendencia de Bancos (SB) deben monitorear las transacciones de sus canales electrónicos contra el perfil transaccional "
  "de cada cliente y, al mismo tiempo, tratar los datos personales conforme a la Ley Orgánica de Protección de Datos Personales "
  "(LOPDP, 2021).")
P("El caso planteado ubica al autor en el equipo de ciencia de datos de un banco ecuatoriano regulado por la SB que procesa "
  "3,5 millones de transacciones diarias por canales digitales y que, en los últimos seis meses, registró un incremento del 23 % "
  "en intentos de fraude electrónico. Según el planteamiento del caso, la SB emitió en 2022 directrices sobre el uso de "
  "tecnología analítica avanzada para la prevención del lavado de activos y del fraude electrónico, enmarcadas en la Ley "
  "Orgánica de Prevención, Detección y Erradicación del Delito de Lavado de Activos y del Financiamiento de Delitos. El área de "
  "Seguridad Informática solicita un sistema automatizado capaz de operar en <i>streaming</i> con una latencia máxima de 500 ms "
  "por lote de 10.000 transacciones.")
P("Los objetivos del trabajo son: (a) implementar y comparar algoritmos de detección de anomalías sobre transacciones "
  "financieras; (b) evaluarlos con métricas apropiadas para datos desbalanceados; (c) diseñar un <i>pipeline</i> de detección en "
  "tiempo real considerando sus restricciones de latencia; y (d) interpretar los resultados con técnicas de explicabilidad y "
  "vincularlos con el marco normativo ecuatoriano. El código, los datos y las figuras se encuentran en el repositorio indicado "
  "en la portada; el cuaderno <i>deteccion_anomalias_fraude_ec.ipynb</i> reproduce todos los resultados con la semilla 42.")

# ------------------------------------------------------------------ 2. MARCO
H1("2. Fundamentos")
P("Una anomalía es una observación que no se ajusta al comportamiento esperado de la mayoría (Chandola et al., 2009). En "
  "fraude transaccional conviven tres tipos: anomalías puntuales (una transferencia por un monto atípico), contextuales (un monto "
  "normal a una hora o en un lugar inusual para ese cliente) y colectivas (una ráfaga de microcompras que individualmente parecen "
  "inocuas). Esta distinción orienta la selección de modelos: los métodos tabulares capturan bien las anomalías puntuales, "
  "mientras que las contextuales y colectivas requieren variables de comportamiento o modelos secuenciales.")
P("<b>Isolation Forest</b> (Liu et al., 2008) parte de que las anomalías son pocas y diferentes, por lo que se aíslan con menos "
  "particiones aleatorias; su costo es casi lineal y no requiere distancias. <b>Local Outlier Factor</b> (Breunig et al., 2000) "
  "compara la densidad local de un punto con la de sus vecinos y detecta anomalías relativas a su vecindario, a costa de búsquedas "
  "de vecinos más cercanos. <b>One-Class SVM</b> (Schölkopf et al., 2001) estima la frontera que encierra la masa de datos "
  "normales; su versión con kernel no escala a cientos de miles de filas, por lo que se emplea la aproximación de Nyström "
  "(Williams y Seeger, 2001). Los <b>autoencoders</b> aprenden una representación comprimida de los datos y reconstruyen mal lo "
  "que no vieron durante el entrenamiento (Hinton y Salakhutdinov, 2006); su variante recurrente con celdas LSTM (Hochreiter y "
  "Schmidhuber, 1997) incorpora la dimensión temporal de la secuencia de transacciones de cada cliente.")
P("Con clases desbalanceadas la exactitud y el AUC-ROC son engañosos, porque la gran masa de verdaderos negativos infla la "
  "tasa de falsos positivos aparente. Saito y Rehmsmeier (2015) demostraron que la curva Precision-Recall y su área (AUC-PR o "
  "<i>average precision</i>) son más informativas en este escenario, ya que su línea base es la prevalencia de la clase "
  "positiva y no 0,5. Dal Pozzolo et al. (2018) añaden que en fraude real las etiquetas llegan con retraso y de forma sesgada "
  "(solo se confirma lo que se investiga), lo que favorece enfoques no supervisados o semisupervisados en la primera línea de "
  "defensa.")

# ------------------------------------------------------------------ 3. METODOLOGÍA
H1("3. Metodología y datos")
H2("3.1 Selección y generación del conjunto de datos")
P("De las tres opciones del enunciado se eligió la (c), un conjunto sintético. El conjunto <i>Credit Card Fraud Detection</i> de "
  "la ULB contiene 28 componentes principales anónimas, lo que impide crear variables de comportamiento y vuelve inútil la "
  "explicabilidad frente a un regulador; IEEE-CIS describe comercio electrónico estadounidense. Un generador propio, en la línea "
  "del <i>Synthetic Data Vault</i> (Patki et al., 2016), permite reproducir la operación de un banco ecuatoriano y, al no contener "
  "datos de personas reales, elimina el riesgo de tratamiento indebido de datos personales en un entorno académico.")
P(f"El generador (Faker + NumPy) crea {num(5000)} clientes con segmento (masivo, preferente, pyme), provincia de domicilio "
  f"ponderada por población en las 24 provincias, edad, antigüedad, saldo y preferencias de canal. Sobre ellos se simulan "
  f"transacciones entre el 1 de septiembre y el 31 de octubre de 2026 en cinco canales (app móvil, banca web, POS, cajero "
  f"automático y comercio electrónico), con montos en dólares, picos de demanda en quincena y fin de mes, el feriado del 9 de "
  f"octubre, transferencias interbancarias, recargas de telefonía y pago de servicios básicos. Se inyectaron cuatro tipologías "
  f"de fraude asignadas a clientes reales del universo simulado, para que convivan con su historial normal. La Tabla 1 resume "
  f"las tipologías y su volumen.")
tip = E["tipologias"]
TAB("Tipologías de fraude inyectadas", [
    ["Tipología", "n", "Patrón simulado", "Señales esperadas"],
    ["Toma de cuenta (ATO)", tip["account_takeover"], "1–4 transferencias nocturnas que vacían 25–90 % del saldo; 25 % de casos “silenciosos” con monto moderado",
     "dispositivo y beneficiario nuevos, intentos fallidos de acceso"],
    ["Card testing", tip["card_testing"], "3–10 microcompras (0,5–5 USD) internacionales en minutos, a veces seguidas de una compra grande",
     "frecuencia en 1 h, comercio internacional"],
    ["SIM swap", tip["sim_swap"], "transferencia interbancaria tras cambio de clave en las últimas 6 h",
     "horas desde cambio de clave, dispositivo nuevo"],
    ["Skimming en cajero", tip["skimming_atm"], "retiros de 200–500 USD en otra provincia, frecuentemente de madrugada",
     "distancia y provincia distinta a la habitual"],
], [3.2, 1.2, 6.6, 5])

H2("3.2 Análisis exploratorio de datos")
P(f"El conjunto final tiene {num(E['n_total'])} transacciones, de las cuales {num(E['n_fraude'])} son fraudulentas "
  f"({pct(E['tasa_fraude'], 2)}), es decir, un desbalance aproximado de 1:{round(1 / E['tasa_fraude'])} (Figura 1). La tasa es "
  f"deliberadamente superior a la de un banco real (habitualmente inferior al 0,2 %) para disponer de suficientes positivos en "
  f"el conjunto de prueba; los resultados absolutos de precisión deben leerse con esa salvedad.")
FIG("01_clases.png", "Distribución de clases en escala logarítmica y número de fraudes por tipología.", 15)
P(f"<b>Valores faltantes.</b> Tres variables presentan ausencias (Figura 2). La categoría de comercio falta en "
  f"{E['faltantes_pct']['categoria_comercio']:.1f} % de las filas, pero no es un dato perdido: es estructuralmente no aplicable "
  f"a transferencias y retiros, por lo que se imputa con la categoría explícita <i>no_aplica</i>. La distancia a la ubicación "
  f"habitual falta en {E['faltantes_pct']['distancia_habitual_km']:.1f} % de las filas y es más frecuente en banca web, que no "
  f"geolocaliza al usuario; al depender del canal es un faltante de tipo MAR, por lo que además de imputarla con la mediana se "
  f"agrega un indicador binario de ausencia. La edad falta en {E['faltantes_pct']['edad_cliente']:.1f} % de los registros.")
FIG("02_faltantes.png", "Porcentaje de valores faltantes por variable.", 11)
P(f"<b>Valores atípicos estructurales.</b> Se encontraron {E['montos_negativos']} montos negativos, que corresponden a "
  f"reversos de compra válidos y se conservan con la bandera <i>es_reverso</i>, y {E['edades_invalidas']} edades fuera del rango "
  f"18–100 años, que son errores de captura y se convierten en faltantes. Con el criterio Q3 + 3·IQR, {pct(E['pct_outliers_iqr_monto'])} "
  f"de los montos son extremos; dentro de ese grupo la tasa de fraude sube a {pct(E['tasa_fraude_en_outliers'])}, más de tres "
  f"veces la base. Por eso los montos extremos no se eliminan: eliminarlos borraría precisamente la señal buscada. La Figura 3 "
  f"muestra que las distribuciones del monto se superponen ampliamente entre clases, por lo que el monto por sí solo no separa "
  f"el fraude; las diferencias aparecen al condicionar por canal.")
FIG("03_montos.png", "Distribución de log(1+|monto|) por clase y por canal.", 16)
P("<b>Variables de comportamiento.</b> A partir de los campos crudos se calcularon variables causales, es decir, que usan solo "
  "el pasado de cada cliente: desvío del monto respecto de la media histórica del cliente, número de transacciones del cliente "
  "en la última hora, segundos desde su transacción anterior, razón monto/saldo, codificación cíclica de la hora y banderas de "
  "quincena, fin de semana, feriado y provincia distinta a la de domicilio. Calcularlas de forma causal evita la fuga de "
  "información y replica lo que un operador con estado en Flink puede calcular en producción.")
ct = E["corr_top"]
P(f"<b>Correlación.</b> La matriz de Spearman (Figura 4) muestra que ninguna variable aislada se correlaciona fuertemente con "
  f"la etiqueta: las más asociadas son dispositivo nuevo (ρ = {f2(ct['dispositivo_nuevo'], 2)}), beneficiario nuevo "
  f"(ρ = {f2(ct['beneficiario_nuevo'], 2)}), intentos fallidos (ρ = {f2(ct['intentos_fallidos_24h'], 2)}) y transacción "
  f"internacional (ρ = {f2(ct['es_internacional'], 2)}). Esto confirma que el fraude se manifiesta como una combinación de "
  f"señales débiles, justo el escenario donde los modelos multivariados aportan valor frente a reglas univariadas. El único par "
  f"redundante es log(monto) con el desvío del monto del cliente (ρ = {f2(R['eda']['pares_alta_corr'][0][2], 2)}); se conservan "
  f"ambos porque codifican información distinta (magnitud absoluta y anomalía relativa al cliente) y los modelos empleados no "
  f"sufren de multicolinealidad como una regresión lineal. La Figura 5 muestra que la tasa de fraude se dispara de madrugada y "
  f"es mayor en comercio electrónico y cajeros.")
FIG("04_correlacion.png", "Matriz de correlación de Spearman entre las variables de modelado y la etiqueta.", 14.5)
FIG("05_hora_canal.png", "Tasa de fraude por hora del día y por canal.", 15)

H2("3.3 Pipeline de preprocesamiento")
P("La Tabla 2 resume las decisiones de preprocesamiento y su justificación. Todas las transformaciones se ajustan solo con el "
  "bloque de entrenamiento y se aplican después a validación y prueba, para no filtrar estadísticas del futuro.")
TAB("Decisiones del pipeline de preprocesamiento", [
    ["Paso", "Decisión", "Justificación"],
    ["Partición", f"Temporal 70/10/20: entrenamiento hasta el {S['corte_train'][:10]}, validación hasta el {S['corte_val'][:10]}, prueba en adelante",
     "El modelo siempre predice el futuro; un muestreo aleatorio filtra información temporal y sobreestima el desempeño."],
    ["Numéricas", "log(1+x) en montos, saldos y tiempos; imputación por mediana con indicador de faltante; StandardScaler",
     "La mediana es robusta a colas largas; el estandarizado es imprescindible para LOF, OC-SVM y redes neuronales."],
    ["Categóricas", "Imputación constante no_aplica; One-Hot con handle_unknown = ignore",
     "Cardinalidad baja; preserva el significado del faltante estructural y no falla si aparece una categoría nueva en streaming."],
    ["Desbalance", "Aprendizaje de una clase (entrenar solo con legítimas) y umbral elegido en validación por máximo F1",
     "SMOTE interpola fraudes sintéticos y contaminaría el concepto de normalidad que el detector debe aprender."],
], [2.4, 6.4, 7.2])
P(f"El resultado es un espacio de {S['n_features']} variables. Los bloques quedaron con {num(S['train'])}, {num(S['val'])} y "
  f"{num(S['test'])} transacciones, con {S['fraude_train']}, {S['fraude_val']} y {S['fraude_test']} fraudes respectivamente. "
  f"Sobre la estrategia de desbalance conviene precisar el razonamiento. SMOTE (Chawla et al., 2002) genera ejemplos minoritarios "
  f"sintéticos interpolando entre vecinos y es útil para clasificadores supervisados. En detección de anomalías, en cambio, el "
  f"modelo aprende qué es normal; si se le entregan fraudes, sintéticos o reales, se desplaza su frontera. Por ello el desbalance "
  f"se gestiona por diseño: entrenamiento con legítimas y calibración del umbral sobre la curva Precision-Recall de validación. "
  f"Para contrastar empíricamente SMOTE y la ponderación de clases se entrenó además un modelo supervisado de referencia "
  f"(sección 5.3).")

# ------------------------------------------------------------------ 4. MODELOS
H1("4. Implementación de los modelos")
P("Todos los detectores comparten el mismo protocolo: entrenamiento solo con transacciones legítimas del bloque de "
  "entrenamiento, puntaje continuo de anomalía (mayor es más anómalo), umbral elegido en validación maximizando el F1 de la clase "
  "fraude, evaluación en el bloque de prueba y medición de latencia para un lote de 10.000 transacciones, incluido el "
  "preprocesamiento (mediana de cinco corridas). La Tabla 3 documenta arquitectura e hiperparámetros.")
A = R["arquitecturas"]
TAB("Arquitectura e hiperparámetros de los detectores", [
    ["Modelo", "Arquitectura", "Hiperparámetros y justificación"],
    ["Isolation Forest", A["Isolation Forest"]["arquitectura"], A["Isolation Forest"]["hiper"] + ". Submuestras pequeñas reducen el enmascaramiento de anomalías agrupadas."],
    ["LOF (novedad)", A["LOF"]["arquitectura"], A["LOF"]["hiper"] + ". k mayor que el tamaño típico de un episodio para que los fraudes en ráfaga no se protejan entre sí."],
    ["Autoencoder denso", A["Autoencoder denso"]["arquitectura"], A["Autoencoder denso"]["hiper"] + ". El cuello de 8 neuronas y la regularización impiden aprender la identidad."],
    ["LSTM-Autoencoder", A["LSTM-Autoencoder"]["arquitectura"], A["LSTM-Autoencoder"]["hiper"] + ". El puntaje es el error de reconstrucción del último paso, condicionado por su contexto."],
    ["One-Class SVM", A["One-Class SVM (Nyström)"]["arquitectura"], A["One-Class SVM (Nyström)"]["hiper"] + ". Nyström vuelve lineal el costo del kernel RBF."],
], [2.7, 5.3, 8])
P("El LSTM-Autoencoder requiere una representación secuencial. Para cada transacción se construyó la secuencia de las últimas "
  "ocho transacciones del mismo cliente, incluida la actual, con relleno de ceros cuando el historial es más corto. Esta "
  "construcción es exactamente la que mantendría un operador <i>keyed</i> de Flink en su estado. El One-Class SVM clásico con "
  "kernel RBF, de costo entre cuadrático y cúbico en el número de observaciones, se reemplazó por la combinación de la "
  "aproximación de Nyström con 300 componentes y un SVM de una clase lineal entrenado por descenso estocástico, lo que conserva "
  "una frontera no lineal con costo lineal.")

# ------------------------------------------------------------------ 5. RESULTADOS
H1("5. Resultados")
H2("5.1 Tabla comparativa")
orden = ["Isolation Forest", "One-Class SVM (Nyström)", "Autoencoder denso", "LSTM-Autoencoder", "LOF"]
rows = [["Modelo", "Prec.", "Recall", "F1", "F1 macro", "F1 pond.", "AUC ROC", "AUC PR", "ms", "SLA"]]
for k in orden:
    m = T[k]
    rows.append([k, f2(m["Precision"]), f2(m["Recall"]), f2(m["F1_fraude"]), f2(m["F1_macro"]), f2(m["F1_ponderado"]),
                 f2(m["AUC_ROC"]), f"<b>{f2(m['AUC_PR'])}</b>", num(m["Latencia_ms_10k"]), "Sí" if m["Cumple_500ms"] else "No"])
rows.append([ENSN.replace("Ensamble ", "Ensamble<br/>"), f2(ENS["Precision"]), f2(ENS["Recall"]), f2(ENS["F1_fraude"]), f2(ENS["F1_macro"]),
             f2(ENS["F1_ponderado"]), f2(ENS["AUC_ROC"]), f"<b>{f2(ENS['AUC_PR'])}</b>",
             f"{num(ENS['Latencia_ms_10k_paralelo'])}*", "Sí*"])
TAB("Resultados en el bloque de prueba (futuro no visto)", rows, [3.3, 1.45, 1.5, 1.3, 1.45, 1.45, 1.45, 1.45, 1.4, 1.1],
    f"Prec. = precisión de la clase fraude; F1 = F1 de la clase fraude; ms = latencia por lote de 10.000. Prevalencia de fraude en prueba: {pct(S['fraude_test'] / S['test'], 2)} (línea base del AUC-PR). Latencias medidas en un contenedor "
    f"de un solo vCPU. *Latencia del ensamble con sus componentes en paralelo (máximo de los componentes); en ejecución secuencial "
    f"sería {num(ENS['Latencia_ms_10k'])} ms.")
P(f"La lectura de la Tabla 4 debe partir de una observación metodológica: el F1 ponderado y el AUC-ROC de todos los modelos son "
  f"altos (por encima de 0,98 y 0,86 respectivamente) y casi indistinguibles, lo que ilustra por qué no son métricas adecuadas "
  f"para este problema. El F1 ponderado está dominado por la clase legítima, que el modelo acierta casi siempre; el AUC-ROC se "
  f"beneficia de los más de 30.000 verdaderos negativos. En cambio, el AUC-PR, cuya línea base es la prevalencia "
  f"({pct(S['fraude_test'] / S['test'], 2)}), discrimina con claridad: va de {f2(LS['AUC_PR'])} para el LSTM-Autoencoder a "
  f"{f2(LOF['AUC_PR'])} para LOF, es decir, entre 25 y 60 veces mejor que el azar. El F1 macro, que promedia ambas clases con "
  f"igual peso, ofrece una vista intermedia útil para comunicar a audiencias no técnicas.")
P(f"LOF obtuvo el mejor desempeño individual (AUC-PR = {f2(LOF['AUC_PR'])}, F1 = {f2(LOF['F1_fraude'])}), pero su inferencia "
  f"tardó {ms(LOF['Latencia_ms_10k'])} por lote, casi cuatro veces el límite, porque cada transacción requiere buscar sus 35 "
  f"vecinos entre 40.000 puntos de referencia. Aplicando el criterio de selección —máximo AUC-PR entre los modelos que cumplen "
  f"500 ms— el modelo con mejor relación precisión/latencia es <b>Isolation Forest</b> (AUC-PR = {f2(IF['AUC_PR'])}, "
  f"{ms(IF['Latencia_ms_10k'])}), seguido muy de cerca por el One-Class SVM aproximado (AUC-PR = {f2(OC['AUC_PR'])}), que es "
  f"unas cinco veces más rápido ({ms(OC['Latencia_ms_10k'])}). Si el banco necesitara escalar a volúmenes mucho mayores sin "
  f"aumentar infraestructura, el OC-SVM sería la alternativa natural. Con el umbral de validación, Isolation Forest detectó "
  f"{CM[1][1]} de {CM[1][0] + CM[1][1]} fraudes con {CM[0][1]} falsas alarmas sobre {num(CM[0][0] + CM[0][1])} transacciones "
  f"legítimas: una tasa de falsos positivos de {pct(CM[0][1] / (CM[0][0] + CM[0][1]), 2)}, manejable para un equipo de analistas.")
FIG("06_pr_roc.png", "Curvas Precision-Recall y ROC en el bloque de prueba. La línea discontinua del panel izquierdo es la prevalencia (azar).", 16)

H2("5.2 Desempeño por tipología y ensamble")
P(f"Un mismo F1 puede esconder que un modelo es excelente en una tipología y ciego en otra. La Figura 7 muestra el recall por "
  f"tipología con el umbral de validación. Los modelos tabulares detectan bien la toma de cuenta y el <i>SIM swap</i>, cuyas "
  f"señales (dispositivo y beneficiario nuevos, intentos fallidos, cambio reciente de clave) son raras en la población normal. "
  f"El <i>card testing</i> es más difícil porque sus microcompras se parecen a suscripciones legítimas a plataformas "
  f"internacionales; LOF es el que mejor lo capta ({pct(RT['LOF']['card_testing'], 0)}) gracias a su sensibilidad a la densidad "
  f"local. La clonación en cajeros casi pasa desapercibida para los modelos tabulares (entre {pct(RT['Autoencoder denso']['skimming_atm'], 0)} "
  f"y {pct(RT['Isolation Forest']['skimming_atm'], 0)}), porque un retiro en otra provincia es indistinguible del de un cliente "
  f"que viaja. Solo el LSTM-Autoencoder, que ve la secuencia, alcanza {pct(RT['LSTM-Autoencoder']['skimming_atm'], 0)}: el "
  f"problema no es la transacción sino el cambio abrupto respecto a las anteriores.")
FIG("07_recall_tipologia.png", "Recall por tipología de fraude y modelo, con el umbral fijado en validación.", 14)
P(f"Esta complementariedad motivó un ensamble por promedio de percentiles: cada puntaje se transforma en su percentil respecto "
  f"de la distribución de validación (normalización que no usa etiquetas) y se promedian los cuatro detectores que cumplen el "
  f"límite de latencia. El ensamble obtuvo AUC-PR = {f2(ENS['AUC_PR'])} y F1 = {f2(ENS['F1_fraude'])}, superando incluso a LOF, "
  f"con un recall de {pct(RT[ENSN]['sim_swap'], 0)} en <i>SIM swap</i> y {pct(RT[ENSN]['account_takeover'], 0)} en toma de "
  f"cuenta. Como en Flink los detectores pueden ejecutarse como operadores paralelos sobre el mismo flujo, la latencia relevante "
  f"es la del componente más lento ({ms(ENS['Latencia_ms_10k_paralelo'])}), dentro del límite. Por ello la recomendación final "
  f"es desplegar el ensamble, manteniendo Isolation Forest como modelo de respaldo si un componente falla.")

H2("5.3 Referencia supervisada: SMOTE frente a ponderación de clases")
sw, sm = SUP["HGB + ponderación de clases"], SUP["HGB + SMOTE"]
P(f"Un clasificador <i>HistGradientBoosting</i> entrenado con las etiquetas alcanza AUC-PR = {f2(sw['AUC_PR'])} con ponderación de "
  f"clases y {f2(sm['AUC_PR'])} con SMOTE (razón 1:10), con F1 de {f2(sw['F1_fraude'])} y {f2(sm['F1_fraude'])}. La diferencia "
  f"entre ambas estrategias es marginal, mientras que SMOTE duplica el tiempo de entrenamiento y la latencia; por simplicidad y "
  f"menor riesgo de sobreajuste a fraudes sintéticos se prefiere la ponderación de clases. La gran brecha con los detectores no "
  f"supervisados no invalida a estos últimos: el modelo supervisado solo reconoce tipologías que ya vio y depende de etiquetas "
  f"que en un banco llegan con días o semanas de retraso, cuando el cliente reclama (Dal Pozzolo et al., 2018). Además, en datos "
  f"sintéticos las tipologías son más regulares que en la realidad, lo que favorece al aprendizaje supervisado. La arquitectura "
  f"propuesta usa ambos: detectores no supervisados como primera línea, capaces de alertar sobre patrones nuevos, y un modelo "
  f"supervisado que se incorpora a medida que maduran las etiquetas confirmadas por los analistas.")

# ------------------------------------------------------------------ 6. STREAMING
H1("6. Diseño del pipeline de streaming")
P("La Figura 8 presenta la arquitectura propuesta. No se implementó en producción, pero cada componente se apoya en los "
  "resultados medidos en el cuaderno.")
FIG("11_arquitectura_streaming.png", "Arquitectura de detección de anomalías en tiempo real con Apache Kafka y Apache Flink.", 16.5)
H2("6.1 Ingesta")
P("Los canales publican cada transacción en el tópico <i>tx.raw</i> de Apache Kafka (Kreps et al., 2011), particionado por "
  "<i>cliente_id</i> con 24 particiones y factor de replicación 3. Particionar por cliente garantiza el orden de sus transacciones, "
  "requisito de las variables de comportamiento y del LSTM. Los productores usan <i>acks=all</i> e idempotencia para no perder ni "
  "duplicar eventos, y un registro de esquemas Avro versiona el contrato de datos. El perfil del cliente (límites, domicilio) se "
  "replica desde el núcleo bancario mediante captura de cambios (CDC) y se difunde a todos los operadores como estado de "
  "<i>broadcast</i>.")
H2("6.2 Procesamiento, ventanas e inferencia")
P("Apache Flink (Carbone et al., 2015) consume el flujo con semántica <i>exactly-once</i> y puntos de control periódicos. Tras "
  "validar el esquema (los eventos inválidos van a una cola de mensajes muertos), el flujo se agrupa por cliente y mantiene en "
  "estado RocksDB las últimas ocho transacciones, la media histórica del monto y la marca de tiempo anterior. Se emplean dos "
  "tipos de ventana, en el sentido del modelo Dataflow (Akidau et al., 2015): una ventana deslizante de una hora con paso de un "
  "minuto para variables de velocidad (transacciones en la última hora, suma de montos) y una ventana <i>tumbling</i> diaria para "
  "el perfil de consumo. Las variables resultantes se agrupan en micro-lotes con un disparador doble —10.000 transacciones o "
  "200 ms, lo que ocurra primero— y se envían a los cuatro detectores, exportados a ONNX y ejecutados embebidos en el propio "
  "operador para evitar llamadas de red.")
H2("6.3 Umbrales adaptativos y alertas")
P("Un umbral fijo envejece: en quincena el volumen y los montos suben y un umbral estático dispararía falsas alarmas. Se propone "
  "un umbral adaptativo calculado como un percentil móvil del puntaje del ensamble en las últimas 24 horas, separado por "
  "segmento y canal, y corregido con la retroalimentación de los analistas (si una alerta resulta falsa, el percentil del "
  "estrato se ajusta). El motor de decisión combina el puntaje con reglas regulatorias duras derivadas del perfil transaccional: "
  "por encima del umbral alto la transacción se bloquea, en la zona gris se exige autenticación reforzada (OTP) y el resto se "
  "aprueba. Las decisiones se publican en <i>tx.scored</i> junto con las tres variables SHAP de mayor contribución, y las alertas "
  "priorizadas en <i>fraude.alertas</i>, que alimenta la gestión de casos, la notificación al cliente y el SIEM. Las etiquetas "
  "confirmadas regresan al <i>data lake</i> para reentrenamiento, y el monitoreo vigila la latencia p99 y la deriva de los datos "
  "mediante el índice de estabilidad poblacional (PSI).")
H2("6.4 Análisis de latencia y efecto del tamaño de lote")
P(f"La Figura 9 resume la relación latencia-<i>throughput</i>. En el panel izquierdo se midió el procesamiento (preprocesamiento "
  f"más inferencia) de Isolation Forest para lotes de 100 a 50.000 transacciones. La latencia crece de forma sublineal hasta unos "
  f"2.500 elementos, porque los costos fijos (llamadas, reserva de memoria) se amortizan, y el <i>throughput</i> sube de "
  f"{num(LAT.iloc[0].throughput_tx_s)} a {num(lat2500.throughput_tx_s)} transacciones por segundo. A partir de allí la latencia "
  f"crece de forma superlineal y el <i>throughput</i> cae a {num(lat50k.throughput_tx_s)} tx/s con 50.000 elementos, por presión "
  f"sobre la memoria caché. El lote de 10.000 exigido se procesa en {ms(lat10k.proc_ms)}, dentro del límite, pero cerca del "
  f"punto en que los rendimientos se vuelven decrecientes.")
FIG("08_latencia_batch.png", "Izquierda: latencia de procesamiento medida y throughput según el tamaño de lote. Derecha: latencia "
    "percibida estimada, sumando el tiempo medio de espera para llenar el lote y 15 ms de sobrecarga de Kafka y Flink (valor "
    "bibliográfico estimado).", 16.5)
P(f"El hallazgo más importante está en el panel derecho. El banco recibe en promedio 3,5 millones de transacciones diarias, "
  f"unas 40 por segundo, y en picos de quincena podría acercarse a 200 por segundo. A ese ritmo llenar un lote de 10.000 toma "
  f"entre 50 segundos y más de cuatro minutos, de modo que una transacción esperaría en promedio "
  f"{f2(lat10k.e2e_pico_ms / 1000, 0)}–{f2(lat10k.e2e_media_ms / 1000, 0)} segundos antes de ser evaluada. Para una decisión en "
  f"línea, en la que el autorizador debe responder al canal en menos de un segundo, el cuello de botella no es el modelo sino el "
  f"tamaño del lote. Por eso el requisito de 500 ms por lote de 10.000 debe interpretarse como capacidad de procesamiento en "
  f"picos o reprocesamientos, no como tamaño de lote operativo. El disparador doble resuelve el conflicto: en operación normal "
  f"los lotes se cierran por tiempo (200 ms, unas 40 transacciones), con latencia percibida inferior a 250 ms, y solo en ráfagas "
  f"extremas se cierran por conteo, aprovechando el mayor <i>throughput</i>. Con 24 particiones procesadas en paralelo, la "
  f"capacidad teórica supera holgadamente los picos previstos.")

# ------------------------------------------------------------------ 7. EXPLICABILIDAD
H1("7. Interpretación con SHAP e implicaciones éticas")
P("Para Isolation Forest se utilizó TreeSHAP, que calcula valores de Shapley exactos para ensambles de árboles en tiempo "
  "polinomial (Lundberg et al., 2020), dentro del marco unificado SHAP (Lundberg y Lee, 2017). Como SHAP explica la longitud de "
  "camino esperada, en la que un valor mayor indica normalidad, el signo se invirtió para que un valor positivo signifique un "
  "aporte hacia la anomalía. Se explicaron 200 transacciones de prueba: las 150 de mayor puntaje y 50 aleatorias.")
FIG("09_shap_summary.png", "Valores SHAP de las 15 variables más influyentes en el puntaje de anomalía de Isolation Forest.", 13.5)
top = list(R["shap_top"].keys())
caso = R["shap_caso"]
cc = list(caso["contribuciones"].items())
P(f"Las variables con mayor contribución media fueron transacción internacional, intentos fallidos de acceso en 24 horas, "
  f"dispositivo nuevo, segmento del cliente, compra en línea y beneficiario nuevo (Figura 10). Todas tienen un significado de "
  f"negocio directo y coinciden con las señales que un analista de prevención de fraude revisaría, lo que aporta validez "
  f"aparente al modelo. La explicación local de la Figura 11 corresponde a la transacción {caso['tx']['tx_id']}, una "
  f"transferencia de {f2(caso['tx']['monto_usd'], 2)} USD desde la app móvil, efectivamente una toma de cuenta: los mayores "
  f"aportes provienen de los intentos fallidos, el dispositivo nuevo y el beneficiario nuevo. Este tipo de explicación es la "
  f"que se adjuntaría a cada alerta.")
FIG("10_shap_local.png", f"Explicación local de la transacción {caso['tx']['tx_id']} (toma de cuenta detectada).", 12)
P("SHAP también revela problemas. El indicador de distancia faltante y el segmento del cliente aparecen entre las variables "
  "influyentes. Lo primero significa que el modelo considera sospechoso que no haya geolocalización, lo que penaliza a quienes "
  "usan banca web o desactivan el GPS; lo segundo implica que ciertos segmentos reciben puntajes más altos por el solo hecho de "
  "ser minoritarios en los datos. Ninguna de las dos es causa de fraude; son atajos estadísticos. Detectarlos es precisamente "
  "el valor de la explicabilidad, y la corrección (eliminar o restringir esas variables, o monitorear tasas de alerta por "
  "segmento) debe decidirse con el área de cumplimiento.")
P("Sobre el uso de modelos de caja negra en decisiones financieras, Rudin (2019) sostiene que en decisiones de alto impacto "
  "deberían preferirse modelos interpretables por diseño, porque las explicaciones post hoc son aproximaciones que pueden ser "
  "infieles al modelo. El argumento pesa aquí: bloquear una transferencia afecta el acceso del cliente a su dinero. Se proponen "
  "cuatro salvaguardas. Primera, el modelo no decide solo: bloquea únicamente en el extremo del puntaje y combinado con reglas "
  "regulatorias; en la zona gris pide autenticación adicional, que el cliente legítimo supera en segundos. Segunda, toda alerta "
  "conserva su explicación y es revisable por un analista humano. Tercera, se monitorea la equidad, comparando tasas de falsos "
  "positivos por provincia, segmento y edad, para evitar que poblaciones con menos historial digital, como clientes rurales o "
  "adultos mayores, sean bloqueadas de manera desproporcionada. Cuarta, se prefiere el modelo más simple que cumpla el objetivo: "
  "en este trabajo, Isolation Forest y el OC-SVM son sustancialmente más explicables que las redes neuronales, con desempeño "
  "comparable o superior. Ribeiro et al. (2016) ofrecen con LIME una alternativa local que puede usarse para contrastar la "
  "estabilidad de las explicaciones de SHAP.")

# ------------------------------------------------------------------ 8. CONCLUSIONES
H1("8. Conclusiones")
P(f"El trabajo demostró que es técnicamente viable detectar fraude electrónico en flujos de transacciones de un banco "
  f"ecuatoriano con modelos no supervisados que cumplen la restricción de latencia. Ningún detector domina en todas las "
  f"tipologías: los métodos tabulares capturan la toma de cuenta y el <i>SIM swap</i>, LOF es el más sensible al <i>card "
  f"testing</i> y solo el modelo secuencial percibe la clonación en cajeros. El ensamble de cuatro detectores (AUC-PR = "
  f"{f2(ENS['AUC_PR'])}) supera a cualquiera de ellos y, ejecutado en paralelo, procesa un lote de 10.000 transacciones en "
  f"{ms(ENS['Latencia_ms_10k_paralelo'])}. También quedó claro que el AUC-ROC y el F1 ponderado sobrestiman el desempeño en "
  f"datos tan desbalanceados, por lo que cualquier reporte al comité de riesgos debería basarse en AUC-PR, precisión y recall "
  f"de la clase fraude, y en la tasa de falsas alarmas.")
P("<b>Vinculación con los requerimientos de la Superintendencia de Bancos.</b> La normativa de control de la SB exige desde "
  "hace más de una década que las entidades definan un perfil transaccional por cliente y monitoreen en línea las operaciones "
  "de sus canales electrónicos, de modo que puedan detener oportunamente las que se aparten de dicho perfil; esta exigencia se "
  "incorporó a la norma de gestión de riesgo operativo con la reforma de 2014 y la SB ha seguido emitiendo disposiciones sobre "
  "controles en banca electrónica y monitoreo transaccional. El sistema propuesto operacionaliza ese mandato. El perfil "
  "transaccional deja de ser un conjunto de límites estáticos y se convierte en un modelo de la normalidad de cada cliente, "
  "representado por sus variables de comportamiento y su secuencia de transacciones. El monitoreo en línea se cumple con la "
  "arquitectura de Kafka y Flink, y la capacidad de bloquear o pedir autenticación reforzada responde a la obligación de "
  "proteger los recursos de los usuarios. En el marco de las directrices de 2022 sobre analítica avanzada mencionadas en el "
  "planteamiento del caso y de la Ley Orgánica de Prevención, Detección y Erradicación del Delito de Lavado de Activos, el "
  "tópico de alertas puede alimentar además el análisis de operaciones inusuales que la entidad reporta a la Unidad de "
  "Análisis Financiero y Económico (UAFE). Es igualmente relevante para la gestión de riesgo operativo que el diseño incluya "
  "registro de modelos, trazabilidad de cada decisión con su explicación y monitoreo de deriva: un modelo que se degrada en "
  "silencio es un riesgo operativo en sí mismo.")
P("<b>Vinculación con la LOPDP.</b> El tratamiento de datos transaccionales para prevenir fraude puede ampararse en el "
  "cumplimiento de obligaciones legales y en el interés legítimo de la entidad, pero la LOPDP (2021) impone condiciones que "
  "el diseño debe reflejar. El principio de minimización justificó no utilizar nombres, cédulas ni datos de contacto: el modelo "
  "trabaja con identificadores seudonimizados y variables de comportamiento. El artículo 20 reconoce el derecho a no ser objeto "
  "de decisiones basadas única o parcialmente en valoraciones automatizadas que produzcan efectos jurídicos o afecten derechos "
  "fundamentales; bloquear una transferencia encaja en ese supuesto. Por ello el sistema conserva la revisión humana, almacena "
  "la explicación SHAP de cada decisión para poder informar al titular los criterios aplicados y limita el bloqueo automático "
  "al extremo del puntaje. Como se trata de un tratamiento a gran escala con elaboración de perfiles, corresponde realizar una "
  "evaluación de impacto de protección de datos antes de su despliegue. Dos novedades de 2026 refuerzan estas obligaciones: la "
  "Superintendencia de Protección de Datos Personales expidió una norma específica para el tratamiento de datos en sistemas de "
  "inteligencia artificial, que la faculta para auditarlos, y la Ley Orgánica para el Fortalecimiento de la Ciberseguridad "
  "reformó el régimen de notificación de vulneraciones de seguridad del artículo 43. El <i>data lake</i> de entrenamiento, que "
  "concentra historiales transaccionales, debe por tanto contar con cifrado, control de acceso y plazos de conservación "
  "definidos.")
P("<b>Escalabilidad en la infraestructura del sector financiero ecuatoriano.</b> Con 3,5 millones de transacciones diarias, "
  "el volumen del caso es moderado para Kafka y Flink, plataformas que en otras industrias procesan millones de eventos por "
  "segundo. Las mediciones muestran que un solo núcleo procesa más de 25.000 transacciones por segundo con Isolation Forest, "
  "y la partición por cliente permite escalar horizontalmente agregando particiones y paralelismo sin rediseñar el sistema. Las "
  "limitaciones reales en el contexto ecuatoriano son de otra naturaleza: la integración con núcleos bancarios heredados que no "
  "emiten eventos (lo que exige CDC), la disponibilidad de personal especializado en operación de <i>streaming</i>, la decisión "
  "entre infraestructura propia y nube pública a la luz de los requisitos de localización y transferencia internacional de "
  "datos, y el costo para entidades medianas o cooperativas. Para estas últimas, una versión reducida con Isolation Forest u "
  "OC-SVM, ambos ligeros y sin GPU, ofrece la mayor parte del beneficio con una fracción del costo. Un servicio compartido entre "
  "entidades, al estilo de los consorcios antifraude, permitiría además detectar patrones que cruzan instituciones, siempre "
  "que se resuelvan los acuerdos de transferencia de datos que exige la LOPDP.")
P("Entre las limitaciones del estudio destacan el uso de datos sintéticos, cuyas tipologías son más regulares que las reales "
  "y cuya tasa de fraude es más alta que la de un banco típico; la medición de latencias en un único núcleo; y que el diseño "
  "de <i>streaming</i> no se desplegó. Como trabajo futuro se propone validar el pipeline con datos reales anonimizados bajo un "
  "acuerdo con una entidad, sustituir la variable de dispositivo por un <i>fingerprint</i> continuo, probar modelos de grafos "
  "para detectar redes de cuentas mula y evaluar el modelo supervisado con etiquetas que llegan con retraso.")

# ------------------------------------------------------------------ REFERENCIAS
story.append(PageBreak())
H1("Referencias")
REFS = [
    "Akidau, T., Bradshaw, R., Chambers, C., Chernyak, S., Fernández-Moctezuma, R. J., Lax, R., McVeety, S., Mills, D., Perry, F., Schmidt, E., & Whittle, S. (2015). The dataflow model: A practical approach to balancing correctness, latency, and cost in massive-scale, unbounded, out-of-order data processing. <i>Proceedings of the VLDB Endowment, 8</i>(12), 1792–1803. https://doi.org/10.14778/2824032.2824076",
    "Asamblea Nacional del Ecuador. (2016). <i>Ley Orgánica de Prevención, Detección y Erradicación del Delito de Lavado de Activos y del Financiamiento de Delitos</i>. Registro Oficial Suplemento 802, 21 de julio de 2016.",
    "Asamblea Nacional del Ecuador. (2021). <i>Ley Orgánica de Protección de Datos Personales</i>. Registro Oficial Quinto Suplemento 459, 26 de mayo de 2021.",
    "Asamblea Nacional del Ecuador. (2026). <i>Ley Orgánica para el Fortalecimiento de la Ciberseguridad</i>. Registro Oficial Quinto Suplemento 290, 22 de mayo de 2026.",
    "Breunig, M. M., Kriegel, H.-P., Ng, R. T., & Sander, J. (2000). LOF: Identifying density-based local outliers. <i>Proceedings of the 2000 ACM SIGMOD International Conference on Management of Data</i>, 93–104. https://doi.org/10.1145/342009.335388",
    "Carbone, P., Katsifodimos, A., Ewen, S., Markl, V., Haridi, S., & Tzoumas, K. (2015). Apache Flink: Stream and batch processing in a single engine. <i>Bulletin of the IEEE Computer Society Technical Committee on Data Engineering, 38</i>(4), 28–38.",
    "Chandola, V., Banerjee, A., & Kumar, V. (2009). Anomaly detection: A survey. <i>ACM Computing Surveys, 41</i>(3), Artículo 15. https://doi.org/10.1145/1541880.1541882",
    "Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. <i>Journal of Artificial Intelligence Research, 16</i>, 321–357. https://doi.org/10.1613/jair.953",
    "Dal Pozzolo, A., Boracchi, G., Caelen, O., Alippi, C., & Bontempi, G. (2018). Credit card fraud detection: A realistic modeling and a novel learning strategy. <i>IEEE Transactions on Neural Networks and Learning Systems, 29</i>(8), 3784–3797. https://doi.org/10.1109/TNNLS.2017.2736643",
    "Hinton, G. E., & Salakhutdinov, R. R. (2006). Reducing the dimensionality of data with neural networks. <i>Science, 313</i>(5786), 504–507. https://doi.org/10.1126/science.1127647",
    "Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. <i>Neural Computation, 9</i>(8), 1735–1780. https://doi.org/10.1162/neco.1997.9.8.1735",
    "Kreps, J., Narkhede, N., & Rao, J. (2011). Kafka: A distributed messaging system for log processing. En <i>Proceedings of the 6th International Workshop on Networking Meets Databases (NetDB)</i>.",
    "Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation forest. En <i>2008 Eighth IEEE International Conference on Data Mining</i> (pp. 413–422). IEEE. https://doi.org/10.1109/ICDM.2008.17",
    "Lundberg, S. M., Erion, G., Chen, H., DeGrave, A., Prutkin, J. M., Nair, B., Katz, R., Himmelfarb, J., Bansal, N., & Lee, S.-I. (2020). From local explanations to global understanding with explainable AI for trees. <i>Nature Machine Intelligence, 2</i>(1), 56–67. https://doi.org/10.1038/s42256-019-0138-9",
    "Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. <i>Advances in Neural Information Processing Systems, 30</i>, 4765–4774.",
    "Pang, G., Shen, C., Cao, L., & van den Hengel, A. (2021). Deep learning for anomaly detection: A review. <i>ACM Computing Surveys, 54</i>(2), Artículo 38. https://doi.org/10.1145/3439950",
    "Patki, N., Wedge, R., & Veeramachaneni, K. (2016). The synthetic data vault. En <i>2016 IEEE International Conference on Data Science and Advanced Analytics (DSAA)</i> (pp. 399–410). IEEE. https://doi.org/10.1109/DSAA.2016.49",
    "Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). “Why should I trust you?”: Explaining the predictions of any classifier. En <i>Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining</i> (pp. 1135–1144). https://doi.org/10.1145/2939672.2939778",
    "Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. <i>Nature Machine Intelligence, 1</i>(5), 206–215. https://doi.org/10.1038/s42256-019-0048-x",
    "Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. <i>PLOS ONE, 10</i>(3), Artículo e0118432. https://doi.org/10.1371/journal.pone.0118432",
    "Schölkopf, B., Platt, J. C., Shawe-Taylor, J., Smola, A. J., & Williamson, R. C. (2001). Estimating the support of a high-dimensional distribution. <i>Neural Computation, 13</i>(7), 1443–1471. https://doi.org/10.1162/089976601750264965",
    "Superintendencia de Protección de Datos Personales. (2026). <i>Resolución N.° SPDP-SPD-2026-0009-R: Norma general para la protección de datos personales en el uso de inteligencia artificial</i>.",
    "Williams, C. K. I., & Seeger, M. (2001). Using the Nyström method to speed up kernel machines. <i>Advances in Neural Information Processing Systems, 13</i>, 682–688.",
]
for r in REFS:
    story.append(Paragraph(r, sty["ref"]))


# ------------------------------------------------------------------ BUILD
def deco(c, d):
    c.saveState()
    if d.page > 1:
        c.setFont("Sans", 7.5); c.setFillColor(colors.HexColor("#666"))
        c.drawString(2.2 * cm, 1.3 * cm, "De La Torre Durán, L. A. · Detección de anomalías en transacciones financieras · UNIANDES 2026")
        c.drawRightString(A4[0] - 2.2 * cm, 1.3 * cm, str(d.page))
    c.restoreState()


out = f"{REPO}/informe/Informe_tecnico_deteccion_anomalias_DeLaTorre.pdf"
doc = BaseDocTemplate(out, pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2.2 * cm, bottomMargin=2.2 * cm,
                      title="Detección de anomalías en flujos financieros – contexto ecuatoriano",
                      author="Luis Alberto De La Torre Durán")
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=deco)])
doc.build(story)
body = " ".join(WORDS)
concl = body[body.index("8. Conclusiones"):]
print("palabras cuerpo:", len(body.split()), "| conclusiones:", len(concl.split()), "| refs:", len(REFS))

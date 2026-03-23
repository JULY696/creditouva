from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import random
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = FastAPI()

# CORS (IMPORTANTE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELOS ----------------

class CreditoInput(BaseModel):
    tipo: str
    monto: float
    tna: float
    plazo_meses: int
    cftea: float
    seguro_pct: float = 0.002
    gastos_pct: float = 0.001
    usar_cvs: bool = False

class InversionInput(BaseModel):
    tipo: str
    capital_inicial: float
    aporte_mensual: float
    tasa_anual: float

class MacroInput(BaseModel):
    inflacion_mensual: float
    devaluacion_mensual: float

class SimulacionInput(BaseModel):
    credito: CreditoInput
    inversion: InversionInput
    macro: MacroInput
    montecarlo: bool = False

# ---------------- UTILIDADES ----------------

def sistema_frances(monto, tasa, meses):
    if meses <= 0:
        raise ValueError("El plazo debe ser mayor a 0")

    tasa_m = tasa / 12

    if tasa_m == 0:
        return monto / meses

    return monto * (tasa_m * (1+tasa_m)**meses) / ((1+tasa_m)**meses -1)

# ---------------- CRÉDITO UVA ----------------

def simular_uva(monto, tasa, meses, inflacion, usar_cvs):
    cuota_base = sistema_frances(monto, tasa, meses)
    saldo = monto
    inflacion_acum = 1
    cvs_acum = 1

    data = []

    for m in range(1, meses+1):
        inflacion_acum *= (1 + inflacion)
        cvs_acum *= (1 + inflacion * 0.8)

        cuota_uva = cuota_base * inflacion_acum

        if usar_cvs:
            cuota_cvs = cuota_base * cvs_acum
            cuota = min(cuota_uva, cuota_cvs)
        else:
            cuota = cuota_uva

        saldo -= (cuota_base - saldo * (tasa/12))

        data.append({"mes": m, "cuota": cuota, "saldo": max(saldo,0)})

    return data

# ---------------- CRÉDITO VARIABLE ----------------

def simular_variable(monto, tasa_base, meses):
    saldo = monto
    data = []

    for m in range(1, meses+1):
        tasa = tasa_base + random.uniform(-0.05, 0.05)
        cuota = sistema_frances(saldo, tasa, meses-m+1)
        saldo -= cuota * 0.3

        data.append({"mes": m, "cuota": cuota, "saldo": max(saldo,0)})

    return data

# ---------------- INVERSION ----------------

def simular_inversion(tipo, capital, aporte, tasa, meses, inflacion, devaluacion):
    saldo = capital
    data = []

    for m in range(1, meses+1):

        if tipo == "cer":
            r = tasa/12 + inflacion
        elif tipo == "mep":
            r = devaluacion
        else:
            r = tasa/12

        saldo = saldo * (1 + r) + aporte

        data.append({"mes": m, "capital": saldo})

    return data

# ---------------- MONTE CARLO ----------------

def simular_montecarlo(input_data, n=50):
    resultados = []

    for _ in range(n):
        inflacion = random.uniform(0.02, 0.08)

        credito = simular_uva(
            input_data.credito.monto,
            input_data.credito.tna,
            input_data.credito.plazo_meses,
            inflacion,
            input_data.credito.usar_cvs
        )

        resultados.append(credito[-1]["cuota"])

    return resultados

# ---------------- PDF ----------------

def generar_pdf(resultado):
    doc = SimpleDocTemplate("reporte.pdf")
    styles = getSampleStyleSheet()

    content = [Paragraph("Simulación Financiera", styles['Title'])]

    for r in resultado[:12]:
        content.append(
            Paragraph(f"Mes {r['mes']}: Dif {round(r['diferencia'],2)}", styles['Normal'])
        )

    doc.build(content)

# ---------------- HOME ----------------

@app.get("/")
def home():
    return {"mensaje": "Backend funcionando OK 🚀"}

# ---------------- SIMULADOR ----------------

@app.post("/simular")
def simular(data: SimulacionInput):

    meses = data.credito.plazo_meses

    # crédito
    if data.credito.tipo == "uva":
        credito = simular_uva(
            data.credito.monto,
            data.credito.tna,
            meses,
            data.macro.inflacion_mensual,
            data.credito.usar_cvs
        )
    else:
        credito = simular_variable(
            data.credito.monto,
            data.credito.tna,
            meses
        )

    # inversión
    inversion = simular_inversion(
        data.inversion.tipo,
        data.inversion.capital_inicial,
        data.inversion.aporte_mensual,
        data.inversion.tasa_anual,
        meses,
        data.macro.inflacion_mensual,
        data.macro.devaluacion_mensual
    )

    # comparación
    resultado = []
    acumulado = 0

    for i in range(meses):
        cuota = credito[i]["cuota"]
        inv = inversion[i]["capital"]

        dif = inv - cuota
        acumulado += dif

        resultado.append({
            "mes": i+1,
            "cuota": cuota,
            "inversion": inv,
            "diferencia": dif,
            "acumulado": acumulado
        })

    generar_pdf(resultado)

    return {
        "credito": credito,
        "inversion": inversion,
        "resultado": resultado
    }
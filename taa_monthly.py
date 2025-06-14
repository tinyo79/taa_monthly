# 1. LIBRERÍAS
import yfinance as yf
import pandas as pd
import numpy as np
import smtplib
from email.message import EmailMessage
import ssl

# 2. PARÁMETROS DE LA ESTRATEGIA
activos = ['SPY', 'QQQ', 'IWM', 'IEV', 'EWJ', 'EEM', 'DBC', 'VNQ',
           'XLK', 'XLY', 'XLF', 'XLV', 'XLI', 'XLE', 'XLB', 'XLU',
           'XLC', 'XLP', 'XLRE', 'GLD', 'TLT']
inicio = "2000-01-01"
capital_inicial = 10000

n_activos = 2
roc_n_val = 3
roc_m_val = 6
vol_p_val = 10
formula_name = "ligero"

# 3. DESCARGA DE DATOS MENSUALES
data = yf.download(activos, start=inicio, interval="1mo", auto_adjust=True)["Close"]
data.dropna(how="all", inplace=True)

# 4. CÁLCULO DE INDICADORES
roc_n = data.pct_change(roc_n_val)
roc_m = data.pct_change(roc_m_val)
vol = data.pct_change().rolling(vol_p_val).std()

# Fórmula 'ligero'
ranking = (0.4 * roc_n + 0.2 * roc_m) / vol
ranking.replace([np.inf, -np.inf], np.nan, inplace=True)

# 5. EJECUCIÓN DE LA ESTRATEGIA
capital = capital_inicial
capital_mensual = []
resultados = []
fechas_validas = ranking.index[max(roc_n_val, roc_m_val, vol_p_val):]

for fecha in fechas_validas:
    r = ranking.loc[fecha]
    df = pd.DataFrame({
        "ranking": r,
        "roc_n": roc_n.loc[fecha],
        "roc_m": roc_m.loc[fecha],
        "vol": vol.loc[fecha]
    }).dropna()

    if len(df) < n_activos:
        continue

    seleccionados = df.sort_values("ranking", ascending=False).head(n_activos).index
    ret_mensual = data.pct_change().loc[fecha, seleccionados].mean()
    if pd.isna(ret_mensual):
        continue

    capital *= (1 + ret_mensual)
    capital_mensual.append((fecha, capital))

    # Guardar resultados detallados
    for activo in seleccionados:
        resultados.append({
            "Fecha": fecha,
            "Activo": activo,
            "Ranking": r[activo],
            "ROC_n": roc_n.loc[fecha, activo],
            "ROC_m": roc_m.loc[fecha, activo],
            "Volatilidad": vol.loc[fecha, activo],
            "Capital": capital
        })

# 6. RESULTADOS
df_resultados = pd.DataFrame(resultados)
df_resultados.to_csv("resultados_mensuales_con_ranking.csv", index=False)
csv_filename = "resultados_mensuales_con_ranking.csv"


# ENVIAR CORREO
remitente = "robertcanovasvela@gmail.com"
destinatario = "robertcanovasvela@gmail.com"
password = "unyf inbl aczo oqfq"

mensaje = EmailMessage()
mensaje["Subject"] = "TAA_Monthly"
mensaje["From"] = remitente
mensaje["To"] = destinatario
mensaje.set_content(f"""Hola,

Te adjunto el archivo con los etfs seleccionados para este mes.

Saludos,
Tu sistema automático
""")

# Adjuntar archivo
with open(csv_filename, "rb") as f:
    mensaje.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=csv_filename)

# Enviar email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as servidor:
    servidor.login(remitente, password)
    servidor.send_message(mensaje)

print(f"Correo enviado a {destinatario} con {csv_filename} adjunto.")

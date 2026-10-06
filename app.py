import streamlit as st
import datetime
import random
import json
import os

DB_FILE = "ahorro_data.json"

def calcular_dias_restantes():
    hoy = datetime.date.today()
    fin_de_ano = datetime.date(hoy.year, 12, 31)
    return (fin_de_ano - hoy).days + 1

def cargar_datos():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        dias = calcular_dias_restantes()
        # Generar lista de montos: 0.30, 0.60, 0.90, ...
        montos_disponibles = [round((i + 1) * 0.30, 2) for i in range(dias)]
        return {
            "fecha_creacion": str(datetime.date.today()),
            "total_dias": dias,
            "montos_disponibles": montos_disponibles,
            "historial": [] # [{fecha, monto}]
        }

def guardar_datos(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

st.set_page_config(page_title="Mi Reto de Ahorro", page_icon="🐷")

st.title("🐷 Mi Reto de Ahorro Diarios")

data = cargar_datos()
hoy_str = str(datetime.date.today())

# Verificar si ya ahorró hoy
ahorro_hoy = next((item for item in data["historial"] if item["fecha"] == hoy_str), None)

total_ahorrado = sum(item["monto"] for item in data["historial"])
st.metric("Total Ahorrado", f"${total_ahorrado:.2f}")

if ahorro_hoy:
    st.success(f"¡Hoy ya sacaste tu cuota! Te tocó ahorrar: **${ahorro_hoy['monto']:.2f}**")
else:
    if st.button("🎲 Sacar cuota de hoy", type="primary"):
        if not data["montos_disponibles"]:
            st.balloons()
            st.success("¡Felicidades! Completaste todos los días de ahorro del año.")
        else:
            disponibles = data["montos_disponibles"]
            monto_maximo = max(disponibles)
            umbral_alto = monto_maximo * 0.7  # Definimos el top 30% como 'alto'
            
            ultimo_monto = data["historial"][-1]["monto"] if data["historial"] else 0
            
            # Filtro para no repetir montos altos consecutivos
            if ultimo_monto >= umbral_alto and len(disponibles) > 1:
                opciones = [m for m in disponibles if m < umbral_alto]
                if not opciones:  # Si solo quedan altos, tomar cualquiera
                    opciones = disponibles
            else:
                opciones = disponibles
                
            monto_elegido = random.choice(opciones)
            
            # Actualizar datos
            data["montos_disponibles"].remove(monto_elegido)
            data["historial"].append({"fecha": hoy_str, "monto": monto_elegido})
            guardar_datos(data)
            
            st.rerun()

st.divider()
st.subheader("📊 Historial de Ahorros")
if data["historial"]:
    for item in reversed(data["historial"]):
        st.write(f"📅 **{item['fecha']}**: ${item['monto']:.2f}")
else:
    st.info("Aún no has comenzado. ¡Presiona el botón arriba para tu primer día!")
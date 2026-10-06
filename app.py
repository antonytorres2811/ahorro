import streamlit as st
import datetime
import random
import json
import extra_streamlit_components as stx

def calcular_dias_restantes():
    hoy = datetime.date.today()
    fin_de_ano = datetime.date(hoy.year, 12, 31)
    return (fin_de_ano - hoy).days + 1

FRASES = [
    "¡Excelente trabajo! Cada moneda cuenta para tus metas. 🚀",
    "¡Un paso más cerca de tu objetivo financiero! 💪",
    "¡El hábito del ahorro es el secreto de la libertad financiera! 🔥",
    "¡Sigue así, tu 'yo' del futuro te lo agradecerá! 🐷✨",
    "¡Tu disciplina de hoy es tu tranquilidad de mañana! 🎉"
]

st.set_page_config(page_title="Mi Reto de Ahorro", page_icon="🐷")
st.title("🐷 Mi Reto de Ahorro Diarios")

# Manejo de Cookie/Storage local en el navegador del celular
cookie_manager = stx.get_cookie_manager()

# Cargar o inicializar datos guardados en el dispositivo
saved_data = cookie_manager.get(cookie="ahorro_reto_data")

dias_restantes = calcular_dias_restantes()

if saved_data:
    try:
        data = json.loads(saved_data)
    except:
        data = {"montos_disponibles": [round((i + 1) * 0.30, 2) for i in range(dias_restantes)], "historial": []}
else:
    data = {"montos_disponibles": [round((i + 1) * 0.30, 2) for i in range(dias_restantes)], "historial": []}

if "monto_pendiente" not in st.session_state:
    st.session_state.monto_pendiente = None

hoy_str = str(datetime.date.today())
ahorro_hoy = next((item for item in data["historial"] if item["fecha"] == hoy_str), None)

total_ahorrado = sum(item["monto"] for item in data["historial"])
dias_completados = len(data["historial"])
porcentaje_progreso = min(1.0, dias_completados / dias_restantes) if dias_restantes > 0 else 1.0

col1, col2 = st.columns(2)
col1.metric("💰 Total Ahorrado", f"S/ {total_ahorrado:.2f}")
col2.metric("📅 Días Guardados", f"{dias_completados} / {dias_restantes}")

st.progress(porcentaje_progreso, text=f"Progreso del reto: {porcentaje_progreso * 100:.1f}%")
st.divider()

if ahorro_hoy:
    st.success(f"🎉 **¡Cuota de hoy completada!** Ahorraste: **S/ {ahorro_hoy['monto']:.2f}**")
    st.info(f"💡 *{ahorro_hoy.get('frase', '¡Buen trabajo!')}*")

elif st.session_state.monto_pendiente:
    monto = st.session_state.monto_pendiente
    st.subheader(f"🎯 Tu monto asignado para hoy es: **S/ {monto:.2f}**")
    st.warning("⚠️ **Paso final para validar tu día:** ¿Ya transferiste o guardaste este dinero en tu cuenta?")

    col_si, col_no = st.columns(2)
    
    if col_si.button("✅ ¡Sí, ya lo deposité!", type="primary", use_container_width=True):
        st.balloons()
        frase_elegida = random.choice(FRASES)
        data["montos_disponibles"].remove(monto)
        data["historial"].append({
            "fecha": hoy_str, 
            "monto": monto,
            "frase": frase_elegida
        })
        
        # Guardar permanentemente en la memoria del celular (expira en 365 días)
        cookie_manager.set("ahorro_reto_data", json.dumps(data), key="save_data", expires_at=datetime.datetime.now() + datetime.timedelta(days=365))
        st.session_state.monto_pendiente = None
        st.rerun()

    if col_no.button("⏳ Aún no, lo haré luego", use_container_width=True):
        st.session_state.monto_pendiente = None
        st.rerun()

else:
    if st.button("🎲 Sacar cuota de hoy", type="primary", use_container_width=True):
        disponibles = data["montos_disponibles"]
        if not disponibles:
            st.snow()
            st.success("¡Felicidades! Completaste todos los días del reto.")
        else:
            monto_maximo = max(disponibles)
            umbral_alto = monto_maximo * 0.7
            ultimo_monto = data["historial"][-1]["monto"] if data["historial"] else 0

            if ultimo_monto >= umbral_alto and len(disponibles) > 1:
                opciones = [m for m in disponibles if m < umbral_alto]
                if not opciones:
                    opciones = disponibles
            else:
                opciones = disponibles

            monto_elegido = random.choice(opciones)
            st.session_state.monto_pendiente = monto_elegido
            st.rerun()

st.divider()
st.subheader("📊 Historial de Ahorros")
if data["historial"]:
    for item in reversed(data["historial"]):
        st.write(f"📅 **{item['fecha']}**: S/ {item['monto']:.2f}")
else:
    st.info("Aún no has comenzado. ¡Haz clic en el botón para sacar tu primer monto!")

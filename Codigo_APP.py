import streamlit as st
import requests
import pandas as pd
import dns.resolver  # Esto es lo que verifica el email real
import re

# --- CONFIGURACIÓN DE GUMROAD ---
PRODUCT_ID = "EiQAVZ13bGetAXwtLbDaiw=="


def validar_con_gumroad(license_key):
    url = "https://api.gumroad.com/v2/licenses/verify"
    datos = {"product_id": PRODUCT_ID, "license_key": license_key, "increment_uses_count": "true"}
    try:
        respuesta = requests.post(url, data=datos)
        resultado = respuesta.json()
        if resultado.get("success") and not resultado["purchase"].get("refunded"):
            return True, "¡Acceso concedido!"
        return False, "Clave inválida o reembolsada."
    except:
        return False, "Error de conexión con Gumroad."


# --- MOTOR DE VERIFICACIÓN DE EMAILS ---
def verificar_mx(email):
    """Verifica si el dominio del email tiene registros MX (puede recibir correos)"""
    try:
        dominio = email.split('@')[-1]
        registros = dns.resolver.resolve(dominio, 'MX')
        return "Válido" if registros else "Inválido"
    except:
        return "Inválido"


# --- INTERFAZ ---
st.title("⚡ Validador Premium 2025")

if 'auth' not in st.session_state:
    st.session_state.auth = False

with st.sidebar:
    st.header("🔑 Activación")
    user_key = st.text_input("License Key de Gumroad:", type="password")
    if st.button("Verificar"):
        es_valida, mensaje = validar_con_gumroad(user_key)
        if es_valida:
            st.session_state.auth = True
            st.success(mensaje)
        else:
            st.error(mensaje)

# --- LÓGICA DE NEGOCIO ---
archivo = st.file_uploader("Sube tu lista de correos (CSV)", type="csv")

if archivo:
    df = pd.read_csv(archivo)

    # Buscamos la columna que contenga los emails automáticamente
    col_email = [c for c in df.columns if 'email' in c.lower()]

    if not col_email:
        st.error("No se encontró una columna llamada 'email'.")
    else:
        if st.button("🚀 Iniciar Validación Real"):
            # Aquí ocurre la magia
            with st.spinner('Verificando dominios y registros MX...'):
                df['Estado_Email'] = df[col_email[0]].apply(verificar_mx)

            # Filtramos solo los válidos para el cliente
            df_limpio = df[df['Estado_Email'] == "Válido"]

            st.write(f"Proceso terminado. Emails válidos encontrados: {len(df_limpio)}")
            st.dataframe(df.head(10))  # Vista previa

            if st.session_state.auth:
                csv_download = df_limpio.to_csv(index=False).encode('utf-8')
                st.download_button("📥 DESCARGAR LISTA LIMPIA", csv_download, "emails_validados.csv")
            else:
                st.warning("⚠️ Acceso limitado: Valida tu licencia para descargar la lista limpia.")
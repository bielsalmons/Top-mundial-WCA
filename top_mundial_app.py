import pandas as pd
import requests
import streamlit as st

st.title("Top mundial WCA por Evento")

# Diccionario para traducir IDs a nombres oficiales
NOMBRES_EVENTOS = {
    "222": "2x2x2 Cube",
    "333": "3x3x3 Cube",
    "444": "4x4x4 Cube",
    "555": "5x5x5 Cube",
    "666": "6x6x6 Cube",
    "777": "7x7x7 Cube",
    "333bf": "3x3x3 Blindfolded",
    "333fm": "3x3x3 Fewest Moves",
    "333oh": "3x3x3 One-Handed",
    "clock": "Clock",
    "minx": "Megaminx",
    "pyram": "Pyraminx",
    "skewb": "Skewb",
    "sq1": "Square-1",
    "444bf": "4x4x4 Blindfolded",
    "555bf": "5x5x5 Blindfolded",
    "333mbf": "3x3x3 Multi-Blind",
}

# Campo único de entrada
busqueda_input = st.text_input("Escribe un WCA ID o un nombre:").strip()

wca_id = None

if busqueda_input:
    # 1. Si coincide con el formato estándar de un WCA ID (Ej: 2018GARC01)
    if (
        len(busqueda_input) == 10
        and busqueda_input[:4].isdigit()
        and busqueda_input[4:8].isalpha()
        and busqueda_input[8:].isdigit()
    ):
        wca_id = busqueda_input.upper()
    else:
        # 2. Si es un nombre, consultar la API de búsqueda WCA
        url_search = f"https://www.worldcubeassociation.org/api/v0/search/users?q={busqueda_input}"
        resp_search = requests.get(url_search)

        if resp_search.status_code == 200:
            resultados = resp_search.json().get("result", [])
            personas = [
                u for u in resultados if u.get("wca_id") is not None
            ]

            if personas:
                opciones_personas = {
                    f"{p['name']} ({p['wca_id']})": p["wca_id"] for p in personas
                }
                persona_elegida = st.selectbox(
                    "Selecciona el competidor:",
                    options=list(opciones_personas.keys()),
                )
                wca_id = opciones_personas[persona_elegida]
            else:
                st.warning(
                    "No se encontraron competidores con WCA ID para esa búsqueda."
                )

# --- PROCESAMIENTO Y TARJETAS ---
if wca_id:
    URL_PERSON = f"https://raw.githubusercontent.com/robiningelbrecht/wca-rest-api/refs/heads/v1/persons/{wca_id}.json"
    respuesta_raw = requests.get(URL_PERSON)

    if respuesta_raw.status_code == 200:
        respuesta = respuesta_raw.json()

        # Extraer dataframes de la persona
        df_averages = pd.json_normalize(
            respuesta, record_path=["rank", "averages"], meta="name"
        )
        df_singles = pd.json_normalize(
            respuesta, record_path=["rank", "singles"], meta="name"
        )

        # Nombre del competidor
        nombre_completo = (
            df_averages["name"].values[0]
            if not df_averages.empty
            else df_singles["name"].values[0]
        )

        # Obtener lista única de eventos
        eventos_avg = (
            df_averages["eventId"].tolist() if not df_averages.empty else []
        )
        eventos_single = (
            df_singles["eventId"].tolist() if not df_singles.empty else []
        )
        eventos_disponibles = sorted(list(set(eventos_avg + eventos_single)))

        # Desplegable dinámico de eventos
        evento_elegido = st.selectbox(
            "Selecciona un evento:",
            options=eventos_disponibles,
            format_func=lambda x: NOMBRES_EVENTOS.get(x, x),
        )

        if evento_elegido:
            nombre_evento = NOMBRES_EVENTOS.get(evento_elegido, evento_elegido)

            # Subcabecera con Competidor y Evento
            st.subheader(f"Competidor: {nombre_completo} ({wca_id})")
            st.markdown(
                f"<p style='font-size: 15px; color: #D4AF37; margin-top: -12px; margin-bottom: 20px; font-weight: 600;'>Evento: <span style='color: #FFFFFF;'>{nombre_evento}</span></p>",
                unsafe_allow_html=True,
            )

            # --- TARJETA AVERAGE ---
            fila_avg = df_averages[df_averages["eventId"] == evento_elegido]

            if not fila_avg.empty:
                url_total_avg = f"https://raw.githubusercontent.com/robiningelbrecht/wca-rest-api/refs/heads/v1/rank/world/average/{evento_elegido}.json"
                total_avg = requests.get(url_total_avg).json()["total"]

                rank_avg = fila_avg["rank.world"].values[0]
                tiempo_avg = (
                    f"{fila_avg['best'].values[0] / 100:.2f}s".replace(".", ",")
                )
                top_avg_fmt = f"{(rank_avg / total_avg):.3%}".replace(".", ",")

                rank_avg_str = f"{rank_avg:,}".replace(",", ".")
                total_avg_str = f"{total_avg:,}".replace(",", ".")

                html_card_avg = f"""
                <div style="
                    background: radial-gradient(circle at top left, #1A1A1A 0%, #0D0D0D 100%);
                    border: 1px solid #D4AF37;
                    border-left: 5px solid #FFD700;
                    border-radius: 12px;
                    padding: 16px 22px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.6);
                    color: white;
                    margin-bottom: 16px;
                ">
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <span style="font-size: 13px; font-weight: 800; color: #D4AF37; letter-spacing: 1.5px; text-transform: uppercase;">Average</span>
                        <div style="font-size: 14px; color: #E0E0E0;">
                            Tiempo: <b style="color: #FFFFFF;">{tiempo_avg}</b> 
                            <span style="color: #D4AF37; margin: 0 6px;">|</span> 
                            Rank: <b style="color: #FFFFFF;">#{rank_avg_str}</b>
                        </div>
                        <div style="font-size: 12px; color: #A0A0A0;">
                            Total competidores: <span style="color: #FFFFFF;">{total_avg_str}</span>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 10px; color: #D4AF37; letter-spacing: 1.2px; text-transform: uppercase; font-weight: 600;">Top Mundial</div>
                        <div style="font-size: 34px; font-weight: 900; background: linear-gradient(180deg, #FFE57F 0%, #D4AF37 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{top_avg_fmt}</div>
                    </div>
                </div>
                """

                st.markdown(html_card_avg, unsafe_allow_html=True)
            else:
                st.info(
                    f"El competidor no tiene registro de **Average** en **{nombre_evento}**."
                )

            # --- TARJETA SINGLE ---
            fila_single = df_singles[df_singles["eventId"] == evento_elegido]

            if not fila_single.empty:
                url_total_single = f"https://raw.githubusercontent.com/robiningelbrecht/wca-rest-api/refs/heads/v1/rank/world/single/{evento_elegido}.json"
                total_single = requests.get(url_total_single).json()["total"]

                rank_single = fila_single["rank.world"].values[0]
                tiempo_single = (
                    f"{fila_single['best'].values[0] / 100:.2f}s".replace(
                        ".", ","
                    )
                )
                top_single_fmt = f"{(rank_single / total_single):.3%}".replace(
                    ".", ","
                )

                rank_single_str = f"{rank_single:,}".replace(",", ".")
                total_single_str = f"{total_single:,}".replace(",", ".")

                html_card_single = f"""
                <div style="
                    background: radial-gradient(circle at top left, #1A1A1A 0%, #0D0D0D 100%);
                    border: 1px solid #D4AF37;
                    border-left: 5px solid #FFD700;
                    border-radius: 12px;
                    padding: 16px 22px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.6);
                    color: white;
                ">
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <span style="font-size: 13px; font-weight: 800; color: #D4AF37; letter-spacing: 1.5px; text-transform: uppercase;">Single</span>
                        <div style="font-size: 14px; color: #E0E0E0;">
                            Tiempo: <b style="color: #FFFFFF;">{tiempo_single}</b> 
                            <span style="color: #D4AF37; margin: 0 6px;">|</span> 
                            Rank: <b style="color: #FFFFFF;">#{rank_single_str}</b>
                        </div>
                        <div style="font-size: 12px; color: #A0A0A0;">
                            Total competidores: <span style="color: #FFFFFF;">{total_single_str}</span>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 10px; color: #D4AF37; letter-spacing: 1.2px; text-transform: uppercase; font-weight: 600;">Top Mundial</div>
                        <div style="font-size: 34px; font-weight: 900; background: linear-gradient(180deg, #FFE57F 0%, #D4AF37 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{top_single_fmt}</div>
                    </div>
                </div>
                """

                st.markdown(html_card_single, unsafe_allow_html=True)
            else:
                st.info(
                    f"El competidor no tiene registro de **Single** en **{nombre_evento}**."
                )
    else:
        st.error("No se encontraron registros para el WCA ID indicado.")

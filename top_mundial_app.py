import pandas as pd
import requests
import streamlit as st

st.title("Top mundial WCA por Evento")

# 1. Entrada del WCA ID
wca_id = st.text_input("Escribe un WCA_ID: ").strip().upper()

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

        # 2. Obtener lista única de eventos
        eventos_avg = (
            df_averages["eventId"].tolist() if not df_averages.empty else []
        )
        eventos_single = (
            df_singles["eventId"].tolist() if not df_singles.empty else []
        )
        eventos_disponibles = sorted(list(set(eventos_avg + eventos_single)))

        # 3. Desplegable dinámico
        evento_elegido = st.selectbox(
            "Selecciona un evento:", options=eventos_disponibles
        )

        if evento_elegido:
            st.subheader(f"Competidor: {nombre_completo}")

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

                # Formatear números con puntos de miles
                rank_avg_str = f"{rank_avg:,}".replace(",", ".")
                total_avg_str = f"{total_avg:,}".replace(",", ".")

                html_card_avg = f"""
                <div style="
                    background: linear-gradient(135deg, #1e1e2f 0%, #11111d 100%);
                    border: 2px solid #2b2b3d;
                    border-radius: 16px;
                    padding: 20px 25px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
                    color: white;
                    margin-bottom: 20px;
                ">
                    <div>
                        <h3 style="margin: 0; font-size: 18px; color: #FFFFFF;">Average ({evento_elegido})</h3>
                        <p style="margin: 5px 0 0 0; color: #A0A0B0; font-size: 14px;">Tiempo oficial: <b>{tiempo_avg}</b></p>
                        <p style="margin: 3px 0 0 0; color: #A0A0B0; font-size: 13px;">Ranking mundial: <b style="color: #FFFFFF;">#{rank_avg_str}</b></p>
                        <p style="margin: 3px 0 0 0; color: #A0A0B0; font-size: 13px;">Total competidores: <b style="color: #FFFFFF;">{total_avg_str}</b></p>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 12px; color: #A0A0B0; text-transform: uppercase;">Top Mundial</span>
                        <h2 style="margin: 0; color: #00C853; font-size: 24px; font-weight: 800;">{top_avg_fmt}</h2>
                    </div>
                </div>
                """

                st.markdown(html_card_avg, unsafe_allow_html=True)
            else:
                st.info(
                    f"El competidor no tiene registro de **Average** en la categoría {evento_elegido}."
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

                # Formatear números con puntos de miles
                rank_single_str = f"{rank_single:,}".replace(",", ".")
                total_single_str = f"{total_single:,}".replace(",", ".")

                html_card_single = f"""
                <div style="
                    background: linear-gradient(135deg, #1e1e2f 0%, #11111d 100%);
                    border: 2px solid #2b2b3d;
                    border-radius: 16px;
                    padding: 20px 25px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
                    color: white;
                ">
                    <div>
                        <h3 style="margin: 0; font-size: 18px; color: #FFFFFF;">Single ({evento_elegido})</h3>
                        <p style="margin: 5px 0 0 0; color: #A0A0B0; font-size: 14px;">Tiempo oficial: <b>{tiempo_single}</b></p>
                        <p style="margin: 3px 0 0 0; color: #A0A0B0; font-size: 13px;">Ranking mundial: <b style="color: #FFFFFF;">#{rank_single_str}</b></p>
                        <p style="margin: 3px 0 0 0; color: #A0A0B0; font-size: 13px;">Total competidores: <b style="color: #FFFFFF;">{total_single_str}</b></p>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 12px; color: #A0A0B0; text-transform: uppercase;">Top Mundial</span>
                        <h2 style="margin: 0; color: #00C853; font-size: 24px; font-weight: 800;">{top_single_fmt}</h2>
                    </div>
                </div>
                """

                st.markdown(html_card_single, unsafe_allow_html=True)
            else:
                st.info(
                    f"El competidor no tiene registro de **Single** en la categoría {evento_elegido}."
                )
    else:
        st.error("No se encontró el WCA_ID introducido.")

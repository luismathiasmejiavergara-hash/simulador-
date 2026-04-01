from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st


COPPER_RESISTIVITY = 1.68e-8
ALUMINUM_RESISTIVITY = 2.82e-8
CONDUCTORS = {
    "Cobre": COPPER_RESISTIVITY,
    "Aluminio": ALUMINUM_RESISTIVITY,
}


def mm2_to_m2(area_mm2: float) -> float:
    """Convierte un area en mm2 a m2."""
    return area_mm2 * 1e-6


def calculate_resistance(resistivity: float, length_m: float, area_mm2: float) -> float:
    """Calcula la resistencia del conductor."""
    return resistivity * (length_m / mm2_to_m2(area_mm2))


def calculate_joule_losses(current_a: float, resistance_ohm: float) -> float:
    """Calcula la potencia disipada por efecto Joule."""
    return (current_a**2) * resistance_ohm


def calculate_voltage_drop(current_a: float, resistance_ohm: float) -> float:
    """Calcula el voltaje sobre el conductor usando la ley de Ohm."""
    return current_a * resistance_ohm


def calculate_efficiency(supply_voltage_v: float, current_a: float, power_loss_w: float) -> float:
    """Estima la eficiencia energetica a partir de la potencia de entrada y las perdidas."""
    input_power_w = supply_voltage_v * current_a
    if input_power_w <= 0:
        return 0.0
    efficiency = (input_power_w - power_loss_w) / input_power_w * 100
    return float(np.clip(efficiency, 0, 100))


def build_current_vs_power_curve(
    current_max_a: float,
    resistivity: float,
    length_m: float,
    area_mm2: float,
) -> pd.DataFrame:
    """Genera la curva Corriente vs Potencia disipada."""
    current_values = np.linspace(1, current_max_a, 100)
    resistance = calculate_resistance(resistivity, length_m, area_mm2)
    power_values = calculate_joule_losses(current_values, resistance)
    return pd.DataFrame(
        {
            "Corriente (A)": current_values,
            "Potencia disipada (W)": power_values,
        }
    )


def build_length_vs_resistance_curve(
    length_max_m: float,
    resistivity: float,
    area_mm2: float,
) -> pd.DataFrame:
    """Genera la curva Longitud vs Resistencia."""
    length_values = np.linspace(5, length_max_m, 100)
    resistance_values = calculate_resistance(resistivity, length_values, area_mm2)
    return pd.DataFrame(
        {
            "Longitud del cable (m)": length_values,
            "Resistencia (Ohm)": resistance_values,
        }
    )


def build_current_vs_efficiency_curve(
    current_max_a: float,
    resistivity: float,
    length_m: float,
    area_mm2: float,
    supply_voltage_v: float,
) -> pd.DataFrame:
    """Genera la curva Corriente vs Eficiencia."""
    current_values = np.linspace(1, current_max_a, 100)
    resistance = calculate_resistance(resistivity, length_m, area_mm2)
    losses = calculate_joule_losses(current_values, resistance)
    efficiencies = [calculate_efficiency(supply_voltage_v, current, loss) for current, loss in zip(current_values, losses)]
    return pd.DataFrame(
        {
            "Corriente (A)": current_values,
            "Eficiencia (%)": efficiencies,
        }
    )


def get_status_message(power_loss_w: float, efficiency_pct: float) -> tuple[str, str]:
    """Define el mensaje automatico de estado del sistema."""
    if power_loss_w >= 120 or efficiency_pct < 85:
        return "Alta perdida de energia", "error"
    if efficiency_pct >= 95 and power_loss_w <= 40:
        return "Sistema eficiente", "success"
    return "Perdidas moderadas", "warning"


def render_status(message: str, level: str) -> None:
    """Muestra el estado usando el componente visual mas adecuado."""
    if level == "error":
        st.error(message)
    elif level == "success":
        st.success(message)
    else:
        st.warning(message)


def apply_custom_styles() -> None:
    """Agrega una capa visual simple para mejorar la interfaz."""
    st.markdown(
        """
        <style>
            :root {
                --page-bg: #eef4f9;
                --card-bg: rgba(255, 255, 255, 0.96);
                --card-border: rgba(18, 52, 77, 0.10);
                --text-main: #12344d;
                --text-soft: #486581;
                --accent: #e4572e;
                --accent-soft: rgba(228, 87, 46, 0.12);
            }
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(12, 85, 136, 0.12), transparent 28%),
                    linear-gradient(180deg, #f7fbff 0%, var(--page-bg) 100%);
                color: var(--text-main);
            }
            .hero-card {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(246, 250, 253, 0.92));
                border: 1px solid rgba(12, 85, 136, 0.10);
                border-radius: 24px;
                padding: 1.5rem 1.7rem;
                box-shadow: 0 16px 40px rgba(24, 39, 75, 0.10);
                margin-bottom: 1.2rem;
                backdrop-filter: blur(10px);
            }
            .hero-card h1 {
                color: var(--text-main);
                font-size: clamp(2rem, 3.2vw, 3rem);
                line-height: 1.08;
                margin-bottom: 0.55rem;
            }
            .hero-card p {
                color: var(--text-soft);
                font-size: 1.1rem;
                margin-bottom: 0;
            }
            .metric-caption {
                color: var(--text-soft);
                font-size: 1rem;
                margin-top: -0.2rem;
            }
            .metric-caption strong {
                color: var(--text-main);
            }
            [data-testid="stSidebar"] {
                background: rgba(18, 52, 77, 0.96);
            }
            [data-testid="stSidebar"] * {
                color: #f8fbff;
            }
            [data-testid="stHeading"] h1,
            [data-testid="stHeading"] h2,
            [data-testid="stHeading"] h3,
            .stMarkdown h1,
            .stMarkdown h2,
            .stMarkdown h3,
            .stMarkdown h4,
            p,
            label,
            span,
            div {
                color: inherit;
            }
            h2, h3, h4 {
                color: var(--text-main) !important;
            }
            div[data-testid="stMetric"] {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 18px;
                padding: 0.95rem 0.9rem;
                box-shadow: 0 10px 24px rgba(24, 39, 75, 0.08);
            }
            div[data-testid="stMetricLabel"] {
                color: var(--text-soft) !important;
                font-weight: 600;
            }
            div[data-testid="stMetricValue"] {
                color: var(--text-main) !important;
                font-weight: 700;
            }
            div[data-testid="stMetricDelta"] {
                color: var(--text-soft) !important;
            }
            div[data-testid="stAlert"] {
                border-radius: 18px;
                font-weight: 600;
            }
            div[data-testid="stAlert"] p {
                font-size: 1.1rem;
            }
            [data-testid="stChart"] {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 18px;
                padding: 0.6rem;
                box-shadow: 0 10px 24px rgba(24, 39, 75, 0.06);
            }
            [data-testid="stDivider"] {
                background-color: rgba(18, 52, 77, 0.12);
            }
            .stCaption {
                color: var(--text-soft) !important;
                font-size: 0.96rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Simulador de Perdidas por Efecto Joule",
        page_icon="SJ",
        layout="wide",
    )

    apply_custom_styles()

    st.markdown(
        """
        <div class="hero-card">
            <h1>Simulador de Perdidas por Efecto Joule</h1>
            <p>Explora en tiempo real el impacto de la corriente, la geometria del cable y el material conductor sobre las perdidas energeticas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.header("Parametros de entrada")
    current_a = st.sidebar.slider("Corriente (A)", min_value=1.0, max_value=15.0, value=8.0, step=0.5)
    length_m = st.sidebar.slider("Longitud del cable (m)", min_value=5.0, max_value=120.0, value=45.0, step=1.0)
    area_mm2 = st.sidebar.slider("Area del cable (mm2)", min_value=1.0, max_value=12.0, value=4.0, step=0.5)
    conductor = st.sidebar.selectbox("Tipo de conductor", options=list(CONDUCTORS.keys()))
    supply_voltage_v = st.sidebar.slider("Voltaje de alimentacion (V)", min_value=110, max_value=220, value=127, step=1)

    resistivity = CONDUCTORS[conductor]
    resistance_ohm = calculate_resistance(resistivity, length_m, area_mm2)
    power_loss_w = calculate_joule_losses(current_a, resistance_ohm)
    voltage_drop_v = calculate_voltage_drop(current_a, resistance_ohm)
    efficiency_pct = calculate_efficiency(supply_voltage_v, current_a, power_loss_w)
    input_power_w = supply_voltage_v * current_a
    loss_ratio_pct = (power_loss_w / input_power_w * 100) if input_power_w else 0.0

    message, level = get_status_message(power_loss_w, efficiency_pct)
    render_status(message, level)

    st.subheader("Analisis de eficiencia energetica")

    metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)
    metric_col_1.metric("Resistencia total", f"{resistance_ohm:.4f} ohm")
    metric_col_2.metric("Potencia disipada", f"{power_loss_w:.2f} W")
    metric_col_3.metric("Voltaje en el conductor", f"{voltage_drop_v:.2f} V")
    metric_col_4.metric("Eficiencia estimada", f"{efficiency_pct:.2f} %")

    info_col_1, info_col_2, info_col_3 = st.columns(3)
    info_col_1.markdown(f'<p class="metric-caption">Potencia de entrada estimada: <strong>{input_power_w:.2f} W</strong></p>', unsafe_allow_html=True)
    info_col_2.markdown(f'<p class="metric-caption">Perdida relativa: <strong>{loss_ratio_pct:.2f} %</strong></p>', unsafe_allow_html=True)
    info_col_3.markdown(f'<p class="metric-caption">Material seleccionado: <strong>{conductor}</strong></p>', unsafe_allow_html=True)

    st.divider()

    chart_col_1, chart_col_2 = st.columns(2)

    with chart_col_1:
        st.markdown("#### Corriente vs Potencia disipada")
        current_power_df = build_current_vs_power_curve(current_a, resistivity, length_m, area_mm2)
        st.line_chart(current_power_df, x="Corriente (A)", y="Potencia disipada (W)", use_container_width=True)

    with chart_col_2:
        st.markdown("#### Longitud vs Resistencia")
        length_resistance_df = build_length_vs_resistance_curve(length_m, resistivity, area_mm2)
        st.line_chart(length_resistance_df, x="Longitud del cable (m)", y="Resistencia (Ohm)", use_container_width=True)

    st.markdown("#### Corriente vs Eficiencia")
    current_efficiency_df = build_current_vs_efficiency_curve(current_a, resistivity, length_m, area_mm2, supply_voltage_v)
    st.area_chart(current_efficiency_df, x="Corriente (A)", y="Eficiencia (%)", use_container_width=True)

    st.caption(
        "Los resultados se actualizan automaticamente a medida que cambias los controles. "
        "El area del conductor se convierte internamente de mm2 a m2 para mantener coherencia dimensional."
    )


if __name__ == "__main__":
    main()

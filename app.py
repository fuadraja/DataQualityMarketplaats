import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Data quality checks volgens DAMA

def completeness_check(df, columns):
    return {col: df[col].notnull().mean() * 100 for col in columns}

def uniqueness_check(df, columns):
    return {col: df[col].is_unique for col in columns}

def consistency_check(df, columns):
    results = {}
    for col in columns:
        dtype_consistent = df[col].map(type).nunique() == 1
        results[col] = dtype_consistent
    return results

def validity_check(df, columns):
    results = {}
    numeric_keywords = ['id', 'leeftijd', 'aantal', 'prijs', 'nummer']
    text_keywords = ['naam', 'adres', 'plaats', 'beschrijving']
    for col in columns:
        col_lower = col.lower()
        if any(keyword.lower() in col_lower for keyword in numeric_keywords):
            valid_count = pd.to_numeric(df[col], errors='coerce').notnull().sum()
            validity = (valid_count / len(df[col])) * 100
        elif any(keyword.lower() in col_lower for keyword in text_keywords):
            valid_count = df[col].astype(str).apply(lambda x: isinstance(x, str) and x.strip() != '').sum()
            validity = (valid_count / len(df[col])) * 100
        else:
            validity = 100.0
        results[col] = validity
    return results

def date_range_check(df, columns, start_date, end_date):
    results = {}
    for col in columns:
        try:
            col_parsed = pd.to_datetime(df[col], errors='coerce').dt.date
            in_range = col_parsed.between(start_date, end_date).sum()
            validity = (in_range / len(df[col])) * 100
            results[col] = validity
        except:
            results[col] = 0.0
    return results

check_definitions = {
    'Completeness': "Mate waarin alle vereiste data aanwezig is (geen lege waarden).",
    'Uniqueness': "Data bevat geen duplicaten; elke waarde is uniek.",
    'Consistency': "Data is logisch en structureel samenhangend binnen datasets.",
    'Validity': "Data voldoet aan het verwachte formaat, type of regels (bijv. getallen in getalvelden of tekst in tekstvelden).",
    'Datumvalidatie': "Datumwaarden liggen binnen een opgegeven tijdsperiode."
}

checks = {
    'Completeness': completeness_check,
    'Uniqueness': uniqueness_check,
    'Consistency': consistency_check,
    'Validity': validity_check,
    'Datumvalidatie': date_range_check
}

st.title("🛒 Data Quality Marketplace Demo")

uploaded_file = st.file_uploader("Upload Excel-bestand", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file, parse_dates=True)
    for col in df.select_dtypes(include=['datetime']).columns:
        df[col] = df[col].dt.date

    st.write("### Preview van je dataset:")
    st.dataframe(df.head())

    selected_checks = st.multiselect("Selecteer Data Quality Checks", list(checks.keys()))

    for check in selected_checks:
        st.markdown(f"**{check}**: {check_definitions[check]}")

    columns = st.multiselect("Selecteer kolommen voor checks", df.columns)

    user_kpis = {}
    for check in selected_checks:
        if check in ['Completeness', 'Validity', 'Datumvalidatie']:
            user_kpis[check] = st.slider(f"KPI voor {check} (%)", 0, 100, 90)
        elif check in ['Uniqueness', 'Consistency']:
            user_kpis[check] = st.selectbox(f"KPI voor {check}", [True, False])

    start_date = end_date = None
    if 'Datumvalidatie' in selected_checks:
        st.markdown("### Datumvalidatie instellingen")
        start_date = st.date_input("Startdatum", value=pd.to_datetime("2020-01-01"))
        end_date = st.date_input("Einddatum", value=pd.to_datetime("2025-12-31"))

    if st.button("Voer checks uit"):
        for check_name in selected_checks:
            st.subheader(f"Resultaten voor {check_name}:")

            if check_name == 'Datumvalidatie':
                result = checks[check_name](df, columns, start_date, end_date)
            else:
                result = checks[check_name](df, columns)

            for col, value in result.items():
                kpi = user_kpis[check_name]
                if isinstance(value, bool):
                    status = "✅ Geslaagd" if value == kpi else "❌ Niet geslaagd"
                    value_display = "Consistent" if value else "Inconsistent"
                    kpi_display = "Consistent" if kpi else "Inconsistent toegestaan"
                    st.write(f"Kolom **{col}**: {value_display} (KPI: {kpi_display}) - {status}")
                else:
                    status = "✅ Geslaagd" if value >= kpi else "❌ Niet geslaagd"
                    st.write(f"Kolom **{col}**: {value:.2f}% (KPI: {kpi}%) - {status}")

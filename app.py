import streamlit as st
import pandas as pd

def completeness_check(df, columns):
    results = {}
    for col in columns:
        completeness = df[col].notnull().mean() * 100
        results[col] = completeness
    return results

def uniqueness_check(df, columns):
    results = {}
    for col in columns:
        uniqueness = df[col].is_unique
        results[col] = uniqueness
    return results

checks = {
    'Completeness': completeness_check,
    'Uniqueness': uniqueness_check
}

st.title("🛒 Data Quality Marketplace Demo")

uploaded_file = st.file_uploader("Upload Excel-bestand", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.write("### Preview van je dataset:")
    st.dataframe(df.head())

    selected_checks = st.multiselect("Selecteer Data Quality Checks", list(checks.keys()))

    columns = st.multiselect("Selecteer kolommen voor checks", df.columns)

    user_kpis = {}
    for check in selected_checks:
        if check == 'Completeness':
            user_kpis[check] = st.slider(f"KPI voor {check} (%)", 0, 100, 90)
        elif check == 'Uniqueness':
            user_kpis[check] = st.selectbox(f"KPI voor {check}", [True, False])

    if st.button("Voer checks uit"):
        for check_name in selected_checks:
            st.subheader(f"Resultaten voor {check_name}:")
            result = checks[check_name](df, columns)
            
            for col, value in result.items():
                kpi = user_kpis[check_name]
                if isinstance(value, bool):
                    status = "✅ Geslaagd" if value == kpi else "❌ Niet geslaagd"
                    st.write(f"Kolom **{col}**: {value} (KPI: {kpi}) - {status}")
                else:
                    status = "✅ Geslaagd" if value >= kpi else "❌ Niet geslaagd"
                    st.write(f"Kolom **{col}**: {value:.2f}% (KPI: {kpi}%) - {status}")

import streamlit as st
import pandas as pd

# Data quality checks volgens DAMA

def completeness_check(df, columns):
    return {col: df[col].notnull().mean() * 100 for col in columns}

def uniqueness_check(df, columns):
    return {col: df[col].is_unique for col in columns}

def accuracy_check(df, columns):
    # Dummy check: simulatie dat alles accuraat is
    return {col: 100.0 for col in columns}

def consistency_check(df, columns):
    # Dummy check: altijd consistent
    return {col: True for col in columns}

def validity_check(df, columns):
    # Dummy check: alles geldig
    return {col: 100.0 for col in columns}

def timeliness_check(df, columns):
    # Dummy check: 100% op tijd
    return {col: 100.0 for col in columns}

check_definitions = {
    'Completeness': "Mate waarin alle vereiste data aanwezig is (geen lege waarden).",
    'Uniqueness': "Data bevat geen duplicaten; elke waarde is uniek.",
    'Accuracy': "Mate waarin data correct is en overeenkomt met de werkelijkheid.",
    'Consistency': "Data is logisch en structureel samenhangend binnen datasets.",
    'Validity': "Data voldoet aan het verwachte formaat, type of regels (bijv. e-mailformaat).",
    'Timeliness': "Data is actueel en beschikbaar op het moment dat het nodig is."
}

checks = {
    'Completeness': completeness_check,
    'Uniqueness': uniqueness_check,
    'Accuracy': accuracy_check,
    'Consistency': consistency_check,
    'Validity': validity_check,
    'Timeliness': timeliness_check
}

st.title("🛒 Data Quality Marketplace Demo")

uploaded_file = st.file_uploader("Upload Excel-bestand", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.write("### Preview van je dataset:")
    st.dataframe(df.head())

    selected_checks = st.multiselect("Selecteer Data Quality Checks", list(checks.keys()))

    # Toon definities van geselecteerde checks
    for check in selected_checks:
        st.markdown(f"**{check}**: {check_definitions[check]}")

    columns = st.multiselect("Selecteer kolommen voor checks", df.columns)

    user_kpis = {}
    for check in selected_checks:
        if check in ['Completeness', 'Accuracy', 'Validity', 'Timeliness']:
            user_kpis[check] = st.slider(f"KPI voor {check} (%)", 0, 100, 90)
        elif check in ['Uniqueness', 'Consistency']:
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

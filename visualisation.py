import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file, sep=';', skip_blank_lines=True)
    df.columns = df.columns.str.strip().str.lower()

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce', dayfirst=True)

    if 'heure' in df.columns:
        df['heure'] = pd.to_datetime(df['heure'], format='%H:%M:%S', errors='coerce').dt.hour

    def detect_bottype(ua):
        ua = str(ua).lower()
        if "google" in ua:
            return "Googlebot"
        elif "semrush" in ua:
            return "SemrushBot"
        elif "ahrefs" in ua:
            return "AhrefsBot"
        elif "bot" in ua or "spider" in ua or "crawl" in ua:
            return "OtherBot"
        else:
            return "Human"

if 'user-agent' in df.columns:
    df['bottype'] = df['user-agent'].apply(detect_bottype)
    return df

def apply_filters(df):
    st.sidebar.header("🔍 Filtres")

    if 'date' in df.columns:
        dates = df['date'].dropna().dt.date.unique()
        selected = st.sidebar.multiselect("📅 Date", sorted(dates))
        if selected:
            df = df[df['date'].dt.date.isin(selected)]

    if 'country' in df.columns:
        countries = df['country'].dropna().unique()
        selected = st.sidebar.multiselect("🌍 Pays", sorted(countries))
        if selected:
            df = df[df['country'].isin(selected)]

    if 'heure' in df.columns:
        hours = sorted(df['heure'].dropna().unique())
        selected = st.sidebar.multiselect("⏰ Heure", hours)
        if selected:
            df = df[df['heure'].isin(selected)]

    if 'bottype' in df.columns:
    st.sidebar.markdown("### 🧠 Type de visiteur")
    bot_filter = st.sidebar.radio("Filtrer par :", ["Tous", "Humain", "Bots"])

    if bot_filter == "Humain":
        df = df[df['bottype'] == "Human"]
    elif bot_filter == "Bots":
        df = df[df['bottype'] != "Human"]


    return df

def visualisation_page(df):
    df = apply_filters(df)
    st.header("📊 Visualisations")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Régénérer les graphiques"):
            st.rerun()
    with col2:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Télécharger les données filtrées", csv, "data_filtree.csv", "text/csv")

    # Graphes fixes
    if 'heure' in df.columns and 'ip' in df.columns:
        st.subheader("1️⃣ Nombre d’IP par heure")
        data = df.groupby('heure')['ip'].nunique().reset_index()
        st.plotly_chart(px.bar(data, x='heure', y='ip', labels={'ip': "Nombre d'IP"}))

    if 'country' in df.columns and 'ip' in df.columns:
        st.subheader("2️⃣ Nombre d’IP par pays")
        data = df.groupby('country')['ip'].nunique().reset_index().sort_values(by='ip', ascending=True)
        st.plotly_chart(px.bar(data, x='ip', y='country', orientation='h'))

    if 'city' in df.columns and 'ip' in df.columns:
        st.subheader("3️⃣ Nombre d’IP par ville")
        data = df.groupby('city')['ip'].nunique().reset_index().sort_values(by='ip', ascending=False)
        st.plotly_chart(px.pie(data, names='city', values='ip', hole=0.4))

    if all(col in df.columns for col in ['country', 'city', 'ip']):
        st.subheader("4️⃣ Nombre d’IP par ville et pays")
        data = df.groupby(['country', 'city'])['ip'].nunique().reset_index()
        st.plotly_chart(px.bar(data, x='city', y='ip', color='country', barmode='stack'))

    if all(col in df.columns for col in ['date', 'bottype', 'visiteur']):
        st.subheader("5️⃣ Nombre de visiteurs par date et BotType")
        data = df.groupby(['date', 'bottype'])['visiteur'].nunique().reset_index()
        st.plotly_chart(px.bar(data, x='date', y='visiteur', color='bottype', barmode='stack'))

    if all(col in df.columns for col in ['date', 'bottype', 'ip']):
        st.subheader("6️⃣ Nombre d’IP par date et BotType")
        data = df.groupby(['date', 'bottype'])['ip'].nunique().reset_index()
        st.plotly_chart(px.bar(data, x='date', y='ip', color='bottype', barmode='group'))

    if 'url' in df.columns:
        st.subheader("7️⃣ Top 10 des URLs visitées")
        data = df['url'].value_counts().reset_index().head(10)
        data.columns = ['url', 'count']
        st.plotly_chart(px.bar(data, x='url', y='count'))

    if all(col in df.columns for col in ['bottype', 'user-agent']):
        st.subheader("8️⃣ Nombre de User-Agent distincts par BotType")
        data = df.groupby('bottype')['user-agent'].nunique().reset_index()
        data.columns = ['bottype', 'nb_user_agent']
        st.plotly_chart(px.bar(data, x='bottype', y='nb_user_agent', color='bottype'))

def custom_visualisation(df):
    if 'custom_charts' not in st.session_state:
        st.session_state['custom_charts'] = []

    st.header("🎨 Créer votre propre graphique")
    columns = df.columns.tolist()

    x_axis = st.selectbox("🧭 Axe X :", columns, index=0)
    y_axis = st.selectbox("📊 Axe Y :", columns, index=1)

    chart_type = st.selectbox("📈 Type :", ["Bar", "Line", "Scatter", "Pie"])

    title = st.text_input("✏️ Titre :", f"{chart_type} de {y_axis} par {x_axis}")

    if st.button("🚀 Générer le graphique"):
        if chart_type == "Bar":
            fig = px.bar(df, x=x_axis, y=y_axis, title=title)
        elif chart_type == "Line":
            fig = px.line(df, x=x_axis, y=y_axis, title=title)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_axis, y=y_axis, title=title)
        elif chart_type == "Pie":
            fig = px.pie(df, names=x_axis, values=y_axis, title=title, hole=0.3)
        else:
            st.warning("Type non pris en charge.")
            return

        st.plotly_chart(fig, use_container_width=True)
        st.session_state['custom_charts'].append({'title': title, 'fig': fig})

def overview_page(df):
    st.header("🧾 Vue d’ensemble :")

    visualisation_page(df)

    if 'custom_charts' in st.session_state and st.session_state['custom_charts']:
        st.subheader("🎨 Graphiques personnalisés")
        for chart in st.session_state['custom_charts']:
            st.markdown(f"**{chart['title']}**")
            st.plotly_chart(chart['fig'], use_container_width=True)
    else:
        st.info("Aucun graphique personnalisé ajouté.")





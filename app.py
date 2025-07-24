import streamlit as st
from visualisation import load_data, visualisation_page, custom_visualisation, overview_page

# Simuler une base d’utilisateurs
if 'USERS' not in st.session_state:
    st.session_state['USERS'] = {"user1": "pass1", "user2": "pass2"}

def login_page():
    st.title("🔐 Authentification")
    tab1, tab2 = st.tabs(["Se connecter", "S’inscrire"])

    with tab1:
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if username in st.session_state['USERS'] and st.session_state['USERS'][username] == password:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

    with tab2:
        new_user = st.text_input("Créer un nom d'utilisateur")
        new_pass = st.text_input("Créer un mot de passe", type="password")
        if st.button("S’inscrire"):
            if new_user in st.session_state['USERS']:
                st.error("Nom d'utilisateur déjà existant.")
            else:
                st.session_state['USERS'][new_user] = new_pass
                st.success("Inscription réussie. Veuillez vous connecter.")

def main_page():
    st.sidebar.title("📁 Téléversez vos données")
    uploaded_file = st.sidebar.file_uploader("Charger un fichier CSV", type=['csv'])

    if uploaded_file:
        df = load_data(uploaded_file)
        st.title("📊 Tableau de Bord - Analyse des Logs")

        menu = st.radio(
            "Navigation", 
            ["📄 Données", "📊 Visualiser", "🔀 Combiner", "🧾 Vue d'ensemble"],
            horizontal=True
        )

        if menu == "📄 Données":
            st.subheader("Aperçu des données brutes")
            st.dataframe(df)

        elif menu == "📊 Visualiser":
            visualisation_page(df)

        elif menu == "🔀 Combiner":
            custom_visualisation(df)

        elif menu == "🧾 Vue d'ensemble":
            overview_page(df)

    else:
        st.markdown(
            "<h3 style='text-align: center;'>📤 Veuillez importer un fichier CSV pour continuer</h3>", 
            unsafe_allow_html=True
        )

def main():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        login_page()
    else:
        main_page()

if __name__ == "__main__":
    main()

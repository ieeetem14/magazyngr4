import streamlit as st
from supabase import create_client, Client

# Konfiguracja połączenia z Supabase
# Na Streamlit Cloud dodaj te dane w zakładce "Settings" -> "Secrets"
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(URL, KEY)

st.title("📦 Menadżer Produktów i Kategorii")

# --- SEKCJA KATEGORIE ---
st.header("📂 Kategorie")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Dodaj kategorię")
    with st.form("add_category_form", clear_on_submit=True):
        kat_nazwa = st.text_input("Nazwa kategorii")
        kat_opis = st.text_area("Opis")
        submit_kat = st.form_submit_button("Dodaj kategorię")
        
        if submit_kat and kat_nazwa:
            data = {"nazwa": kat_nazwa, "opis": kat_opis}
            response = supabase.table("kategorie").insert(data).execute()
            st.success(f"Dodano kategorię: {kat_nazwa}")

with col2:
    st.subheader("Usuń kategorię")
    # Pobieranie listy kategorii do selectboxa
    kategorie_raw = supabase.table("kategorie").select("id, nazwa").execute()
    lista_kat = {item['nazwa']: item['id'] for item in kategorie_raw.data}
    
    kat_do_usuniecia = st.selectbox("Wybierz kategorię do usunięcia", options=list(lista_kat.keys()))
    if st.button("Usuń kategorię"):
        kat_id = lista_kat[kat_do_usuniecia]
        # Uwaga: Usunięcie kategorii może się nie udać, jeśli są do niej przypisane produkty (klucz obcy)
        try:
            supabase.table("kategorie").delete().eq("id", kat_id).execute()
            st.warning(f"Usunięto: {kat_do_usuniecia}")
            st.rerun()
        except Exception as e:
            st.error(f"Błąd: Prawdopodobnie kategoria zawiera produkty. {e}")

st.divider()

# --- SEKCJA PRODUKTY ---
st.header("🛒 Produkty")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Dodaj produkt")
    with st.form("add_product_form", clear_on_submit=True):
        prod_nazwa = st.text_input("Nazwa produktu")
        prod_liczba = st.number_input("Liczba (szt.)", min_value=0, step=1)
        prod_cena = st.number_input("Cena", min_value=0.0, format="%.2f")
        
        # Wybór kategorii z bazy
        wybrana_kat_nazwa = st.selectbox("Kategoria", options=list(lista_kat.keys()))
        
        submit_prod = st.form_submit_button("Dodaj produkt")
        
        if submit_prod and prod_nazwa:
            prod_data = {
                "nazwa": prod_nazwa,
                "liczba": prod_liczba,
                "cena": prod_cena,
                "kategoria_id": lista_kat[wybrana_kat_nazwa]
            }
            supabase.table("produkty").insert(prod_data).execute()
            st.success(f"Dodano produkt: {prod_nazwa}")

with col4:
    st.subheader("Usuń produkt")
    produkty_raw = supabase.table("produkty").select("id, nazwa").execute()
    lista_prod = {item['nazwa']: item['id'] for item in produkty_raw.data}
    
    prod_do_usuniecia = st.selectbox("Wybierz produkt do usunięcia", options=list(lista_prod.keys()))
    if st.button("Usuń produkt"):
        prod_id = lista_prod[prod_do_usuniecia]
        supabase.table("produkty").delete().eq("id", prod_id).execute()
        st.warning(f"Usunięto produkt: {prod_do_usuniecia}")
        st.rerun()

# --- PODGLĄD DANYCH ---
st.divider()
st.subheader("📊 Aktualny stan magazynowy")
view_data = supabase.table("produkty").select("nazwa, liczba, cena, kategorie(nazwa)").execute()
st.table(view_data.data)

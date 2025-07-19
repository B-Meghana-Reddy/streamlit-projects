import streamlit as st
import pyshorteners
import pyperclip

# Function to copy shortened URL to clipboard
def copying(shorted_url):
    pyperclip.copy(shorted_url)
    st.success("Copied to clipboard!")

# Streamlit App UI
st.markdown("<h1 style='text-align: center;'>URL SHORTENER</h1>", unsafe_allow_html=True)

# Create a form
with st.form("shortener_form"):
    url = st.text_input("Enter the URL here")
    submit_btn = st.form_submit_button("Shorten")

if submit_btn:
    try:
        shortener = pyshorteners.Shortener()
        shorted_url = shortener.tinyurl.short(url)
        
        st.markdown("<h3 style='text-align: center;'>Shortened URL</h3>", unsafe_allow_html=True)
        st.markdown(f"<h6 style='text-align: center;'><a href='{shorted_url}' target='_blank'>{shorted_url}</a></h6>", unsafe_allow_html=True)
        
        if st.button("Copy"):
            copying(shorted_url)

    except Exception as e:
        st.error(f"Error: {e}")

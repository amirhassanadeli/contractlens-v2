"""Run with: streamlit run app.py"""

import streamlit as st

from ui.chat import render_chat
from ui.session import activate_document, initialize_session
from ui.sidebar import render_language_selector, render_sidebar
from ui.styles import apply_styles
from ui.translations import TEXTS


def main():
    st.set_page_config(
        page_title="ContractLens",
        page_icon="📄",
        layout="centered",
    )
    language = render_language_selector()
    t = TEXTS[language]
    apply_styles(language)
    initialize_session()

    document, document_id = render_sidebar(t, language)
    activate_document(document_id)
    render_chat(t, document)


if __name__ == "__main__":
    main()

import hashlib

import streamlit as st

from .pdf_utils import PDFValidationError, extract_pdf_text
from .session import clear_chat
from .settings import MAX_FILE_BYTES, SAMPLES_DIR


def render_language_selector():
    with st.sidebar:
        language = st.selectbox(
            "Language",
            options=["en", "fa"],
            format_func=lambda value: {
                "fa": "فارسی",
                "en": "English",
            }[value],
            key="ui_language",
        )

    return language


def render_sidebar(t, language):
    selected_document = None
    document_id = None

    with st.sidebar:
        st.title("📄 ContractLens")
        st.caption(t["subtitle"])
        st.info(t["notice"])

        st.divider()
        st.subheader(t["select_contract"])

        source_labels = {
            "english": t["english_pdf"],
            "persian": t["persian_pdf"],
            "upload": t["upload_pdf"],
        }

        source = st.radio(
            t["source"],
            options=["english", "persian", "upload"],
            format_func=lambda value: source_labels[value],
            key="document_source",
        )

        filename = None
        raw = None

        try:
            if source == "english":
                filename = "employment_en.pdf"
                raw = (SAMPLES_DIR / filename).read_bytes()

            elif source == "persian":
                filename = "employment_fa.pdf"
                raw = (SAMPLES_DIR / filename).read_bytes()

            else:
                uploaded_file = st.file_uploader(
                    t["upload_label"],
                    type=["pdf"],
                    help=t["upload_help"],
                    key="uploaded_contract",
                )

                if uploaded_file is not None:
                    if uploaded_file.size > MAX_FILE_BYTES:
                        raise PDFValidationError("large_file")

                    filename = uploaded_file.name
                    raw = uploaded_file.getvalue()

            if raw is not None:
                if len(raw) > MAX_FILE_BYTES:
                    raise PDFValidationError("large_file")

                file_id = hashlib.sha256(
                    filename.encode("utf-8") + b"\0" + raw
                ).hexdigest()

                cached = st.session_state.get("document_cache")

                if cached and cached["id"] == file_id:
                    text = cached["text"]
                else:
                    with st.spinner(t["reading"]):
                        text = extract_pdf_text(raw)

                    st.session_state.document_cache = {
                        "id": file_id,
                        "text": text,
                    }

                selected_document = {
                    "name": filename,
                    "text": text,
                    "raw": raw,
                    "language": (
                        "en" if source == "english"
                        else "fa" if source == "persian"
                        else language
                    ),
                }
                document_id = file_id

                st.success(t["ready"].format(name=filename))

        except FileNotFoundError:
            st.error(t["missing_file"])

        except PDFValidationError as exc:
            st.error(t[exc.args[0]])

        except Exception:
            st.error(t["invalid_pdf"])

        st.divider()

        st.button(
            t["clear"],
            on_click=clear_chat,
            use_container_width=True,
        )

        st.caption(t["history_note"])


    return selected_document, document_id

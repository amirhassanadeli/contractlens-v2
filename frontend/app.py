import hashlib
import os
from io import BytesIO
from pathlib import Path

import requests
import streamlit as st
from pypdf import PdfReader

API_BASE_URL = os.getenv(
    "DJANGO_API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

SAMPLES_DIR = Path(__file__).resolve().parent / "samples"

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_DOCUMENT_CHARS = 30_000

TEXTS = {
    "fa": {
        "subtitle": "دستیار بررسی قراردادها",
        "notice": (
            "نسخه آزمایشی: متن PDF به Django ارسال می‌شود؛ "
            "مدل زبانی هنوز متصل نیست."
        ),
        "select_contract": "انتخاب قرارداد",
        "source": "کدام فایل را استفاده کنیم؟",
        "english_pdf": "PDF انگلیسی پیش‌فرض",
        "persian_pdf": "PDF فارسی پیش‌فرض",
        "upload_pdf": "آپلود PDF خودم",
        "upload_label": "فایل PDF را انتخاب کنید",
        "upload_help": "حداکثر ۵ مگابایت و ۳۰ صفحه",
        "reading": "در حال خواندن PDF...",
        "ready": "فایل آماده است: {name}",
        "missing_file": "فایل پیش‌فرض در پوشه samples پیدا نشد.",
        "invalid_pdf": "خواندن PDF ناموفق بود؛ سالم‌بودن فایل را بررسی کنید.",
        "empty_file": "فایل خالی است.",
        "large_file": "حجم فایل نباید بیشتر از ۵ مگابایت باشد.",
        "encrypted": "PDF رمزگذاری‌شده پشتیبانی نمی‌شود.",
        "many_pages": "PDF باید حداکثر ۳۰ صفحه باشد.",
        "long_text": "متن PDF باید حداکثر ۳۰ هزار نویسه باشد.",
        "no_text": "متنی استخراج نشد؛ PDF اسکن‌شده به OCR نیاز دارد.",
        "clear": "🗑️ پاک‌کردن گفتگو",
        "history_note": (
            "با تغییر قرارداد، گفتگو پاک می‌شود. "
            "تاریخچه در دیتابیس ذخیره نمی‌شود."
        ),
        "title": "💬 گفت‌وگو با ContractLens",
        "active": "قرارداد فعال: {name}",
        "choose_first": "ابتدا یک PDF معتبر از نوار کناری انتخاب کنید.",
        "welcome": (
            "سلام! یک قرارداد PDF انتخاب کنید و درباره آن سؤال بپرسید. "
            "فعلاً در حالت تست اتصال به Django هستیم."
        ),
        "prompt": "درباره قرارداد سؤال بپرسید...",
        "waiting": "در حال دریافت پاسخ از Django...",
        "timeout": "زمان انتظار برای پاسخ تمام شد.",
        "connection": "اتصال به Django برقرار نشد؛ روشن‌بودن سرور را بررسی کنید.",
        "http_error": "بک‌اند خطای HTTP {status} برگرداند.",
        "request_error": "در ارسال درخواست خطایی رخ داد.",
        "response_error": "پاسخ بک‌اند قالب معتبری ندارد.",
        "retry_note": "دوباره تلاش کنید یا گفتگو را پاک کنید.",
        "retry": "تلاش مجدد",
    },

    "en": {
        "subtitle": "Contract review assistant",
        "notice": (
            "Demo mode: PDF text is sent to Django. "
            "No language model is connected yet."
        ),
        "select_contract": "Select a contract",
        "source": "Which file would you like to use?",
        "english_pdf": "Default English PDF",
        "persian_pdf": "Default Persian PDF",
        "upload_pdf": "Upload my PDF",
        "upload_label": "Choose a PDF file",
        "upload_help": "Up to 5 MB and 30 pages",
        "reading": "Reading PDF...",
        "ready": "File ready: {name}",
        "missing_file": "The default file was not found in the samples folder.",
        "invalid_pdf": "Could not read the PDF. Check that the file is valid.",
        "empty_file": "The file is empty.",
        "large_file": "The file must not exceed 5 MB.",
        "encrypted": "Encrypted PDFs are not supported.",
        "many_pages": "The PDF must contain no more than 30 pages.",
        "long_text": "PDF text must not exceed 30,000 characters.",
        "no_text": "No text was extracted. Scanned PDFs require OCR.",
        "clear": "🗑️ Clear conversation",
        "history_note": (
            "Changing the contract clears the conversation. "
            "Chat history is not saved to the database."
        ),
        "title": "💬 Chat with ContractLens",
        "active": "Active contract: {name}",
        "choose_first": "Select a valid PDF from the sidebar first.",
        "welcome": (
            "Hello! Select a PDF contract and ask a question about it. "
            "We are currently testing the Django connection."
        ),
        "prompt": "Ask a question about the contract...",
        "waiting": "Waiting for Django...",
        "timeout": "The request timed out.",
        "connection": "Could not connect to Django. Check that the server is running.",
        "http_error": "The backend returned HTTP {status}.",
        "request_error": "The request could not be sent.",
        "response_error": "The backend returned an invalid response.",
        "retry_note": "Try again or clear the conversation.",
        "retry": "Try again",
    },
}


class PDFValidationError(Exception):
    """An error identified by a translation key."""


st.set_page_config(
    page_title="ContractLens",
    page_icon="📄",
    layout="centered",
)

# Keep stable values regardless of the selected UI language.
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

t = TEXTS[language]
direction = "rtl" if language == "fa" else "ltr"
alignment = "right" if language == "fa" else "left"

st.markdown(
    f"""
    <style>
    /* Text direction follows the selected language. */
    [data-testid="stMarkdownContainer"] {{
        direction: {direction};
        text-align: {alignment};
    }}

    [data-testid="stChatInput"] textarea {{
        direction: {direction};
        text-align: {alignment};
    }}

    /* Shared chat message styling. */
    [data-testid="stChatMessage"] {{
        width: 85%;
        max-width: 85%;
        box-sizing: border-box;
        border-radius: 16px;
        padding: 16px;
        direction: ltr;
    }}

    /* Assistant: bubble and avatar on the left. */
    [data-testid="stChatMessage"]:has(
        [data-testid="stChatMessageAvatarAssistant"]
    ) {{
        margin-left: 0;
        margin-right: auto;
        flex-direction: row;
        background-color: rgba(128, 128, 128, 0.10);
    }}

    /* User: bubble and avatar on the right. */
    [data-testid="stChatMessage"]:has(
        [data-testid="stChatMessageAvatarUser"]
    ) {{
        margin-left: auto;
        margin-right: 0;
        flex-direction: row-reverse;
        background-color: rgba(59, 130, 246, 0.16);
    }}

    [data-testid="stChatMessageContent"] {{
        min-width: 0;
    }}

    /* Keep long text inside the bubble. */
    [data-testid="stChatMessageContent"]
    [data-testid="stMarkdownContainer"] {{
        overflow-wrap: anywhere;
    }}

    @media (max-width: 640px) {{
        [data-testid="stChatMessage"] {{
            width: 95%;
            max-width: 95%;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def clear_chat():
    st.session_state.messages = []
    st.session_state.pending = False


def extract_pdf_text(raw):
    if not raw:
        raise PDFValidationError("empty_file")

    if len(raw) > MAX_FILE_BYTES:
        raise PDFValidationError("large_file")

    reader = PdfReader(BytesIO(raw))

    if reader.is_encrypted:
        raise PDFValidationError("encrypted")

    if len(reader.pages) > 30:
        raise PDFValidationError("many_pages")

    parts = []
    total_chars = 0

    for page in reader.pages:
        page_text = page.extract_text() or ""
        total_chars += len(page_text) + 2

        if total_chars > MAX_DOCUMENT_CHARS:
            raise PDFValidationError("long_text")

        parts.append(page_text)

    text = "\n\n".join(parts).strip()

    if not text:
        raise PDFValidationError("no_text")

    return text


def request_reply(messages, document, response_language):
    response = requests.post(
        f"{API_BASE_URL}/api/chat/",
        json={
            "messages": messages,
            "document": document,
            "language": response_language,
        },
        timeout=(5, 60),
    )

    response.raise_for_status()
    data = response.json()

    if not isinstance(data, dict):
        raise ValueError("Invalid response format.")

    reply = data.get("reply")

    if not isinstance(reply, str) or not reply.strip():
        raise ValueError("Missing reply.")

    return reply


if "messages" not in st.session_state:
    clear_chat()

if "pending" not in st.session_state:
    st.session_state.pending = False

if "active_document_id" not in st.session_state:
    st.session_state.active_document_id = None

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

if st.session_state.active_document_id != document_id:
    clear_chat()
    st.session_state.active_document_id = document_id

st.title(t["title"])

if selected_document:
    st.caption(t["active"].format(name=selected_document["name"]))
else:
    st.warning(t["choose_first"])

# The greeting changes language without altering chat history.
with st.chat_message("assistant"):
    st.markdown(t["welcome"])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input(
    t["prompt"],
    disabled=(
            st.session_state.pending
            or selected_document is None
    ),
    max_chars=8000,
)

if prompt and prompt.strip():
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt.strip(),
        }
    )
    st.session_state.pending = True
    st.rerun()

if st.session_state.pending and selected_document is not None:
    error_message = None

    with st.chat_message("assistant"):
        with st.spinner(t["waiting"]):
            try:
                history = st.session_state.messages[-49:]

                reply = request_reply(
                    history,
                    selected_document,
                    language,
                )

            except requests.exceptions.Timeout:
                error_message = t["timeout"]

            except requests.exceptions.ConnectionError:
                error_message = t["connection"]

            except requests.exceptions.HTTPError as exc:
                error_message = t["http_error"].format(
                    status=exc.response.status_code
                )

            except requests.exceptions.RequestException:
                error_message = t["request_error"]

            except ValueError:
                error_message = t["response_error"]

    if error_message:
        st.error(error_message)
        st.caption(t["retry_note"])

        if st.button(t["retry"]):
            st.rerun()

    else:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": reply,
            }
        )
        st.session_state.pending = False
        st.rerun()

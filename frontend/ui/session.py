"""Conversation state and orchestration of the upload/chat API flow."""

from pathlib import Path

import streamlit as st

from .api_client import post_api, require_id, parse_message


def clear_chat():
    st.session_state.messages = []
    st.session_state.pending = False
    st.session_state.conversation_id = None


def initialize_session():
    if "messages" not in st.session_state:
        clear_chat()

    if "pending" not in st.session_state:
        st.session_state.pending = False

    if "active_document_id" not in st.session_state:
        st.session_state.active_document_id = None


def activate_document(document_id):
    if st.session_state.active_document_id != document_id:
        clear_chat()
        st.session_state.active_document_id = document_id
        st.session_state.contract_id = None


def request_reply(messages, document):
    # Persist each completed step before starting the next request.
    if not st.session_state.get("contract_id"):
        contract = post_api(
            "contracts/",
            data={
                "title": Path(document["name"]).stem[:200],
                "language": document["language"].upper(),
            },
            files={
                "file": (document["name"], document["raw"], "application/pdf"),
            },
        )
        st.session_state.contract_id = require_id(contract)

    if not st.session_state.get("conversation_id"):
        conversation = post_api(
            "conversations/",
            json={
                "contract_id": st.session_state.contract_id,
                "title": "Contract chat",
            },
        )
        st.session_state.conversation_id = require_id(conversation)

    data = post_api(
        f"conversations/{st.session_state.conversation_id}/messages/",
        json={"content": messages[-1]["content"]},
    )
    return parse_message(data)

import requests
import streamlit as st

from .api_client import regenerate_message, set_feedback
from .session import request_reply


def render_message_actions(index, message, t):
    message_id = message.get("id")
    if not message_id:
        st.caption(t["legacy_message"])
        return

    disabled = st.session_state.pending
    liked = message.get("liked")
    like_col, dislike_col, regenerate_col = st.columns([1, 1, 2])
    with like_col:
        like_clicked = st.button(
            t["like"], key=f"like_{message_id}",
            type="primary" if liked is True else "secondary",
            disabled=disabled or liked is True,
        )
    with dislike_col:
        dislike_clicked = st.button(
            t["dislike"], key=f"dislike_{message_id}",
            type="primary" if liked is False else "secondary",
            disabled=disabled or liked is False,
        )
    with regenerate_col:
        regenerate_clicked = st.button(
            t["regenerate"], key=f"regenerate_{message_id}",
            disabled=disabled,
        )

    if not (like_clicked or dislike_clicked or regenerate_clicked):
        return

    try:
        with st.spinner(t["regenerating"] if regenerate_clicked else t["saving"]):
            if regenerate_clicked:
                updated = regenerate_message(message_id)
            else:
                updated = set_feedback(message_id, like_clicked)
        # Only update the UI after the server confirms success.
        # Regeneration replaces the visible version, not the database history.
        st.session_state.messages[index] = updated
    except requests.exceptions.Timeout:
        st.error(t["timeout"])
        st.caption(t["retry_note"])
        return
    except requests.exceptions.ConnectionError:
        st.error(t["connection"])
        return
    except requests.exceptions.HTTPError as exc:
        st.error(t["http_error"].format(status=exc.response.status_code))
        return
    except requests.exceptions.RequestException:
        st.error(t["request_error"])
        return
    except ValueError:
        st.error(t["response_error"])
        return
    st.rerun()


def render_chat(t, selected_document):
    st.title(t["title"])

    if selected_document:
        st.caption(t["active"].format(name=selected_document["name"]))
    else:
        st.warning(t["choose_first"])

    # The greeting changes language without altering chat history.
    with st.chat_message("assistant"):
        st.markdown(t["welcome"])

    for index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_message_actions(index, message, t)

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
                    )

                except requests.exceptions.Timeout:
                    error_message = t["timeout"]

                except requests.exceptions.ConnectionError:
                    error_message = t["connection"]

                except requests.exceptions.HTTPError as exc:
                    error_message = (
                        f"HTTP {exc.response.status_code}\n\n"
                        f"{exc.response.text}"
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
            st.session_state.messages.append(reply)
            st.session_state.pending = False
            st.rerun()

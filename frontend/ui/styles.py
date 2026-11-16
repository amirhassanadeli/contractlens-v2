import streamlit as st


def apply_styles(language):
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

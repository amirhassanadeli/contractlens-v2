"""Django HTTP requests and response validation; no Streamlit dependency."""

import requests

from .settings import API_BASE_URL


def api_request(method, path, **kwargs):
    response = requests.request(
        method,
        f"{API_BASE_URL}/api/{path}",
        timeout=(10, 300),
        **kwargs,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Invalid response format.")
    return data


def post_api(path, **kwargs):
    return api_request("POST", path, **kwargs)


def require_id(data):
    value = data.get("id")
    if not isinstance(value, str) or not value:
        raise ValueError("Missing resource ID.")
    return value


def parse_message(data):
    message_id = require_id(data)
    content = data.get("content")
    if str(data.get("role", "")).lower() != "assistant" or not isinstance(content, str) or not content.strip():
        raise ValueError("Invalid assistant message.")
    liked = data.get("liked")
    if liked is not None and not isinstance(liked, bool):
        raise ValueError("Invalid feedback value.")
    return {
        "id": message_id,
        "role": "assistant",
        "content": content,
        "liked": liked,
        "sources": data.get("sources", []),
        "regenerated_from": data.get("regenerated_from"),
    }


def set_feedback(message_id, liked):
    data = api_request(
        "PATCH",
        f"messages/{message_id}/feedback/",
        json={"liked": liked},
    )
    result = parse_message(data)
    if result["id"] != message_id or result["liked"] is not liked:
        raise ValueError("Unexpected feedback response.")
    return result


def regenerate_message(message_id):
    data = post_api(f"messages/{message_id}/regenerate/", json={})
    result = parse_message(data)
    if result["id"] == message_id:
        raise ValueError("Expected a new message ID.")
    return result

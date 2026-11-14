import json

from django.core.exceptions import RequestDataTooBig
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


MAX_REQUEST_BYTES = 2 * 1024 * 1024
MAX_DOCUMENT_CHARS = 30_000


def error_response(message, status=400):
    return JsonResponse(
        {"error": message},
        status=status,
    )


# Development only: authentication and rate limits are not implemented.
@csrf_exempt
@require_POST
def chat(request):
    if request.content_type != "application/json":
        return error_response(
            "Content-Type must be application/json.",
            status=415,
        )

    try:
        body = request.body
    except RequestDataTooBig:
        return error_response("Request is too large.", status=413)

    if len(body) > MAX_REQUEST_BYTES:
        return error_response("Request is too large.", status=413)

    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return error_response("Invalid JSON.")

    if not isinstance(payload, dict):
        return error_response("Expected a JSON object.")

    language = payload.get("language", "fa")

    if language not in ("fa", "en"):
        return error_response("Unsupported language.")

    messages = payload.get("messages")

    if not isinstance(messages, list):
        return error_response("Messages must be a list.")

    if not 1 <= len(messages) <= 50:
        return error_response("Send between 1 and 50 messages.")

    for message in messages:
        if not isinstance(message, dict):
            return error_response("Invalid message.")

        role = message.get("role")
        content = message.get("content")

        if role not in ("user", "assistant"):
            return error_response("Invalid message role.")

        if (
            not isinstance(content, str)
            or not content.strip()
            or len(content) > 8000
        ):
            return error_response("Invalid message content.")

    if messages[-1]["role"] != "user":
        return error_response(
            "The last message must be from the user."
        )

    document = payload.get("document")

    if not isinstance(document, dict):
        return error_response("A document is required.")

    name = document.get("name")
    text = document.get("text")

    if (
        not isinstance(name, str)
        or not name.strip()
        or len(name) > 255
        or not name.lower().endswith(".pdf")
    ):
        return error_response("Invalid PDF filename.")

    if (
        not isinstance(text, str)
        or not text.strip()
        or len(text) > MAX_DOCUMENT_CHARS
    ):
        return error_response("Invalid document text.")

    user_message = messages[-1]["content"]

    if language == "en":
        reply = (
            "Contract text received by Django ✅\n\n"
            f"File: {name}\n\n"
            f"Your question: {user_message}\n\n"
            "This is a test response. "
            "No language model is connected and "
            "no contract analysis has been performed."
        )
    else:
        reply = (
            "متن قرارداد به Django رسید ✅\n\n"
            f"فایل: {name}\n\n"
            f"سؤال شما: {user_message}\n\n"
            "این پاسخ آزمایشی است. "
            "مدل زبانی هنوز متصل نشده و "
            "تحلیل قرارداد انجام نشده است."
        )

    return JsonResponse(
        {"reply": reply},
        json_dumps_params={"ensure_ascii": False},
    )

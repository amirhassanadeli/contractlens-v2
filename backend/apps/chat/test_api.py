import json

from django.test import TestCase


class ChatAPITests(TestCase):
    endpoint = "/api/chat/"

    def make_payload(self, language="fa"):
        return {
            "language": language,
            "messages": [
                {
                    "role": "user",
                    "content": "What are the termination terms?",
                }
            ],
            "document": {
                "name": "employment.pdf",
                "text": (
                    "Either party may terminate this agreement "
                    "with thirty days of written notice."
                ),
            },
        }

    def post_json(self, payload):
        return self.client.post(
            self.endpoint,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_persian_response(self):
        response = self.post_json(self.make_payload("fa"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "متن قرارداد به Django رسید",
            response.json()["reply"],
        )

    def test_english_response(self):
        response = self.post_json(self.make_payload("en"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Contract text received by Django",
            response.json()["reply"],
        )

    def test_document_is_required(self):
        payload = self.make_payload()
        del payload["document"]

        response = self.post_json(payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "A document is required.",
        )

    def test_empty_document_text_is_rejected(self):
        payload = self.make_payload()
        payload["document"]["text"] = "   "

        response = self.post_json(payload)

        self.assertEqual(response.status_code, 400)

    def test_unsupported_language_is_rejected(self):
        payload = self.make_payload("de")

        response = self.post_json(payload)

        self.assertEqual(response.status_code, 400)

    def test_last_message_must_be_from_user(self):
        payload = self.make_payload()
        payload["messages"][-1]["role"] = "assistant"

        response = self.post_json(payload)

        self.assertEqual(response.status_code, 400)

    def test_invalid_json_is_rejected(self):
        response = self.client.post(
            self.endpoint,
            data="{invalid-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_non_json_content_type_is_rejected(self):
        response = self.client.post(
            self.endpoint,
            data="hello",
            content_type="text/plain",
        )

        self.assertEqual(response.status_code, 415)

    def test_get_is_not_allowed(self):
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, 405)

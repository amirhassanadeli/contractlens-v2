from unittest.mock import patch

from django.http import Http404
from rest_framework import status

from .. import views
from .base import BaseAPITestCase


class ContractChatTests(BaseAPITestCase):
    def test_chat_returns_rag_result(self):
        request = self.factory.post(
            f"/contracts/{self.contract_id}/chat/",
            {"question": "مدت قرارداد چقدر است؟"},
            format="json",
        )
        expected = {
            "answer": "یک سال",
            "sources": [],
        }

        with (
            patch.object(
                views.ContractViewSet,
                "get_object",
                return_value=self.contract,
            ),
            patch.object(
                views.RAGService,
                "ask",
                return_value=expected,
            ) as ask,
        ):
            response = self.call_view(
                views.ContractViewSet,
                "chat",
                request,
                pk=str(self.contract_id),
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
        ask.assert_called_once_with(
            contract_id=str(self.contract_id),
            question="مدت قرارداد چقدر است؟",
        )

    def test_chat_rejects_invalid_question(self):
        invalid_payloads = [
            {},
            {"question": ""},
            {"question": "x" * 256},
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                request = self.factory.post(
                    f"/contracts/{self.contract_id}/chat/",
                    payload,
                    format="json",
                )

                with patch.object(views.RAGService, "ask") as ask:
                    response = self.call_view(
                        views.ContractViewSet,
                        "chat",
                        request,
                        pk=str(self.contract_id),
                    )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn("question", response.data)
                ask.assert_not_called()

    def test_chat_returns_404_when_contract_does_not_exist(self):
        request = self.factory.post(
            f"/contracts/{self.contract_id}/chat/",
            {"question": "مدت قرارداد؟"},
            format="json",
        )

        with (
            patch.object(
                views.ContractViewSet,
                "get_object",
                side_effect=Http404,
            ),
            patch.object(views.RAGService, "ask") as ask,
        ):
            response = self.call_view(
                views.ContractViewSet,
                "chat",
                request,
                pk=str(self.contract_id),
            )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        ask.assert_not_called()

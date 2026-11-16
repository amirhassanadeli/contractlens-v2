from unittest.mock import patch

from rest_framework import status

from .. import views
from .base import BaseAPITestCase


class ConversationTests(BaseAPITestCase):
    def test_list_requires_contract_id(self):
        request = self.factory.get("/conversations/")

        with patch.object(views.ConversationService, "list") as service:
            response = self.call_view(
                views.ConversationViewSet,
                "list",
                request,
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "contract_id is required.",
        )
        service.assert_not_called()

    def test_list_returns_contract_conversations(self):
        request = self.factory.get(
            "/conversations/",
            {"contract_id": str(self.contract_id)},
        )

        with (
            patch.object(
                views,
                "get_object_or_404",
                return_value=self.contract,
            ) as lookup,
            patch.object(
                views.ConversationService,
                "list",
                return_value=[self.conversation],
            ) as service,
        ):
            response = self.call_view(
                views.ConversationViewSet,
                "list",
                request,
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            str(response.data[0]["id"]),
            str(self.conversation_id),
        )
        lookup.assert_called_once_with(
            views.Contract,
            id=str(self.contract_id),
        )
        service.assert_called_once_with(self.contract)

    def test_create_conversation(self):
        request = self.factory.post(
            "/conversations/",
            {
                "contract_id": str(self.contract_id),
                "title": "Test conversation",
            },
            format="json",
        )

        with (
            patch.object(
                views,
                "get_object_or_404",
                return_value=self.contract,
            ) as lookup,
            patch.object(
                views.ConversationService,
                "create",
                return_value=self.conversation,
            ) as service,
        ):
            response = self.call_view(
                views.ConversationViewSet,
                "create",
                request,
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Test conversation")

        # UUIDField مقدار رشته‌ای را به UUID تبدیل می‌کند.
        lookup.assert_called_once_with(
            views.Contract,
            id=self.contract_id,
        )
        service.assert_called_once_with(
            contract=self.contract,
            title="Test conversation",
        )

    def test_create_without_title_uses_empty_string(self):
        request = self.factory.post(
            "/conversations/",
            {"contract_id": str(self.contract_id)},
            format="json",
        )

        with (
            patch.object(
                views,
                "get_object_or_404",
                return_value=self.contract,
            ),
            patch.object(
                views.ConversationService,
                "create",
                return_value=self.conversation,
            ) as service,
        ):
            response = self.call_view(
                views.ConversationViewSet,
                "create",
                request,
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        service.assert_called_once_with(
            contract=self.contract,
            title="",
        )

    def test_create_rejects_missing_or_invalid_contract_id(self):
        for payload in [{}, {"contract_id": "invalid-uuid"}]:
            with self.subTest(payload=payload):
                request = self.factory.post(
                    "/conversations/",
                    payload,
                    format="json",
                )

                with patch.object(
                        views.ConversationService,
                        "create",
                ) as service:
                    response = self.call_view(
                        views.ConversationViewSet,
                        "create",
                        request,
                    )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn("contract_id", response.data)
                service.assert_not_called()

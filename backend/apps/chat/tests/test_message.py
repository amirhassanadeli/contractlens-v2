from unittest.mock import patch

from django.http import Http404
from rest_framework import status

from .. import views
from .base import BaseAPITestCase


class MessageTests(BaseAPITestCase):
    def test_list_returns_history(self):
        request = self.factory.get(
            f"/conversations/{self.conversation_id}/messages/",
        )

        with (
            patch.object(
                views,
                "get_object_or_404",
                return_value=self.conversation,
            ) as lookup,
            patch.object(
                views.MessageService,
                "history",
                return_value=[self.message],
            ) as service,
        ):
            response = self.call_view(
                views.MessageViewSet,
                "list",
                request,
                conversation_pk=self.conversation_id,
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], "Test response")
        lookup.assert_called_once_with(
            views.Conversation,
            id=self.conversation_id,
        )
        service.assert_called_once_with(self.conversation)

    def test_send_message(self):
        request = self.factory.post(
            f"/conversations/{self.conversation_id}/messages/",
            {"content": "سلام"},
            format="json",
        )

        with (
            patch.object(
                views,
                "get_object_or_404",
                return_value=self.conversation,
            ),
            patch.object(
                views.MessageService,
                "send_message",
                return_value=self.message,
            ) as service,
        ):
            response = self.call_view(
                views.MessageViewSet,
                "create",
                request,
                conversation_pk=self.conversation_id,
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "Test response")
        service.assert_called_once_with(
            conversation=self.conversation,
            content="سلام",
        )

    def test_send_rejects_missing_or_blank_content(self):
        for payload in [{}, {"content": ""}, {"content": "   "}]:
            with self.subTest(payload=payload):
                request = self.factory.post(
                    f"/conversations/{self.conversation_id}/messages/",
                    payload,
                    format="json",
                )

                with patch.object(
                        views.MessageService,
                        "send_message",
                ) as service:
                    response = self.call_view(
                        views.MessageViewSet,
                        "create",
                        request,
                        conversation_pk=self.conversation_id,
                    )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn("content", response.data)
                service.assert_not_called()

    def test_history_returns_404_for_missing_conversation(self):
        request = self.factory.get(
            f"/conversations/{self.conversation_id}/messages/",
        )

        with (
            patch.object(
                views,
                "get_object_or_404",
                side_effect=Http404,
            ),
            patch.object(views.MessageService, "history") as service,
        ):
            response = self.call_view(
                views.MessageViewSet,
                "list",
                request,
                conversation_pk=self.conversation_id,
            )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        service.assert_not_called()

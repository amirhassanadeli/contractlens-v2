from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.http import Http404
from rest_framework import status

from .. import views
from .base import BaseAPITestCase


class MessageActionTests(BaseAPITestCase):
    def test_like_and_dislike(self):
        for liked in [True, False]:
            with self.subTest(liked=liked):
                self.message.liked = liked

                request = self.factory.patch(
                    f"/messages/{self.message_id}/feedback/",
                    {"liked": liked},
                    format="json",
                )

                with (
                    patch.object(
                        views,
                        "get_object_or_404",
                        return_value=self.message,
                    ) as lookup,
                    patch.object(
                        views.MessageFeedbackService,
                        "set_feedback",
                        return_value=self.message,
                    ) as service,
                ):
                    response = self.call_view(
                        views.MessageActionViewSet,
                        "partial_update",
                        request,
                        pk=self.message_id,
                    )

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["liked"], liked)
                lookup.assert_called_once_with(
                    views.Message,
                    id=self.message_id,
                )
                service.assert_called_once_with(
                    message=self.message,
                    liked=liked,
                )

    def test_feedback_rejects_invalid_input(self):
        invalid_payloads = [
            {},
            {"liked": None},
            {"liked": "invalid"},
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                request = self.factory.patch(
                    f"/messages/{self.message_id}/feedback/",
                    payload,
                    format="json",
                )

                with patch.object(
                        views.MessageFeedbackService,
                        "set_feedback",
                ) as service:
                    response = self.call_view(
                        views.MessageActionViewSet,
                        "partial_update",
                        request,
                        pk=self.message_id,
                    )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn("liked", response.data)
                service.assert_not_called()

    def test_regenerate_message(self):
        regenerated_id = uuid4()
        regenerated = SimpleNamespace(
            id=regenerated_id,
            pk=regenerated_id,
            role="assistant",
            content="Regenerated response",
            sources=[],
            liked=None,
            regenerated_from=self.message,
            created_at=self.now,
        )

        request = self.factory.post(
            f"/messages/{self.message_id}/regenerate/",
            {},
            format="json",
        )

        with (
            patch.object(
                views,
                "get_object_or_404",
                return_value=self.message,
            ),
            patch.object(
                views.MessageRegenerateService,
                "regenerate",
                return_value=regenerated,
            ) as service,
        ):
            response = self.call_view(
                views.MessageActionViewSet,
                "regenerate",
                request,
                pk=self.message_id,
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "Regenerated response")
        self.assertEqual(
            str(response.data["id"]),
            str(regenerated_id),
        )
        self.assertEqual(
            str(response.data["regenerated_from"]),
            str(self.message_id),
        )
        service.assert_called_once_with(self.message)

    def test_regenerate_returns_404_for_missing_message(self):
        request = self.factory.post(
            f"/messages/{self.message_id}/regenerate/",
            {},
            format="json",
        )

        with (
            patch.object(
                views,
                "get_object_or_404",
                side_effect=Http404,
            ),
            patch.object(
                views.MessageRegenerateService,
                "regenerate",
            ) as service,
        ):
            response = self.call_view(
                views.MessageActionViewSet,
                "regenerate",
                request,
                pk=self.message_id,
            )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        service.assert_not_called()

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory


class BaseAPITestCase(SimpleTestCase):
    def setUp(self):
        super().setUp()

        self.factory = APIRequestFactory()
        self.now = datetime.now(timezone.utc)

        self.contract_id = uuid4()
        self.conversation_id = uuid4()
        self.message_id = uuid4()

        self.contract = SimpleNamespace(
            id=self.contract_id,
            pk=self.contract_id,
            title="Test contract",
            language="fa",
            status="ready",
            created_at=self.now,
        )

        self.conversation = SimpleNamespace(
            id=self.conversation_id,
            pk=self.conversation_id,
            title="Test conversation",
            created_at=self.now,
            updated_at=self.now,
        )

        self.message = SimpleNamespace(
            id=self.message_id,
            pk=self.message_id,
            role="assistant",
            content="Test response",
            sources=[],
            liked=None,
            regenerated_from=None,
            created_at=self.now,
        )

    def call_view(self, viewset, action, request, **kwargs):
        view = viewset.as_view(
            {request.method.lower(): action},
            authentication_classes=[],
            permission_classes=[],
            throttle_classes=[],
        )

        return view(request, **kwargs)

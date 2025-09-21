from django.test import TestCase


class DummySerializer:
    pass


class AnotherSerializer:
    pass


class AllowPermission:
    pass


class DenyPermission:
    pass


class DummyViewSet:
    serializer_class = DummySerializer
    action_serializers = {"custom": AnotherSerializer}
    permission_classes = [AllowPermission]
    action_permissions = {"custom": [AllowPermission, DenyPermission]}

    def get_serializer_class(self):
        return self.action_serializers.get(
            getattr(self, "action", None), self.serializer_class
        )

    def get_permissions(self):
        perms = getattr(self, "action_permissions", {}).get(
            getattr(self, "action", None)
        )
        if perms is not None:
            return [perm() for perm in perms]

        return [perm() for perm in getattr(self, "permission_classes", [])]


class BaseViewSetMethodMixinTestCase(TestCase):
    """Tests action-based serializer and permission behavior in DummyViewSet."""

    def test_get_serializer_class(self):
        """Returns correct serializer class based on action."""
        view = DummyViewSet()

        view.action = "list"
        self.assertIs(view.get_serializer_class(), DummySerializer)

        view.action = "custom"
        self.assertIs(view.get_serializer_class(), AnotherSerializer)

    def test_get_permissions(self):
        """Returns correct permissions list based on action."""
        view = DummyViewSet()

        view.action = "custom"
        perms = view.get_permissions()
        self.assertEqual(len(perms), 2)
        self.assertIsInstance(perms[0], AllowPermission)
        self.assertIsInstance(perms[1], DenyPermission)

        view.action = "list"
        perms = view.get_permissions()
        self.assertEqual(len(perms), 1)
        self.assertIsInstance(perms[0], AllowPermission)

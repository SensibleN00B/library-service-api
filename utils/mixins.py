class BaseViewSetMethodMixin:
    """Mixin for mapping actions with serializers and permissions"""

    def get_serializer_class(self):
        if (
            hasattr(self, "action_serializers")
            and self.action in self.action_serializers
        ):
            return self.action_serializers[self.action]

        return super().get_serializer_class()

    def get_permissions(self):
        if (
            hasattr(self, "action_permissions")
            and self.action in self.action_permissions
        ):
            return [perm() for perm in self.action_permissions[self.action]]
        return super().get_permissions()

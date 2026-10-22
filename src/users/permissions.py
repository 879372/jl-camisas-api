from rest_framework.permissions import BasePermission


class ProfileActionPermission(BasePermission):
    """Authorize viewset actions using the user's business profile."""

    message = 'Seu perfil não possui permissão para executar esta ação.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or getattr(user, 'profile', None) == 'admin':
            return True

        profile_actions = getattr(view, 'profile_actions', {})
        allowed_actions = profile_actions.get(getattr(user, 'profile', None), ())
        return '*' in allowed_actions or getattr(view, 'action', None) in allowed_actions

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from accounts.models import RoleChoices
from .models import Ticket

class RoleRequiredMixin(UserPassesTestMixin):
    """
    Mixin for requiring user to have one of the allowed roles.
    """

    allowed_roles = None

    def test_func(self):
        user = self.request.user

        if self.allowed_roles is None:
            return False

        if not user.is_authenticated:
            return False

        return user.role in self.allowed_roles

class TicketAccessMixin(UserPassesTestMixin):

    def test_func(self):
        user = self.request.user
        ticket_id = self.kwargs.get('pk')
        ticket = get_object_or_404(Ticket, pk=ticket_id)

        if user.role == RoleChoices.ADMIN:
            return True

        if ticket.created_by == user:
            return True

        if user.role == RoleChoices.SUPPORT and ticket.assigned_to == user:
            return True

        return False

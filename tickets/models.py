import os
from django.utils import timezone
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


def ticket_message_attachment_path(instance, filename):
    """
    ticket_attachments/ticket_123/2025-04-05_14-30-59_filename.jpg
    """
    ext = filename.split('.')[-1]
    if not ext:
        ext = 'bin'

    timestamp = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')

    ticket_id = instance.ticket.id if instance.ticket.id else 'tmp'
    filename = f"{timestamp}_{filename}"
    # ساخت مسیر نهایی
    return os.path.join('ticket_attachments', f'ticket_{ticket_id}', filename)


class TicketPriorityChoices(models.TextChoices):
    LOW = 'low', 'Low'
    NORMAL = 'normal', 'Normal'
    HIGH = 'high', 'High'

class TicketStatusChoices(models.TextChoices):
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in_progress', 'In Progress'
    PENDING_CLOSE = 'pending_close', 'Pending Close'
    CLOSED = 'closed', 'Closed'

class Ticket(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField()

    priority = models.CharField(max_length=10,
                                choices=TicketPriorityChoices.choices,
                                default=TicketPriorityChoices.NORMAL)
    status = models.CharField(max_length=20,
                              choices=TicketStatusChoices.choices,
                              default=TicketStatusChoices.OPEN)

    created_by = models.ForeignKey(User, related_name="tickets_created",
                                   on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name="tickets_assigned",
                                    on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def get_ticket_info(self):
        return (f"Ticket {self.title} with status ({self.get_status_display()})"
                f" created by {self.created_by} and assigned to {self.assigned_to} ")


class TicketMessage(models.Model):

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    ticket = models.ForeignKey(Ticket, related_name="ticket_messages",
                               on_delete=models.CASCADE)

    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to=ticket_message_attachment_path,
                                      blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def children(self):
        return self.replies.all()

    def is_parent(self):
        return self.parent is None

    def __str__(self):
        return f"Message by {self.sender} on {self.ticket}"


class CloseRequest(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE,
                                  related_name="close_request")
    # only support user
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Close request by {self.requested_by.get_full_name()} on {self.ticket}"



class StatusLog(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE,
                                  related_name="status_logs")
    # only support user
    old_status = models.CharField(max_length=20,
                              choices=TicketStatusChoices.choices)
    new_status = models.CharField(max_length=20,
                              choices=TicketStatusChoices.choices)

    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Changed status of {self.ticket} from {self.old_status} to {self.new_status}"


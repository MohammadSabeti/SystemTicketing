from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import CreateView, ListView, DetailView,UpdateView,DeleteView
from django.shortcuts import render
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404,redirect
from accounts.models import RoleChoices, UserProfile
from .forms import MessageForm
from .models import *
from .mixins import RoleRequiredMixin,TicketAccessMixin
from django.contrib import messages
from django.db.models import Case, When, IntegerField
# Create your views here.

class TicketListView(RoleRequiredMixin, ListView):
    model = Ticket
    template_name = "tickets/ticket_list.html"
    context_object_name = "tickets"
    ordering = ["-created_at"]
    allowed_roles=[RoleChoices.ADMIN,RoleChoices.SUPPORT,RoleChoices.USER]

    def get_queryset(self):
        user=self.request.user
        queryset=Ticket.objects.all()


        # Filter by Role
        if self.request.user.role == RoleChoices.SUPPORT:
            queryset=queryset.filter(assigned_to=user)
        elif self.request.user.role == RoleChoices.USER:
            queryset = queryset.filter(created_by=user)

        # Filter by Status
        status=self.request.GET.get("status")
        if status:
            queryset=queryset.filter(status=status)

        # Filter by Priority
        priority=self.request.GET.get("priority")
        if priority:
            queryset=queryset.filter(priority=priority)

        # Filter by Sort
        sort=self.request.GET.get("sort",'-created_at')

        # Creating a virtual column for priority sorting
        queryset=queryset.annotate(
            priority_order=Case(
                When(priority=TicketPriorityChoices.LOW, then=0),
                When(priority=TicketPriorityChoices.NORMAL, then=1),
                When(priority=TicketPriorityChoices.HIGH, then=2),
                default=1,
                output_field=IntegerField()
            )
        )

        if sort == "priority":
            queryset = queryset.order_by("priority_order")

        return queryset

class TicketCreateView(RoleRequiredMixin, CreateView):
    model = Ticket
    template_name = "tickets/ticket_form.html"
    fields = ['title', 'description', 'priority']
    allowed_roles = [RoleChoices.ADMIN, RoleChoices.USER]
    context_object_name = "ticket"
    success_url = reverse_lazy("tickets:ticket_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = TicketStatusChoices.OPEN
        messages.success(self.request, "تیکت با موفقیت ایجاد شد.")
        return super().form_valid(form)

class TicketUpdateView(TicketAccessMixin, UpdateView):
    model =Ticket
    template_name = "tickets/ticket_form.html"
    fields = ['title', 'description', 'priority']
    context_object_name = "ticket"
    # extra_context='update'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = True
        return context

    def get_success_url(self):
        return reverse_lazy("tickets:ticket_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "تیکت با موفقیت ویرایش شد.")
        return super().form_valid(form)

class TicketDetailView(TicketAccessMixin, FormMixin, DetailView):
    model=Ticket
    template_name = "tickets/ticket_detail.html"
    form_class = MessageForm
    context_object_name = "ticket"

    def get_success_url(self):
        return reverse_lazy("tickets:ticket_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['ticket_messages']=self.object.ticket_messages.order_by('created_at')
        context['status_logs']=self.object.status_logs.order_by('created_at')
        context['support_users']=UserProfile.objects.filter(role=RoleChoices.SUPPORT)
        context['form']=self.get_form()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form=self.get_form()
        if form.is_valid():
            msg=form.save(commit=False)
            msg.ticket=self.object
            msg.sender=request.user
            msg.save()
            messages.success(request, "پیام شما با موفقیت ثبت شد.")
            return self.form_valid(form)
        else:
            messages.error(request, "متأسفانه ثبت پیام با خطا مواجه شد.")
            return self.form_invalid(form)

class TicketDeleteView(TicketAccessMixin, DeleteView):
    model=Ticket
    template_name = "tickets/ticket_list.html"
    success_url = reverse_lazy("tickets:ticket_list")
    allowed_roles = [RoleChoices.ADMIN,RoleChoices.USER]


    def form_valid(self, form):
        messages.success(self.request, "تیکت با موفقیت حذف شد.")
        print("تیکت با موفقیت حذف شد.")
        return super().form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, "شما اجازه حذف این تیکت را ندارید.")
        return redirect("tickets:ticket_list")

class RequestCloseView(RoleRequiredMixin, View):
    required_role = [RoleChoices.USER]

    def post(self,request,pk):
        ticket=get_object_or_404(Ticket, pk=pk)

        if hasattr(ticket,'close_request'):
            messages.info(request, "درخواست بستن این تیکت قبلاً ثبت شده است.")
            return redirect("tickets:ticket_detail", pk=pk)

        CloseRequest.objects.create(
            ticket=ticket,
            requested_by=request.user
        )
        StatusLog.objects.create(
            ticket=ticket,
            old_status=ticket.status,
            new_status=TicketStatusChoices.PENDING_CLOSE,
            changed_by=request.user
        )
        ticket.status=TicketStatusChoices.PENDING_CLOSE
        ticket.save()
        messages.success(request, "درخواست بستن تیکت با موفقیت ثبت شد.")
        return redirect("tickets:ticket_detail", pk=pk)

class ApproveCloseRequestView(RoleRequiredMixin, View):
    required_role = [RoleChoices.ADMIN]

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)

        if not hasattr(ticket, "close_request"):
            messages.error(request, "درخواستی برای بستن این تیکت وجود ندارد.")
            return redirect("tickets:ticket_detail", pk=pk)

        StatusLog.objects.create(
            ticket=ticket,
            old_status=ticket.status,
            new_status=TicketStatusChoices.CLOSED,
            changed_by=request.user
        )

        ticket.status = TicketStatusChoices.CLOSED
        ticket.save()

        ticket.close_request.approved = True
        ticket.close_request.save()
        messages.success(request, "تیکت با موفقیت بسته شد.")
        return redirect("tickets:ticket_detail", pk=pk)


class AssignTicketView(RoleRequiredMixin,View):
    required_role = [RoleChoices.ADMIN]

    def post(self,request,pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        support_user_id = request.POST.get("assigned_to")
        ticket.assigned_to=UserProfile.objects.get(pk=support_user_id)
        StatusLog.objects.create(
            ticket=ticket,
            old_status=ticket.status,
            new_status=TicketStatusChoices.IN_PROGRESS,
            changed_by=request.user
        )
        ticket.status = TicketStatusChoices.IN_PROGRESS
        ticket.save()
        messages.success(request, "تیکت با موفقیت به پشتیبان مورد نظر ارجاع داده شد.")
        return redirect("tickets:ticket_detail", pk=pk)



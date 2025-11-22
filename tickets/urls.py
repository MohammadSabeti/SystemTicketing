# from django.contrib import admin
from django.urls import path
from .views import *

app_name = 'tickets'
urlpatterns = [
    path("", TicketListView.as_view(), name="ticket_list"),
    path("ticket/create/", TicketCreateView.as_view(), name="ticket_form"),


    path("ticket/<int:pk>/", TicketDetailView.as_view(), name="ticket_detail"),
    path("ticket/<int:pk>/update/", TicketUpdateView.as_view(), name="ticket_edit"),
    path("ticket/<int:pk>/delete/", TicketDeleteView.as_view(), name="ticket_delete"),


    path("ticket/<int:pk>/close/", RequestCloseView.as_view(), name="close_request"),
    path("ticket/<int:pk>/approve-close/", ApproveCloseRequestView.as_view(), name="approve_close_request"),
    path("ticket/<int:pk>/assign_support/", AssignTicketView.as_view(), name="assign_support"),
]

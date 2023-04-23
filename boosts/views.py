from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView

import os

from boosts.forms import InspirationalForm
from boosts.models import Inspirational
from config.settings.common import THE_SITE_NAME

INSPIRATIONAL_LIST_PAGE_TITLE = "Inspirationals"
INSPIRATIONAL_CREATE_PAGE_TITLE = "Create an Inspirational"


class InspirationalListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    ListView for the Inspirational model.

    This view is only accessible to users who have `registration_accepted=True`. This is controlled by the `UserPassesTestMixin` and the `test_func` method.
    """

    paginate_by = 3

    def test_func(self):
        """
        Test if user has `registration_accepted=True`. Only users who pass this test can access this view.

        This function is used by the `UserPassesTestMixin` to control access to this view.
        """
        return self.request.user.registration_accepted

    # We are not using 'model = Inspirational' attribute since we want only
    # the `Inspirationals` for the current user.
    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Inspirational.objects.filter(
                author=self.request.user,
            ).order_by("-created")
            return queryset
        else:
            queryset = Inspirational.objects.none()
            return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = INSPIRATIONAL_LIST_PAGE_TITLE
        context["the_site_name"] = THE_SITE_NAME
        return context


class InspirationalCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    CreateView for the Inspirational model.
    """

    form_class = InspirationalForm
    template_name = "boosts/inspirational_form.html"
    success_url = reverse_lazy("boosts:inspirational-list")

    def test_func(self):
        """
        Test if user has `registration_accepted=True`. Only users who pass this test can access this view.

        This function is used by the `UserPassesTestMixin` to control access to this view.
        """
        return self.request.user.registration_accepted

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = INSPIRATIONAL_CREATE_PAGE_TITLE
        context["the_site_name"] = THE_SITE_NAME
        # Hide the "Create Inspirational" link in the navbar since we are already on the page.
        context["hide_inspirational_create_link"] = True
        return context


def send_inspirational(request, pk):
    """
    Print an inspirational quote to the console.
    """
    inspirational = get_object_or_404(Inspirational, pk=pk)
    # Send the inspirational quote to `MY_VALIDATED_EMAIL`:
    send_mail(
        "Inspirational Quote",
        inspirational.body,
        request.user.email,
        [os.getenv("MY_VALIDATED_EMAIL")],
        fail_silently=False,
    )
    messages.success(request, f"Printed {inspirational.id} to the console.")
    return redirect("boosts:inspirational-list")


# def print_inspirational(request, pk):
#     """
#     Print an inspirational quote.

#     This view is only accessible to users who have `registration_accepted=True`. This is controlled by the `UserPassesTestMixin` and the `test_func` method.
#     """
#     inspirational = get_object_or_404(Inspirational, pk=pk)
#     context = {
#         "inspirational": inspirational,
#         "page_title": f"Print {inspirational}",
#         "the_site_name": THE_SITE_NAME,
#     }
#     return render(request, "boosts/inspirational_print.html", context)

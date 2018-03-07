from django.views.generic import UpdateView, ListView, FormView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from datetime import datetime

from braces.views import StaffuserRequiredMixin, LoginRequiredMixin

from aliss.forms import ClaimUpdateForm, ClaimForm
from aliss.models import Claim, Organisation


class ClaimListView(StaffuserRequiredMixin, ListView):
    model = Claim
    template_name = 'claim/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ClaimListView, self).get_context_data(**kwargs)
        context['unreviewed_count'] = Claim.objects.filter(status=Claim.UNREVIEWED).count()
        context['confirmed_count'] = Claim.objects.filter(status=Claim.CONFIRMED).count()
        context['denied_count'] = Claim.objects.filter(status=Claim.DENIED).count()
        context['revoked_count'] = Claim.objects.filter(status=Claim.REVOKED).count()
        return context

    def get_queryset(self):
        queryset = super(ClaimListView, self).get_queryset()

        if self.request.GET.get('status', None) and int(self.request.GET.get('status', None)) in [Claim.UNREVIEWED, Claim.CONFIRMED, Claim.DENIED, Claim.REVOKED]:
            queryset = queryset.filter(status=self.request.GET['status'])
        else:
            queryset = queryset.filter(status=Claim.UNREVIEWED)

        return queryset


class ClaimDetailView(StaffuserRequiredMixin, UpdateView):
    model = Claim
    template_name = 'claim/detail.html'
    form_class = ClaimUpdateForm
    success_url = reverse_lazy('claim_list')

    def send_user_email(self, claim):
        if claim.status == Claim.CONFIRMED:
            message = 'Congratulations, your claim of ownership for {organisation} on ALISS has been confirmed.'.format(organisation=claim.organisation)
        elif claim.status == Claim.REVOKED:
            message = 'We are sorry, but your claim of ownership for {organisation} on ALISS has been revoked.'.format(
                organisation=claim.organisation
            )
        elif claim.status == Claim.DENIED:
            message = 'We are sorry, but your claim of ownership for {organisation} on ALISS has been denied.'.format(
                organisation=claim.organisation
            )
        else:
            return False

        send_mail(
            'Your ownership claim of {organisation} on ALISS'.format(
                organisation=claim.organisation
            ),
            message,
            settings.DEFAULT_FROM_EMAIL,
            [claim.user.email],
            fail_silently=True,
        )


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.reviewed_on = datetime.now()
        self.object.reviewed_by = self.request.user

        if self.object.status == Claim.CONFIRMED:
            self.object.organisation.claimed_by = self.object.user
            self.object.organisation.save()
        elif self.object.status == Claim.REVOKED:
            self.object.organisation.claimed_by = None
            self.object.organisation.save()

        self.object.save()

        self.send_user_email(self.object)

        return HttpResponseRedirect(self.get_success_url())


class ClaimCreateView(LoginRequiredMixin, FormView):
    form_class = ClaimForm
    template_name = 'claim/create.html'
    success_url = reverse_lazy('claim_thanks')

    def form_valid(self, form):
        organisation = get_object_or_404(Organisation, pk=self.kwargs.get('pk'))

        Claim.objects.create(
            user=self.request.user,
            organisation=organisation,
            email=form.cleaned_data.get('email'),
            phone=form.cleaned_data.get('phone'),
            comment=form.cleaned_data.get('comment'),
            created_by=self.request.user
        )

        return HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        organisation = get_object_or_404(Organisation, pk=self.kwargs.get('pk'))
        return self.render_to_response(
            self.get_context_data(organisation=organisation)
        )

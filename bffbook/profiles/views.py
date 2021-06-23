from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Relationship
from .forms import ProfileModelForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required()
def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileModelForm(request.POST or None, request.FILES or None, instance=profile)
    template_name="profiles/myprofile.html"
    confirm = False

    if request.method=="POST":
        if form.is_valid():
            form.save()
            confirm = True

    context={
        'profile': profile,
        'form': form,
        'confirm': confirm,
    }

    return render(request, template_name, context)

@login_required()
def invites_received_view(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invitaions_received(receiver=profile)

    template_name = "profiles/my_invites.html"

    results = list(map(lambda x: x.sender, qs))
    is_empty = False
    if len(results) == 0:
        is_empty = True

    context = {
        'qs': results,
        'is_empty': is_empty,
    }

    return render(request, template_name, context)

@login_required()
def accept_invitation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()
    return redirect('profiles:my-invites-view')

@login_required()
def reject_invitation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        receiver = Profile.objects.get(user=request.user)
        sender = Profile.objects.get(pk=pk)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('profiles:my-invites-view')


@login_required()
def invite_profiles_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)
    profile = Profile.objects.get(user=user)
    rel_receiver_profiles = Relationship.objects.filter(sender=profile)
    rel_sender_profiles = Relationship.objects.filter(receiver=profile)
    rel_receiver = []
    rel_sender = []
    for item in rel_receiver_profiles:
        rel_receiver.append(item.receiver.user)
    for item in rel_sender_profiles:
        rel_sender.append(item.sender.user)
    is_empty = False
    if len(qs) == 0:
        is_empty = True
    template_name = 'profiles/to_invite_list.html'

    context = {'qs': qs,
        'is_empty': is_empty,
        'rel_receiver': rel_receiver,
        'rel_sender': rel_sender
    }

    return render(request, template_name, context)


@login_required()
def my_friends_list(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    friends_users = profile.get_friends()
    qs=[]
    for f in friends_users:
        profile = Profile.objects.get(user=f)
        qs.append(profile)
    is_empty = False
    if len(qs) == 0:
        is_empty = True
    template_name = 'profiles/my_friends.html'

    context = {'qs': qs,
        'is_empty': is_empty
    }

    return render(request, template_name, context)

@login_required()
def profiles_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles(user)

    template_name = 'profiles/profile_list.html'

    context = {'qs': qs}

    return render(request, template_name, context)



class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/detail.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        rel_receiver_profiles = Relationship.objects.filter(sender=profile)
        rel_sender_profiles = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_receiver_profiles:
            rel_receiver.append(item.receiver.user)
        for item in rel_sender_profiles:
            rel_sender.append(item.sender.user)
        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['posts'] = self.get_object().get_all_authors_posts()
        context['len_posts'] = True if len(self.get_object().get_all_authors_posts()) > 0 else False
        return context


class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    context_object_name = "profiles"

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        rel_receiver_profiles = Relationship.objects.filter(sender=profile)
        rel_sender_profiles = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_receiver_profiles:
            rel_receiver.append(item.receiver.user)
        for item in rel_sender_profiles:
            rel_sender.append(item.sender.user)
        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['profiles'] =  context['profiles'].filter(
                (Q(first_name = search_input)) | (Q(last_name = search_input)) | (Q(email = search_input))
            )


        

        return context

@login_required()
def send_invitation(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')

@login_required()
def remove_from_friends(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender))
        )
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')

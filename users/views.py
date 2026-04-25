from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserSignUpForm, ProfileUpdateForm, LifestylePreferenceForm
from .models import LifestylePreference, PreferenceTag
from househelp.models import Househelp
from househelp.forms import HousehelpProfileForm


@login_required
def edit_profile(request):
    user = request.user
    profile_instance = None
    profile_form_class = None

    if user.role == 'HOUSE_HELP':
        profile_instance = getattr(user, 'househelp', None)
        profile_form_class = HousehelpProfileForm
    elif user.role == 'ROOMMATE':
        profile_instance = getattr(user, 'lifestyle_preference', None)
        profile_form_class = LifestylePreferenceForm

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        profile_form = None
        if profile_form_class:
            profile_form = profile_form_class(request.POST, instance=profile_instance)

        if form.is_valid() and (not profile_form or profile_form.is_valid()):
            form.save()
            if profile_form:
                profile_form.save()
            return redirect('dashboard')
    else:
        form = ProfileUpdateForm(instance=user)
        profile_form = None
        if profile_form_class:
            profile_form = profile_form_class(instance=profile_instance)

    return render(request, 'edit_profile.html', {
        'form': form,
        'profile_form': profile_form
    })


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user

    context = {
        'user': user,
    }

    if user.role == 'ROOMMATE':
        context['profile'] = LifestylePreference.objects.filter(user=user).first()
        from apartments.models import ResidentRecord

        # Fetch active residencies to show linked apartments
        residencies = ResidentRecord.objects.filter(resident=user, is_active=True).select_related('apartment')
        context['residencies'] = residencies

        # Roommate Dashboard Reviews Feature: Gather co-residents and owners
        co_residents = set()
        owners = set()
        for r in residencies:
            apartment = r.apartment
            if apartment.owner:
                owners.add(apartment.owner)

            # Fetch other residents in the same apartment
            other_residents = ResidentRecord.objects.filter(apartment=apartment, is_active=True).exclude(
                resident=user).select_related('resident')
            for other in other_residents:
                co_residents.add(other.resident)

        context['co_residents'] = list(co_residents)
        context['owners'] = list(owners)

        return render(request, 'dashboards/roommate.html', context)
    elif user.role == 'HOUSE_OWNER':
        # Fetch owned apartments
        from apartments.models import Apartment
        from apartments.models import ResidentRecord
        context['owned_apartments'] = Apartment.objects.filter(owner=user)
        return render(request, 'dashboards/owner.html', context)
    elif user.role == 'HOUSE_HELP':
        context['profile'] = Househelp.objects.filter(user=user).first()
        return render(request, 'dashboards/househelp.html', context)


    return redirect('landing')

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Create the User object
            user = form.save()

            # 2. Extract and handle role-specific data
            role = user.role

            if role == 'ROOMMATE':
                # Create Lifestyle Profile and link tags
                profile = LifestylePreference.objects.create(user=user)
                selected_preferences = form.cleaned_data.get('preferences')
                if selected_preferences:
                    profile.preferences.set(selected_preferences)

            elif role == 'HOUSE_HELP':
                # Create Househelp Profile and link skills
                profile = Househelp.objects.create(user=user)
                selected_skills = form.cleaned_data.get('skills')
                if selected_skills:
                    profile.skills.set(selected_skills)

            # 3. Log the user in and redirect
            login(request, user)
            return redirect('landing')
    else:
        form = UserSignUpForm()

    # Group preferences for categorized display in the template
    grouped_preferences = {}
    for cat_code, cat_name in PreferenceTag.CATEGORY_CHOICES:
        tags = PreferenceTag.objects.filter(category=cat_code)
        if tags.exists():
            grouped_preferences[cat_name] = tags

    return render(request, 'signup.html', {
        'form': form,
        'grouped_preferences': grouped_preferences
    })

def logout_view(request):
    logout(request)
    return redirect('landing')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


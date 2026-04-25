from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ApartmentForm
from .models import ResidentRecord


@login_required
def add_apartment(request):
    if request.method == 'POST':
        if request.user.role == 'ROOMMATE':
            if ResidentRecord.objects.filter(resident=request.user, is_active=True).exists():
                messages.error(request,
                               "You can only have one active apartment at a time. Please remove your current apartment first.")
                return redirect('dashboard')

        # PASSING user=request.user for dynamic labels
        form = ApartmentForm(request.POST, user=request.user)
        if form.is_valid():
            apartment = form.save(commit=False)

            # Logic: If owner is adding, set the owner field.
            if request.user.role == 'HOUSE_OWNER':
                apartment.owner = request.user

            # Save the apartment
            apartment.save()

            # Logic: If roommate is adding, link them as a resident immediately
            if request.user.role == 'ROOMMATE':
                ResidentRecord.objects.create(
                    resident=request.user,
                    apartment=apartment,
                    is_active=True
                )
                messages.success(request, f"Apartment '{apartment.name}' registered! You are now listed as a resident.")
            else:
                messages.success(request, f"Apartment '{apartment.name}' registered successfully.")

            return redirect('dashboard')
    else:
        form = ApartmentForm(user=request.user)

    return render(request, 'apartments/add_apartment.html', {'form': form})


@login_required
def join_apartment(request):
    if request.method == 'POST':
        # Roommates: limit to 1 active apartment. Owners: no limit.
        if request.user.role == 'ROOMMATE':
            if ResidentRecord.objects.filter(resident=request.user, is_active=True).exists():
                messages.error(request,
                               "You can only have one active apartment at a time. Please remove your current apartment first.")
                return redirect('dashboard')

        raw_id = request.POST.get('building_id_input', '').strip()

        # Clean the input: Extract numbers if they typed "LIVO-004"
        clean_id = ''.join(filter(str.isdigit, raw_id))

        if not clean_id:
            messages.error(request, "Please enter a valid Building ID (e.g. LIVO-0004).")
            return redirect('dashboard')

        try:
            from apartments.models import Apartment
            apartment = Apartment.objects.get(id=int(clean_id))

            if request.user.role == 'HOUSE_OWNER':
                # Owners claim the apartment as their property
                if apartment.owner == request.user:
                    messages.warning(request, f"You already own {apartment.name}.")
                    return redirect('dashboard')
                if apartment.owner is not None:
                    messages.error(request, f"{apartment.name} already has an owner registered. You cannot claim it.")
                    return redirect('dashboard')
                apartment.owner = request.user
                apartment.save()
                messages.success(request, f"Success! {apartment.name} has been registered as your property.")
            else:
                # Roommates join as residents
                if ResidentRecord.objects.filter(resident=request.user, apartment=apartment, is_active=True).exists():
                    messages.warning(request, f"You are already registered to {apartment.name}.")
                    return redirect('dashboard')

                if apartment.owner == request.user:
                    messages.warning(request, "You already own this property.")
                    return redirect('dashboard')

                # Update or create the residency record to handle rejoining
                record, created = ResidentRecord.objects.update_or_create(
                    resident=request.user,
                    apartment=apartment,
                    defaults={'is_active': True}
                )

                messages.success(request, f"Success! You have joined {apartment.name}.")

        except Apartment.DoesNotExist:
            messages.error(request, f"No building found with ID '{raw_id}'. Please check with your housemates.")
        except Exception as e:
            messages.error(request, "An error occurred while trying to join the building.")

    return redirect('dashboard')


@login_required
def leave_apartment(request, apartment_id):
    if request.method == 'POST':
        record = ResidentRecord.objects.filter(resident=request.user, apartment_id=apartment_id, is_active=True).first()
        if record:
            record.is_active = False
            record.save()
            messages.success(request, f"You have left the apartment.")
        else:
            messages.error(request, "You are not an active resident of this apartment.")
    return redirect('dashboard')


@login_required
def remove_ownership(request, apartment_id):
    if request.method == 'POST':
        from .models import Apartment
        apartment = Apartment.objects.filter(id=apartment_id, owner=request.user).first()
        if apartment:
            apartment.owner = None
            apartment.save()
            messages.success(request, f"You have removed '{apartment.name}' from your managed properties.")
        else:
            messages.error(request, "You do not own this apartment.")
    return redirect('dashboard')
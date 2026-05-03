from django.db import models
from django.core.exceptions import ValidationError
from users.models import User
from apartments.models import Apartment


# Create your models here.
class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('ROOM', 'Room Listing'),
        ('HELP', 'Househelp Post'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES)
    title = models.CharField(max_length=200)

    # REFACTORED: Support single photo per post
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)

    # NEW: Specific listing price (Price per person for Roommates, Total Rent for Owners, Meal price for Vendors)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Simple counter as requested (No list of users)
    likes = models.IntegerField(default=0)

    # link to a physical apartment if this is a ROOM listing
    apartment = models.ForeignKey(Apartment, on_delete=models.SET_NULL, null=True, blank=True, related_name='listings')

    message_link = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField()
    availability = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        # FIXED: Safeguard against 'RelatedObjectDoesNotExist' during form validation
        try:
            current_user = self.user
        except (User.DoesNotExist, AttributeError):
            # If user isn't assigned yet (common during early form validation), we skip role-based checks
            # The view will handle assigning the user later.
            return

        # 1. Role-based Posting Restrictions
        if self.type == 'ROOM' and current_user.role not in ['ROOMMATE', 'HOUSE_OWNER']:
            raise ValidationError(
                f"Only Roommates and House Owners can create Room Listings. Your role is {current_user.get_role_display()}.")

        if self.type == 'FOOD' and current_user.role != 'VENDOR':
            raise ValidationError(
                f"Only Vendors/Meal Providers can create Food Posts. Your role is {current_user.get_role_display()}.")

        if self.type == 'HELP' and current_user.role != 'HOUSE_HELP':
            raise ValidationError(
                f"Only House Help professionals can create Help Posts. Your role is {current_user.get_role_display()}.")

        # 2. Apartment Link Requirements (STRICTLY FORCED)
        if self.type == 'ROOM' and not self.apartment:
            raise ValidationError(
                "Room Listings MUST be linked to a physical Apartment entity. Please create/select an apartment first.")

        if self.type != 'ROOM' and self.apartment:
            raise ValidationError("Only Room Listings should be linked to an Apartment.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"

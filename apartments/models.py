from django.db import models
from users.models import User


# Create your models here.
class Apartment(models.Model):
    name = models.CharField(max_length=200, help_text="Example: Green Valley Apartment, Unit 4B")
    address = models.TextField()
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100, default="", help_text="e.g. Manhattan, Gulshan, or Downtown")

    # Financials
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total rent for the apartment")

    # physical details
    total_rooms = models.IntegerField(default=1)
    has_wifi = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)

    # Ownership (Optional for Roommates, required for Owners)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_apartments', null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.area}, {self.city})"


class ResidentRecord(models.Model):
    resident = models.ForeignKey(User, on_delete=models.CASCADE, related_name='residencies')
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='residents')
    start_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Resident Record"
        verbose_name_plural = "Resident Records"
        unique_together = ('resident', 'apartment', 'is_active')

    def __str__(self):
        status = "Active" if self.is_active else "Former"
        return f"{self.resident.username} at {self.apartment.name} ({status})"
# Create your models here.

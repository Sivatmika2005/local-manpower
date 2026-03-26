import os
import random
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_booking.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import ServiceProvider, Feedback

User = get_user_model()

DEFAULT_PHONE = "9360522919"
locations = ["Chennai", "Coimbatore", "Madurai", "Salem", "Trichy", "Tirunelveli", "Erode", "Vellore", "Thoothukudi", "Nagercoil"]

sample_providers = {
    'electrician': {
        'names': [
            "Arun Kumar", "Ramesh", "Suresh", "Kumar Swamy", "Venkatesh",
            "Siva Kumar", "Rajesh", "Murugan", "Prakash", "Manickam"
        ],
        'specializations': ["Master Electrician", "Certified Electrician", "Emergency Electrician", "Residential Expert", "Industrial Specialist"]
    },
    'plumber': {
        'names': [
            "Kannan", "Mani", "Selvam", "Dinesh", "Senthil",
            "Vijay", "Anand", "Basker", "Ravi", "Ganesh"
        ],
        'specializations': ["Master Plumber", "Certified Plumber", "Emergency Plumber", "Pipe Specialist", "Maintenance Expert"]
    },
    'mechanic': {
        'names': [
            "Raja", "Sekar", "Velu", "Arul", "Vimal",
            "Sathish", "Karthik", "Ramesh Babu", "Saravanan", "Antony"
        ],
        'specializations': ["Master Mechanic", "Car Specialist", "Bike Expert", "Engine Specialist", "Maintenance Pro"]
    }
}

def populate():
    print("Clearing existing providers...")
    ServiceProvider.objects.all().delete()
    # Also delete the associated users to avoid unique constraint issues
    User.objects.filter(user_type='provider').delete()
    
    print("Populating database...")

    # Create dummy users for each provider
    provider_count = 0
    for service_type, details in sample_providers.items():
        for i, provider_name in enumerate(details['names']):
            username = f"{service_type}_{i}_{random.randint(1000, 9999)}"
            user = User.objects.create_user(
                username=username,
                password='password123',
                user_type='provider',
                phone=DEFAULT_PHONE
            )
            
            # Create the ServiceProvider instance linked to the user
            provider = ServiceProvider.objects.create(
                user=user,
                name=provider_name,
                service_type=service_type,
                location=random.choice(locations),
                price_per_hour=random.randint(200, 1000),
                phone_number=DEFAULT_PHONE,
                description=f"Experienced {service_type} with over 5 years of professional service. Available for emergency calls."
            )
            
            # Create dummy feedback for the provider to generate a rating
            Feedback.objects.create(
                user=User.objects.filter(user_type='customer').first() or User.objects.create_user(username=f'cust_{random.randint(1,999)}', password='password123', user_type='customer'),
                provider=provider,
                rating=random.randint(3, 5),
                comment="Great service!"
            )
            provider_count += 1
            print(f"Created {provider_name} ({service_type})")

    print(f"Successfully populated {provider_count} service providers.")

if __name__ == '__main__':
    populate()

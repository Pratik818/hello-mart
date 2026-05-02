"""
Run this script to populate the database with sample data:
    python seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import Category, Product

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@hello-mart.com', 'admin123')
    print("✓ Superuser created: admin / ")

# Create categories
categories_data = [
    ('Electronics', 'electronics', 'Latest gadgets and electronics'),
    ('Fashion', 'fashion', 'Trendy clothing and accessories'),
    ('Home & Living', 'home-living', 'Beautiful home decor and essentials'),
    ('Beauty', 'beauty', 'Skincare, makeup and wellness'),
    ('Books', 'books', 'Bestsellers and timeless classics'),
    ('Sports', 'sports', 'Sports gear and fitness equipment'),
]

categories = {}
for name, slug, desc in categories_data:
    cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'description': desc})
    categories[slug] = cat
    print(f"✓ Category: {name}")

# Create products
products_data = [
    ('Wireless Noise-Cancelling Headphones', 'wireless-headphones', 'electronics',
     'Premium over-ear headphones with 30-hour battery life, adaptive noise cancellation, and crystal-clear audio. Perfect for travel, work, and everyday listening.', 8999, 25),
    ('Smart Watch Pro', 'smart-watch-pro', 'electronics',
     'Feature-packed smartwatch with health monitoring, GPS, sleep tracking, and 7-day battery. Compatible with iOS and Android.', 12499, 15),
    ('Bluetooth Speaker', 'bluetooth-speaker', 'electronics',
     'Portable waterproof speaker with 360° sound, 20-hour battery, and deep bass. Perfect for outdoor adventures.', 3499, 40),
    ('Silk Evening Dress', 'silk-evening-dress', 'fashion',
     'Elegant flowing silk dress for special occasions. Available in multiple colors. Machine washable, wrinkle-resistant fabric.', 4999, 20),
    ('Leather Wallet', 'leather-wallet', 'fashion',
     'Handcrafted genuine leather slim wallet with RFID protection. 8 card slots and a hidden pocket for cash.', 1299, 60),
    ('Sunglasses UV400', 'sunglasses-uv400', 'fashion',
     'Polarized UV400 sunglasses with a lightweight titanium frame. Comes with a protective case.', 2199, 35),
    ('Aromatherapy Diffuser', 'aromatherapy-diffuser', 'home-living',
     'Ultrasonic essential oil diffuser with 7 LED colors, auto shut-off, and whisper-quiet operation. Covers up to 400 sq ft.', 1899, 30),
    ('Ceramic Coffee Mug Set', 'ceramic-mug-set', 'home-living',
     ' handcrafted ceramic mugs in earthy tones. Microwave and dishwasher safe. 350ml capacity.', 999, 50),
    ('Bamboo Cutting Board', 'bamboo-cutting-board', 'home-living',
     'Eco-friendly bamboo cutting board with juice groove, handle, and non-slip feet. Naturally antibacterial.', 799, 45),
    ('Vitamin C Serum', 'vitamin-c-serum', 'beauty',
     'Brightening serum with 20% Vitamin C, hyaluronic acid, and vitamin E. Reduces dark spots and boosts collagen.', 1599, 80),
    ('Hydrating Face Mask', 'hydrating-face-mask', 'beauty',
     'Overnight hydrating mask with aloe vera, shea butter, and ceramides. Restores moisture and plumps skin.', 699, 100),
    ('Atomic Habits', 'atomic-habits', 'books',
     'The #1 New York Times bestseller. James Clear\'s proven framework for building good habits and breaking bad ones.', 499, 200),
    ('The Psychology of Money', 'psychology-of-money', 'books',
     'Morgan Housel\'s timeless lessons on wealth, greed, and happiness. A must-read for every investor.', 449, 150),
    ('Yoga Mat Premium', 'yoga-mat-premium', 'sports',
     'Non-slip 6mm thick eco-friendly yoga mat with alignment lines, carrying strap, and moisture-wicking surface.', 1499, 55),
    ('Resistance Bands Set', 'resistance-bands-set', 'sports',
     'Set of 5 latex resistance bands with varying tension levels. Includes a carrying bag and exercise guide.', 799, 70),
]

for name, slug, cat_slug, desc, price, stock in products_data:
    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            'name': name,
            'category': categories[cat_slug],
            'description': desc,
            'price': price,
            'stock': stock,
            'is_active': True,
        }
    )
    if created:
        print(f"✓ Product: {name} — ₹{price}")

print("\n✅ Database seeded successfully!")

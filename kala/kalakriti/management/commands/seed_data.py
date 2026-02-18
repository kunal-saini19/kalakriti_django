from __future__ import annotations

import random
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.utils import timezone

from kalakriti.models import (
    Artisan,
    Category,
    CulturalStory,
    GalleryImage,
    Newsletter,
    Order,
    OrderItem,
    Product,
    ProductActivity,
    Region,
    Seller,
    SellerProduct,
    StoryPost,
    UserProfile,
)

try:
    from PIL import Image, ImageDraw
except Exception:  # pragma: no cover - pillow should be available in environment
    Image = None
    ImageDraw = None


class Command(BaseCommand):
    help = "Seed the database with sensible demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing data before seeding.",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options.get("reset"):
                self._reset_data()

            self._ensure_media_dirs()
            self._create_images()

            users = self._create_users()
            regions = self._create_regions()
            categories = self._create_categories()
            artisans = self._create_artisans(regions)
            sellers = self._create_sellers(users, regions)
            products = self._create_products(categories, regions, artisans, sellers)
            self._create_seller_products(sellers, products)
            self._create_stories(regions)
            self._create_story_posts(users)
            self._create_gallery(artisans, products, regions)
            self._create_orders(users, products)
            self._create_product_activity(sellers, products, users)
            self._create_newsletters(users)

        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))

    def _reset_data(self):
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        ProductActivity.objects.all().delete()
        SellerProduct.objects.all().delete()
        Product.objects.all().delete()
        GalleryImage.objects.all().delete()
        CulturalStory.objects.all().delete()
        StoryPost.objects.all().delete()
        Artisan.objects.all().delete()
        Seller.objects.all().delete()
        UserProfile.objects.all().delete()
        Newsletter.objects.all().delete()
        Category.objects.all().delete()
        Region.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

    def _ensure_media_dirs(self):
        media_root = Path(settings.MEDIA_ROOT)
        for folder in [
            "categories",
            "regions",
            "artisans",
            "products",
            "stories",
            "gallery",
            "shop_logos",
            "profiles",
        ]:
            (media_root / folder).mkdir(parents=True, exist_ok=True)

    def _create_images(self):
        if Image is None:
            return

        media_root = Path(settings.MEDIA_ROOT)
        items = [
            ("categories/textiles.jpg", "Textiles"),
            ("categories/pottery.jpg", "Pottery"),
            ("categories/jewelry.jpg", "Jewelry"),
            ("categories/paintings.jpg", "Paintings"),
            ("regions/rajasthan.jpg", "Rajasthan"),
            ("regions/gujarat.jpg", "Gujarat"),
            ("regions/west-bengal.jpg", "West Bengal"),
            ("regions/tamil-nadu.jpg", "Tamil Nadu"),
            ("artisans/meera-sharma.jpg", "Meera"),
            ("artisans/arjun-patel.jpg", "Arjun"),
            ("artisans/riya-sen.jpg", "Riya"),
            ("artisans/karthik-iyer.jpg", "Karthik"),
            ("products/blue-pottery-vase.jpg", "Blue Vase"),
            ("products/ajrakh-stole.jpg", "Ajrakh"),
            ("products/terracotta-lamp.jpg", "Lamp"),
            ("products/kalamkari-wall-art.jpg", "Kalamkari"),
            ("products/silver-jhumkas.jpg", "Jhumkas"),
            ("products/kantha-throw.jpg", "Kantha"),
            ("stories/heritage-textiles.jpg", "Heritage"),
            ("stories/craft-traditions.jpg", "Traditions"),
            ("gallery/loom.jpg", "Loom"),
            ("gallery/atelier.jpg", "Atelier"),
            ("shop_logos/sadbhav-crafts.jpg", "Sadbhav"),
            ("shop_logos/raaga-studio.jpg", "Raaga"),
            ("shop_logos/sundar-collective.jpg", "Sundar"),
            ("profiles/buyer1.jpg", "Buyer"),
            ("profiles/buyer2.jpg", "Buyer"),
        ]

        for rel_path, label in items:
            file_path = media_root / rel_path
            if file_path.exists():
                continue
            image = Image.new("RGB", (900, 600), self._color_for(label))
            draw = ImageDraw.Draw(image)
            draw.text((40, 40), label, fill=(255, 255, 255))
            image.save(file_path, format="JPEG", quality=85)

    def _color_for(self, seed: str):
        random.seed(seed)
        return (
            random.randint(40, 200),
            random.randint(40, 200),
            random.randint(40, 200),
        )

    def _create_users(self):
        users = {}

        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@kala.local", "is_staff": True, "is_superuser": True},
        )
        if not admin.has_usable_password():
            admin.set_password("Admin123!")
            admin.save(update_fields=["password"])

        buyer1 = self._get_or_create_user("neha", "neha@kala.local", "Kala123!")
        buyer2 = self._get_or_create_user("vikram", "vikram@kala.local", "Kala123!")
        seller1 = self._get_or_create_user("sadbhav", "sadbhav@kala.local", "Kala123!")
        seller2 = self._get_or_create_user("raaga", "raaga@kala.local", "Kala123!")
        seller3 = self._get_or_create_user("sundar", "sundar@kala.local", "Kala123!")

        users.update(
            {
                "admin": admin,
                "buyer1": buyer1,
                "buyer2": buyer2,
                "seller1": seller1,
                "seller2": seller2,
                "seller3": seller3,
            }
        )

        self._create_profile(buyer1, "buyer", "+91-9876543210", "Jaipur")
        self._create_profile(buyer2, "buyer", "+91-9898989898", "Ahmedabad")
        self._create_profile(seller1, "seller", "+91-9000000001", "Jaipur")
        self._create_profile(seller2, "seller", "+91-9000000002", "Kolkata")
        self._create_profile(seller3, "seller", "+91-9000000003", "Chennai")

        return users

    def _get_or_create_user(self, username: str, email: str, password: str):
        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        if created or not user.has_usable_password():
            user.set_password(password)
            user.save(update_fields=["password"])
        return user

    def _create_profile(self, user: User, user_type: str, phone: str, city: str):
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "user_type": user_type,
                "phone": phone,
                "address": f"{city} Heritage Street, Craft Block",
                "city": city,
                "state": "India",
                "pincode": "302001",
                "profile_image": "profiles/buyer1.jpg" if user_type == "buyer" else "profiles/buyer2.jpg",
            },
        )

    def _create_regions(self):
        regions = []
        entries = [
            (
                "Rajasthan",
                "Vibrant desert culture with block printing, blue pottery, and mirror work.",
            ),
            (
                "Gujarat",
                "Home to Ajrakh, Patola, and folk embroidery traditions.",
            ),
            (
                "West Bengal",
                "Known for Kantha, terracotta, and storytelling through textiles.",
            ),
            (
                "Tamil Nadu",
                "Celebrated for Kalamkari, bronze casting, and temple arts.",
            ),
        ]

        for name, description in entries:
            slug = slugify(name)
            region, _ = Region.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": description,
                    "image": f"regions/{slug}.jpg",
                    "cultural_heritage": f"{name} preserves legacy craft communities and heritage guilds.",
                },
            )
            regions.append(region)

        return regions

    def _create_categories(self):
        categories = []
        entries = [
            ("Textiles", "Handwoven stoles, sarees, and throws."),
            ("Pottery", "Terracotta and glazed ceramic pieces."),
            ("Jewelry", "Silver, beadwork, and folk accessories."),
            ("Paintings", "Narrative paintings and wall art."),
        ]

        for name, description in entries:
            slug = slugify(name)
            category, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": description,
                    "image": f"categories/{slug}.jpg",
                },
            )
            categories.append(category)

        return categories

    def _create_artisans(self, regions):
        artisans = []
        entries = [
            (
                "Meera Sharma",
                "Blue pottery artisan specializing in floral glaze work.",
                "Blue Pottery",
                12,
                regions[0],
                True,
            ),
            (
                "Arjun Patel",
                "Ajrakh block printer with a focus on natural dyes.",
                "Ajrakh Printing",
                18,
                regions[1],
                True,
            ),
            (
                "Riya Sen",
                "Kantha storyteller bringing heritage motifs to modern throws.",
                "Kantha Embroidery",
                10,
                regions[2],
                False,
            ),
            (
                "Karthik Iyer",
                "Kalamkari painter known for temple-inspired wall art.",
                "Kalamkari",
                15,
                regions[3],
                False,
            ),
        ]

        for name, bio, specialty, experience, region, featured in entries:
            slug = slugify(name)
            artisan, _ = Artisan.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "bio": bio,
                    "image": f"artisans/{slug}.jpg",
                    "region": region,
                    "specialty": specialty,
                    "years_of_experience": experience,
                    "email": f"{slug}@kala.local",
                    "phone": "+91-9000011122",
                    "website": f"https://{slug}.example.com",
                    "social_media_links": {"instagram": f"https://instagram.com/{slug}"},
                    "featured": featured,
                },
            )
            artisans.append(artisan)

        return artisans

    def _create_sellers(self, users, regions):
        sellers = []
        entries = [
            (
                users["seller1"],
                "Sadbhav Crafts",
                "Curated heritage crafts from Rajasthan.",
                regions[0].name,
                "shop_logos/sadbhav-crafts.jpg",
            ),
            (
                users["seller2"],
                "Raaga Studio",
                "Textile studio celebrating Bengal artisans.",
                regions[2].name,
                "shop_logos/raaga-studio.jpg",
            ),
            (
                users["seller3"],
                "Sundar Collective",
                "Southern crafts and ritual art pieces.",
                regions[3].name,
                "shop_logos/sundar-collective.jpg",
            ),
        ]

        for user, name, description, state, logo in entries:
            seller, _ = Seller.objects.get_or_create(
                user=user,
                defaults={
                    "shop_name": name,
                    "shop_description": description,
                    "shop_logo": logo,
                    "state": state,
                    "phone": "+91-9000000000",
                    "bank_account": "1234567890",
                    "bank_name": "Kala Bank",
                    "ifsc_code": "KALA0001234",
                    "rating": round(random.uniform(4.2, 4.9), 2),
                    "is_verified": True,
                },
            )
            sellers.append(seller)

        return sellers

    def _create_products(self, categories, regions, artisans, sellers):
        products = []
        entries = [
            (
                "Blue Pottery Vase",
                "Hand-painted blue pottery vase with floral patterns.",
                categories[1],
                regions[0],
                artisans[0],
                sellers[0],
                Decimal("2499.00"),
                "products/blue-pottery-vase.jpg",
                True,
                12,
            ),
            (
                "Ajrakh Cotton Stole",
                "Naturally dyed Ajrakh stole with geometric motifs.",
                categories[0],
                regions[1],
                artisans[1],
                sellers[0],
                Decimal("1899.00"),
                "products/ajrakh-stole.jpg",
                True,
                25,
            ),
            (
                "Terracotta Lamp",
                "Handcrafted terracotta lamp with cutwork design.",
                categories[1],
                regions[2],
                artisans[2],
                sellers[1],
                Decimal("1599.00"),
                "products/terracotta-lamp.jpg",
                False,
                18,
            ),
            (
                "Kalamkari Wall Art",
                "Detailed Kalamkari wall art inspired by temple narratives.",
                categories[3],
                regions[3],
                artisans[3],
                sellers[2],
                Decimal("3199.00"),
                "products/kalamkari-wall-art.jpg",
                True,
                8,
            ),
            (
                "Silver Jhumkas",
                "Hand-finished silver jhumkas with bead detailing.",
                categories[2],
                regions[1],
                artisans[1],
                sellers[2],
                Decimal("1299.00"),
                "products/silver-jhumkas.jpg",
                True,
                32,
            ),
            (
                "Kantha Throw",
                "Soft Kantha throw with layered storytelling motifs.",
                categories[0],
                regions[2],
                artisans[2],
                sellers[1],
                Decimal("2799.00"),
                "products/kantha-throw.jpg",
                False,
                14,
            ),
        ]

        for name, desc, category, region, artisan, seller, price, image, featured, stock in entries:
            slug = slugify(name)
            product, _ = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": desc,
                    "category": category,
                    "region": region,
                    "artisan": artisan,
                    "seller": seller,
                    "price": price,
                    "original_price": price + Decimal("400.00"),
                    "stock": stock,
                    "image": image,
                    "gallery_images": [image],
                    "featured": featured,
                    "in_stock": stock > 0,
                    "rating": round(random.uniform(4.1, 4.9), 2),
                    "reviews_count": random.randint(6, 42),
                },
            )
            products.append(product)

        for seller in sellers:
            seller.total_products = Product.objects.filter(seller=seller).count()
            seller.total_sales = Decimal(random.randint(50, 200)) * Decimal("100.00")
            seller.save(update_fields=["total_products", "total_sales"])

        return products

    def _create_seller_products(self, sellers, products):
        for product in products:
            SellerProduct.objects.get_or_create(
                seller=product.seller,
                product=product,
                defaults={
                    "seller_sku": f"{product.slug[:10].upper()}-{random.randint(1000, 9999)}",
                    "seller_price": product.price,
                    "seller_stock": product.stock,
                },
            )

    def _create_stories(self, regions):
        entries = [
            (
                "Threads of the Desert",
                "Rajasthan's textile heritage blends color, mirror work, and nomadic tales.",
                regions[0],
            ),
            (
                "Ajrakh and the Rhythm of Print",
                "Ajrakh printing is a ritual of dye, patience, and geometry.",
                regions[1],
            ),
            (
                "Kantha: Stories in Stitches",
                "Bengal's Kantha reflects memory, daily life, and resilience.",
                regions[2],
            ),
            (
                "Temple Murals and Kalamkari",
                "Tamil Nadu's Kalamkari connects myth, craft, and devotion.",
                regions[3],
            ),
        ]

        for title, content, region in entries:
            slug = slugify(title)
            CulturalStory.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "content": content,
                    "author": "Kala Editorial",
                    "featured_image": "stories/heritage-textiles.jpg",
                    "region": region,
                    "category": "Heritage",
                    "published": True,
                },
            )

    def _create_story_posts(self, users):
        entries = [
            (users["buyer1"], "Visited the artisans market today. The detailing was incredible."),
            (users["buyer2"], "Just got my handcrafted order. Quality is amazing and delivery was smooth."),
            (users["seller1"], "New hand-painted collection just dropped this week."),
            (users["seller2"], "Working on fresh textile patterns inspired by Bengal heritage."),
            (users["seller3"], "Thank you for the support on our latest craft launch!"),
        ]

        for user, content in entries:
            if not StoryPost.objects.filter(user=user, content=content).exists():
                StoryPost.objects.create(user=user, content=content)

    def _create_gallery(self, artisans, products, regions):
        entries = [
            ("Loom in Motion", "gallery/loom.jpg", artisans[1], None, None, True),
            ("Craft Atelier", "gallery/atelier.jpg", artisans[3], None, None, False),
            ("Blue Pottery Detail", "gallery/loom.jpg", None, products[0], None, True),
            ("Terracotta Textures", "gallery/atelier.jpg", None, products[2], None, False),
            ("Desert Workshop", "gallery/loom.jpg", None, None, regions[0], False),
        ]

        for title, image, artisan, product, region, featured in entries:
            GalleryImage.objects.get_or_create(
                title=title,
                defaults={
                    "image": image,
                    "description": f"{title} capturing the craft process.",
                    "artisan": artisan,
                    "product": product,
                    "region": region,
                    "featured": featured,
                },
            )

    def _create_orders(self, users, products):
        buyer1 = users["buyer1"]
        buyer2 = users["buyer2"]

        order1, _ = Order.objects.get_or_create(
            user=buyer1,
            status="delivered",
            defaults={
                "total_amount": Decimal("4398.00"),
                "shipping_address": "Jaipur Heritage Street, 302001",
            },
        )
        order2, _ = Order.objects.get_or_create(
            user=buyer2,
            status="processing",
            defaults={
                "total_amount": Decimal("2799.00"),
                "shipping_address": "Ahmedabad Craft Lane, 380001",
            },
        )

        OrderItem.objects.get_or_create(
            order=order1,
            product=products[0],
            defaults={"quantity": 1, "price": products[0].price},
        )
        OrderItem.objects.get_or_create(
            order=order1,
            product=products[1],
            defaults={"quantity": 1, "price": products[1].price},
        )
        OrderItem.objects.get_or_create(
            order=order2,
            product=products[5],
            defaults={"quantity": 1, "price": products[5].price},
        )

    def _create_product_activity(self, sellers, products, users):
        buyer1 = users["buyer1"]
        buyer2 = users["buyer2"]
        activity_types = ["view", "click", "add_cart", "purchase"]

        for product in products:
            for _ in range(3):
                ProductActivity.objects.create(
                    seller=product.seller,
                    product=product,
                    activity_type=random.choice(activity_types),
                    user=random.choice([buyer1, buyer2]),
                    details={"source": "seed", "ref": "homepage"},
                    created_at=timezone.now(),
                )

    def _create_newsletters(self, users):
        Newsletter.objects.get_or_create(email=users["buyer1"].email)
        Newsletter.objects.get_or_create(email=users["buyer2"].email)

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import StoryPost, Seller, UserProfile, Region, Category, Product


class StoryPageTests(TestCase):
	def setUp(self):
		self.user1 = User.objects.create_user(
			username='neha',
			email='neha@kala.local',
			password='Kala123!'
		)
		self.user2 = User.objects.create_user(
			username='vikram',
			email='vikram@kala.local',
			password='Kala123!'
		)

	def test_stories_page_status_with_fake_story(self):
		StoryPost.objects.create(user=self.user2, content='Fake story for status check')
		response = self.client.get(reverse('kalakriti:cultural_stories'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Fake story for status check')

	def test_authenticated_user_does_not_see_own_story_in_feed(self):
		StoryPost.objects.create(user=self.user1, content='My own story')
		StoryPost.objects.create(user=self.user2, content='Other user story')

		self.client.login(username='neha', password='Kala123!')
		response = self.client.get(reverse('kalakriti:cultural_stories'))

		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, 'My own story')
		self.assertContains(response, 'Other user story')

	def test_ajax_post_story_creates_story(self):
		self.client.login(username='neha', password='Kala123!')

		response = self.client.post(
			reverse('kalakriti:cultural_stories'),
			{'content': 'Posting from test case'},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(StoryPost.objects.filter(user=self.user1, content='Posting from test case').exists())


class SellerRegionSyncTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='seller_user',
			email='seller@kala.local',
			password='Kala123!'
		)
		self.profile = UserProfile.objects.create(user=self.user, user_type='seller', seller_verified=True)
		self.seller = Seller.objects.create(
			user=self.user,
			shop_name='Seller Shop',
			shop_description='Test seller',
			phone='+91 9999999999',
			state='Rajasthan',
		)
		self.category = Category.objects.create(name='Test Category', slug='test-category')

	def test_profile_state_change_creates_region(self):
		self.client.login(username='seller_user', password='Kala123!')

		response = self.client.post(
			reverse('kalakriti:seller_profile'),
			{
				'shop_name': 'Seller Shop',
				'shop_description': 'Updated',
				'country_code': '+91',
				'phone': '9999999999',
				'state': 'Punjab',
				'first_name': 'Seller',
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(Region.objects.filter(name__iexact='Punjab').exists())

	def test_bulk_upload_assigns_region_from_seller_state(self):
		self.client.login(username='seller_user', password='Kala123!')

		self.client.post(
			reverse('kalakriti:seller_profile'),
			{
				'shop_name': 'Seller Shop',
				'shop_description': 'Updated',
				'country_code': '+91',
				'phone': '9999999999',
				'state': 'Punjab',
				'first_name': 'Seller',
			},
			follow=True,
		)

		response = self.client.post(
			reverse('kalakriti:bulk_upload'),
			{
				'product_name[]': ['Punjab Craft Item'],
				'category[]': [str(self.category.id)],
				'new_category[]': [''],
				'price[]': ['999'],
				'stock[]': ['5'],
				'description[]': ['Craft from updated seller region'],
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		product = Product.objects.get(name='Punjab Craft Item')
		self.assertIsNotNone(product.region)
		self.assertEqual(product.region.name, 'Punjab')

		products_page = self.client.get(reverse('kalakriti:products_list'))
		self.assertContains(products_page, 'Punjab')

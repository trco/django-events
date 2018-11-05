from django.contrib.auth.models import User
from django.test import TestCase
from .models import Event


class AuthenticationViewsTest(TestCase):

    def setUp(self):
        # create user
        self.user = User.objects.create_user(
            username='user',
            password='test1234'
        )
        # login
        self.client.login(username='user', password='test1234')

    def test_login_logout(self):
        response = self.client.get('/')
        # check that the user is logged in
        self.assertEqual(str(response.context['user']), 'user')

        # logout
        response = self.client.logout()
        response = self.client.get('/')
        # check that the user is logged out
        self.assertEqual(str(response.context['user']), 'AnonymousUser')

    def test_login_redirection(self):
        response = self.client.get('/accounts/login/redirection/')
        self.assertRedirects(response, f'/{ self.user.username }')


class IndexViewTest(TestCase):

    def test_index_visit(self):
        response = self.client.get('/')
        self.assertContains(response, 'Events Marketplace')
        self.assertContains(response, 'Add Event')

    def test_go_to_create_event(self):
        User.objects.create_user(
            username='user',
            password='test1234'
        )
        # login
        self.client.login(username='user', password='test1234')
        response = self.client.get('/events/add')
        self.assertContains(response, 'Add Event')

    def test_display_events_at_index(self):
        event_one = Event.objects.create(title='Test event #1')
        event_two = Event.objects.create(title='Test event #2')

        response = self.client.get('/')

        self.assertContains(response, 'Test event #1')
        self.assertContains(response, 'Test event #2')


class UserProfileTest(TestCase):

    def setUp(self):
        # create user
        self.user_1 = User.objects.create_user(
            username='user_1',
            password='test1234'
        )
        self.event_1 = Event.objects.create(
            title='Test event #1',
            user=self.user_1
        )
        self.user_2 = User.objects.create_user(
            username='user_2',
            password='test1234'
        )
        self.event_1 = Event.objects.create(
            title='Test event #2',
            user=self.user_2
        )
        # login
        self.client.login(username='user_1', password='test1234')

    def test_display_user_events(self):
        response = self.client.get(f'/{ self.user_1.username }')
        self.assertContains(response, 'Test event #1')
        self.assertNotContains(response, 'Test event #2')

    def test_display_other_user_events_readonly(self):
        response = self.client.get(f'/{ self.user_2.username }')
        self.assertContains(response, 'Test event #2')
        self.assertNotContains(response, 'Test event #1')
        self.assertNotContains(response, 'Edit')


class CreateEventViewTest(TestCase):

    def setUp(self):
        # create user
        self.user = User.objects.create_user(
            username='user',
            password='test1234'
        )
        # login
        self.client.login(username='user', password='test1234')

    def test_create_event_post(self):
        response = self.client.post(
            '/events/add',
            data={'title_text': 'Test title #1'}
        )
        self.assertEqual(Event.objects.count(), 1)
        new_event = Event.objects.first()
        self.assertEqual(new_event.title, 'Test title #1')

    def test_redirect_after_post(self):
        response = self.client.post(
            '/events/add',
            data={'title_text': 'Test title #1'}
        )
        self.assertRedirects(response, f'/{ self.user.username }')


class UpdateEventViewTest(TestCase):

    def setUp(self):
        # create user
        self.user_1 = User.objects.create_user(
            username='user_1',
            password='test1234'
        )
        self.user_2 = User.objects.create_user(
            username='user_2',
            password='test1234'
        )
        self.event_1 = Event.objects.create(
            title='Test event #1',
            user=self.user_1
        )
        self.event_2 = Event.objects.create(
            title='Test event #2',
            user=self.user_2
        )
        # login
        self.client.login(username='user_1', password='test1234')

    def test_update_event_post(self):
        response = self.client.post(
            f'/events/edit/{ self.event_1.id }',
            data={'title_text': 'Test title #2'}
        )
        self.assertEqual(Event.objects.count(), 2)
        updated_event = Event.objects.first()
        self.assertEqual(updated_event.title, 'Test title #2')

    def test_redirect_after_post(self):
        response = self.client.post(
            f'/events/edit/{ self.event_1.id }',
            data={'title_text': 'Test title #2'}
        )
        self.assertRedirects(response, f'/{ self.user_1.username }')

    def test_cannot_update_other_users_event(self):
        response = self.client.post(
            f'/events/edit/{ self.event_2.id }',
            data={'title_text': 'Test title #3'}
        )
        self.assertEqual(response.status_code, 403)


class DeleteEventViewTest(TestCase):

    def setUp(self):
        # create users
        self.user_1 = User.objects.create_user(
            username='user_1',
            password='test1234'
        )
        self.user_2 = User.objects.create_user(
            username='user_2',
            password='test1234'
        )
        # create events
        self.event_1 = Event.objects.create(
            title='Test event #1',
            user=self.user_1
        )
        self.event_2 = Event.objects.create(
            title='Test event #2',
            user=self.user_1
        )
        self.event_3 = Event.objects.create(
            title='Test event #3',
            user=self.user_2
        )
        # login
        self.client.login(username='user_1', password='test1234')

    def test_delete_event_get(self):
        response = self.client.get(
            f'/events/delete/{ self.event_1.id }'
        )
        self.assertEqual(Event.objects.count(), 3)
        first_event = Event.objects.first()
        self.assertEqual(first_event.title, 'Test event #1')
        self.assertEqual(response.context['event'], self.event_1)

    def test_delete_event_post(self):
        response = self.client.post(
            f'/events/delete/{ self.event_1.id }'
        )
        self.assertEqual(Event.objects.count(), 2)
        first_event = Event.objects.first()
        self.assertEqual(first_event.title, 'Test event #2')

    def test_redirect_after_post(self):
        response = self.client.post(
            f'/events/delete/{ self.event_1.id }'
        )
        self.assertRedirects(response, f'/{ self.user_1.username }')

    def test_cannot_delete_other_users_event(self):
        response = self.client.post(
            f'/events/delete/{ self.event_3.id }'
        )
        self.assertEqual(response.status_code, 403)


class EventModelTest(TestCase):

    def test_create_read_event(self):
        # create events
        event_one = Event()
        event_one.title = 'Test event #1'
        event_one.save()

        event_two = Event()
        event_two.title = 'Test event #2'
        event_two.save()

        # read events
        events = Event.objects.all()
        self.assertEqual(events.count(), 2)

        saved_event_one = events[0]
        saved_event_two = events[1]

        self.assertIn('Test event #1', saved_event_one.title)
        self.assertIn('Test event #2', saved_event_two.title)

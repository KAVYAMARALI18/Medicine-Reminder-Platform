from django.test import TestCase

from django.urls import reverse

from .models import User


class RegistrationUsernameTests(TestCase):
    def test_registration_accepts_username_with_spaces(self):
        response = self.client.post(reverse('register'), {
            'username': 'kavya m',
            'email': 'kavya@example.com',
            'password1': 'Safe-Password-9482!',
            'password2': 'Safe-Password-9482!',
        })

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='kavya m').exists())
        self.assertEqual(response.wsgi_request.user.username, 'kavya m')

        self.client.logout()
        login_response = self.client.post(reverse('login'), {
            'username': 'kavya m',
            'password': 'Safe-Password-9482!',
        })

        self.assertRedirects(login_response, reverse('dashboard'))
        self.assertEqual(login_response.wsgi_request.user.username, 'kavya m')

    def test_registration_still_rejects_unsupported_username_characters(self):
        response = self.client.post(reverse('register'), {
            'username': 'kavya!',
            'email': 'kavya@example.com',
            'password1': 'Safe-Password-9482!',
            'password2': 'Safe-Password-9482!',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='kavya!').exists())
        self.assertContains(response, 'Use letters, numbers, spaces')

    def test_password_similarity_error_is_shown_on_password_field(self):
        response = self.client.post(reverse('register'), {
            'username': 'karthik',
            'email': 'karthik@example.com',
            'password1': 'karthik123!',
            'password2': 'karthik123!',
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('password1', response.context['form'].errors)
        self.assertNotIn('password2', response.context['form'].errors)
        self.assertContains(response, 'The password is too similar to the username.')

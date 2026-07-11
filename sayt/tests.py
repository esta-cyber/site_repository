from django.test import TestCase
from django.urls import reverse


class LoginFlowTests(TestCase):
    def test_admin_login_redirects_to_admin_dashboard(self):
        response = self.client.post(
            reverse('enter'),
            {'surname': 'Adminov', 'login': 'admin'},
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin-boshqarish-bulimi/')

    def test_student_login_redirects_to_student_dashboard(self):
        response = self.client.post(
            reverse('enter'),
            {'surname': 'Aliyev', 'login': 'aliyev'},
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/student-dashboard/')

    def test_teacher_login_redirects_to_teacher_dashboard(self):
        response = self.client.post(
            reverse('enter'),
            {'surname': 'Karimov', 'login': 'teacher'},
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/teacher-dashboard/')

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            reverse('enter'),
            {'surname': 'NotFound', 'login': 'wrong'},
            follow=True,
        )
        self.assertContains(response, 'Noto&#x27;g&#x27;ri surname yoki login')


# ----------------------------------------------------------------------------------------------------------
from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page_code = (
            ('/about/author/', HTTPStatus.OK),
            ('/about/tech/', HTTPStatus.OK),
        )

    def setUp(self):
        self.guest_client = Client()

    def test_urls_with_codes(self):
        for url, code in StaticURLTests.page_code:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, code)

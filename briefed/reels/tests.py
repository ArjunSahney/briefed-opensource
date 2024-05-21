from django.test import TestCase
from .models import Reel

class ReelModelTest(TestCase):

    def setUp(self):
        Reel.objects.create(
            title="Test Reel",
            summary="This is a test reel.",
            image_url="http://example.com/image.jpg",
            sources={"source1": "http://example.com/source1"}
        )

    def test_reel_content(self):
        reel = Reel.objects.get(id=1)
        self.assertEqual(reel.title, "Test Reel")
        self.assertEqual(reel.summary, "This is a test reel.")
        self.assertEqual(reel.image_url, "http://example.com/image.jpg")
        self.assertEqual(reel.sources, {"source1": "http://example.com/source1"})

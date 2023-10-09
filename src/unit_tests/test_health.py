from unittest import TestCase

class TestHealth(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestHealth, self).__init__(*args, **kwargs)

    def test_get_health(self):
        ## Given
        from routes.health import get_health
        
        ## When
        result = get_health()

        ## Then
        self.assertIsNotNone(result)
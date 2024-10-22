from django.test import TestCase

from mysql_manager import DatabaseManager

# Test the database manager class
class TestDatabaseManager(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods"""
        pass
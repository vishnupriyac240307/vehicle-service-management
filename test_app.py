"""
TN SKILLS – Database Administration Back End – Oracle
Vehicle Service Management Database System
Automated Test Suite: test_app.py
Verifies routes, template rendering, and error handling.
"""

import unittest
from app import app
from db import db_manager


class VehicleServiceManagementTests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_dashboard_route(self):
        """Dashboard renders with HTTP 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AutoService DB", response.data)
        self.assertIn(b"TN SKILLS", response.data)

    def test_customers_list_route(self):
        """Customers page renders with HTTP 200."""
        response = self.client.get('/customers')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Customer Management", response.data)

    def test_vehicles_list_route(self):
        """Vehicles page renders with HTTP 200."""
        response = self.client.get('/vehicles')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Vehicle Management", response.data)

    def test_services_list_route(self):
        """Services page renders with HTTP 200."""
        response = self.client.get('/services')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Service Order Management", response.data)

    def test_reports_route(self):
        """Reports page renders with HTTP 200 and all sections."""
        response = self.client.get('/reports')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Oracle SQL Analytical Reports", response.data)
        self.assertIn(b"THREE-TABLE RELATIONAL JOIN", response.data)
        self.assertIn(b"AGGREGATE FUNCTIONS", response.data)
        self.assertIn(b"GROUPING (GROUP BY)", response.data)

    def test_db_status_route(self):
        """DB Status page renders with diagnostics and setup guide."""
        response = self.client.get('/db-status')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Oracle Database Diagnostics", response.data)
        self.assertIn(b"full_database_setup.sql", response.data)

    def test_api_db_test_route(self):
        """API connection test endpoint returns JSON."""
        response = self.client.get('/api/db-test')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIn('connected', data)
        self.assertIn('dsn', data)


if __name__ == '__main__':
    unittest.main()

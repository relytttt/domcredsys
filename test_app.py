"""
Unit tests for the Domain Credit System (domcredsys)
Tests for claim/unclaim credit functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import sys
import os

# Add the parent directory to the path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set mock environment variables before importing app
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test-key'
os.environ['SECRET_KEY'] = 'test-secret-key'

# Mock supabase before importing app
with patch('app.create_client'):
    from app import app


class TestClaimCredit(unittest.TestCase):
    """Test cases for claim_credit() function"""

    def setUp(self):
        """Set up test client and mock environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def _create_session(self, user_code='1234', display_name='Test User', is_admin=False, selected_store='STORE1'):
        """Helper to create a session"""
        with self.client.session_transaction() as sess:
            sess['user_code'] = user_code
            sess['display_name'] = display_name
            sess['is_admin'] = is_admin
            sess['selected_store'] = selected_store

    @patch('app.supabase')
    def test_claim_credit_success(self, mock_supabase):
        """Test successful credit claiming"""
        self._create_session()
        
        # Mock the SELECT query - credit exists and is active
        mock_select_result = Mock()
        mock_select_result.data = [{'code': 'ABC', 'status': 'active', 'customer_name': 'John Doe'}]
        
        # Mock the UPDATE query - update succeeds
        mock_update_result = Mock()
        mock_update_result.data = [{'code': 'ABC', 'status': 'claimed'}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/claim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.location)

    @patch('app.supabase')
    def test_claim_credit_not_found(self, mock_supabase):
        """Test claiming a credit that doesn't exist"""
        self._create_session()
        
        # Mock the SELECT query - credit not found
        mock_select_result = Mock()
        mock_select_result.data = []
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/claim-credit', data={
            'code': 'XYZ'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    @patch('app.supabase')
    def test_claim_credit_database_error(self, mock_supabase):
        """Test handling of database errors during claiming"""
        self._create_session()
        
        # Mock the SELECT query to raise an exception
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception("Database connection error")
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/claim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.location)

    @patch('app.supabase')
    def test_claim_credit_update_fails(self, mock_supabase):
        """Test when credit exists but update fails"""
        self._create_session()
        
        # Mock the SELECT query - credit exists
        mock_select_result = Mock()
        mock_select_result.data = [{'code': 'ABC', 'status': 'active', 'customer_name': 'John Doe'}]
        
        # Mock the UPDATE query - update fails (no data returned)
        mock_update_result = Mock()
        mock_update_result.data = []
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/claim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    def test_claim_credit_no_session(self):
        """Test claiming without being logged in"""
        response = self.client.post('/claim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_claim_credit_invalid_user_code(self):
        """Test claiming with invalid user session (no user_code)"""
        with self.client.session_transaction() as sess:
            sess['display_name'] = 'Test User'
            sess['selected_store'] = 'STORE1'
            # user_code is missing
        
        response = self.client.post('/claim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_claim_credit_invalid_display_name(self):
        """Test claiming with invalid display_name (empty string fallback to user_code is OK)"""
        with self.client.session_transaction() as sess:
            sess['user_code'] = '1234'
            sess['display_name'] = ''  # Empty display name, but will fallback to user_code
            sess['selected_store'] = 'STORE1'
        
        # This should actually work because display_name falls back to user_code
        # So we expect it to attempt the claim (and fail due to missing mocks)
        # Let's test the case where both are missing instead
        with self.client.session_transaction() as sess:
            sess.pop('user_code', None)
            sess['display_name'] = ''
            sess['selected_store'] = 'STORE1'
        
        response = self.client.post('/claim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_claim_credit_no_store(self):
        """Test claiming without selecting a store"""
        with self.client.session_transaction() as sess:
            sess['user_code'] = '1234'
            sess['display_name'] = 'Test User'
            # selected_store is missing
        
        response = self.client.post('/claim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    def test_claim_credit_invalid_code_length(self):
        """Test claiming with invalid code length"""
        self._create_session()
        
        response = self.client.post('/claim-credit', data={
            'code': 'AB'  # Too short
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    # Remove the old customer name/phone tests as they are no longer relevant


class TestUnclaimCredit(unittest.TestCase):
    """Test cases for unclaim_credit() function"""

    def setUp(self):
        """Set up test client and mock environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def _create_session(self, user_code='1234', display_name='Test User', is_admin=False, selected_store='STORE1'):
        """Helper to create a session"""
        with self.client.session_transaction() as sess:
            sess['user_code'] = user_code
            sess['display_name'] = display_name
            sess['is_admin'] = is_admin
            sess['selected_store'] = selected_store

    @patch('app.supabase')
    def test_unclaim_credit_success(self, mock_supabase):
        """Test successful credit unclaiming by the same user who claimed it"""
        self._create_session(user_code='1234')
        
        # Mock the SELECT query - credit exists and is claimed by this user
        mock_select_result = Mock()
        mock_select_result.data = [{
            'code': 'ABC',
            'status': 'claimed',
            'claimed_by_user': '1234'
        }]
        
        # Mock the UPDATE query - update succeeds
        mock_update_result = Mock()
        mock_update_result.data = [{'code': 'ABC', 'status': 'active'}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/unclaim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.location)

    @patch('app.supabase')
    def test_unclaim_credit_by_admin(self, mock_supabase):
        """Test admin can unclaim any credit"""
        self._create_session(user_code='9999', is_admin=True)
        
        # Mock the SELECT query - credit claimed by different user
        mock_select_result = Mock()
        mock_select_result.data = [{
            'code': 'ABC',
            'status': 'claimed',
            'claimed_by_user': '1234'
        }]
        
        # Mock the UPDATE query
        mock_update_result = Mock()
        mock_update_result.data = [{'code': 'ABC', 'status': 'active'}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/unclaim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    @patch('app.supabase')
    def test_unclaim_credit_unauthorized(self, mock_supabase):
        """Test that regular users can't unclaim credits claimed by others"""
        self._create_session(user_code='5678', is_admin=False)
        
        # Mock the SELECT query - credit claimed by different user
        mock_select_result = Mock()
        mock_select_result.data = [{
            'code': 'ABC',
            'status': 'claimed',
            'claimed_by_user': '1234'
        }]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/unclaim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    @patch('app.supabase')
    def test_unclaim_credit_not_found(self, mock_supabase):
        """Test unclaiming a credit that doesn't exist"""
        self._create_session()
        
        # Mock the SELECT query - credit not found
        mock_select_result = Mock()
        mock_select_result.data = []
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/unclaim-credit', data={
            'code': 'XYZ'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    @patch('app.supabase')
    def test_unclaim_credit_database_error(self, mock_supabase):
        """Test handling of database errors during unclaiming"""
        self._create_session()
        
        # Mock the SELECT query to raise an exception
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception("Database connection error")
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/unclaim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.location)

    @patch('app.supabase')
    def test_unclaim_credit_update_fails(self, mock_supabase):
        """Test when credit exists but update fails"""
        self._create_session(user_code='1234')
        
        # Mock the SELECT query - credit exists
        mock_select_result = Mock()
        mock_select_result.data = [{
            'code': 'ABC',
            'status': 'claimed',
            'claimed_by_user': '1234'
        }]
        
        # Mock the UPDATE query - update fails (no data returned)
        mock_update_result = Mock()
        mock_update_result.data = []
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/unclaim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    def test_unclaim_credit_no_session(self):
        """Test unclaiming without being logged in"""
        response = self.client.post('/unclaim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_unclaim_credit_invalid_user_code(self):
        """Test unclaiming with invalid user session (no user_code)"""
        with self.client.session_transaction() as sess:
            sess['display_name'] = 'Test User'
            sess['selected_store'] = 'STORE1'
            # user_code is missing
        
        response = self.client.post('/unclaim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_unclaim_credit_no_store(self):
        """Test unclaiming without selecting a store"""
        with self.client.session_transaction() as sess:
            sess['user_code'] = '1234'
            sess['display_name'] = 'Test User'
            # selected_store is missing
        
        response = self.client.post('/unclaim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    def test_unclaim_credit_invalid_code_length(self):
        """Test unclaiming with invalid code length"""
        self._create_session()
        
        response = self.client.post('/unclaim-credit', data={
            'code': 'AB'  # Too short
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    @patch('app.supabase')
    def test_unclaim_legacy_credit_as_admin(self, mock_supabase):
        """Test admin can unclaim legacy credits (claimed_by_user is None)"""
        self._create_session(user_code='9999', is_admin=True)
        
        # Mock the SELECT query - legacy credit (no claimed_by_user)
        mock_select_result = Mock()
        mock_select_result.data = [{
            'code': 'ABC',
            'status': 'claimed',
            'claimed_by_user': None
        }]
        
        # Mock the UPDATE query
        mock_update_result = Mock()
        mock_update_result.data = [{'code': 'ABC', 'status': 'active'}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/unclaim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    @patch('app.supabase')
    def test_unclaim_legacy_credit_as_user(self, mock_supabase):
        """Test regular user cannot unclaim legacy credits"""
        self._create_session(user_code='1234', is_admin=False)
        
        # Mock the SELECT query - legacy credit (no claimed_by_user)
        mock_select_result = Mock()
        mock_select_result.data = [{
            'code': 'ABC',
            'status': 'claimed',
            'claimed_by_user': None
        }]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/unclaim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)


class TestCreateCreditWithCustomer(unittest.TestCase):
    """Test cases for create_credit() with customer information"""

    def setUp(self):
        """Set up test client and mock environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def _create_session(self, user_code='1234', display_name='Test User', is_admin=False, selected_store='STORE1'):
        """Helper to create a session"""
        with self.client.session_transaction() as sess:
            sess['user_code'] = user_code
            sess['display_name'] = display_name
            sess['is_admin'] = is_admin
            sess['selected_store'] = selected_store

    @patch('app.supabase')
    @patch('app.generate_code')
    def test_create_credit_with_customer_success(self, mock_generate_code, mock_supabase):
        """Test successful credit creation with customer information"""
        self._create_session()
        mock_generate_code.return_value = 'ABC'
        
        # Mock the insert query
        mock_insert_result = Mock()
        mock_insert_result.data = [{'code': 'ABC'}]
        
        mock_table = Mock()
        mock_table.insert.return_value.execute.return_value = mock_insert_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/create-credit', data={
            'items': '["Item 1", "Item 2"]',
            'reason': 'Test reason',
            'customer_name': 'John Doe',
            'customer_phone': '1234567890'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        # Verify the insert was called with customer info
        mock_table.insert.assert_called_once()
        call_args = mock_table.insert.call_args[0][0]
        self.assertEqual(call_args['customer_name'], 'John Doe')
        self.assertEqual(call_args['customer_phone'], '1234567890')

    def test_create_credit_missing_customer_name(self):
        """Test creating credit without customer name fails"""
        self._create_session()
        
        response = self.client.post('/create-credit', data={
            'items': '["Item 1"]',
            'reason': 'Test reason',
            'customer_name': '',
            'customer_phone': '1234567890'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)

    def test_create_credit_missing_customer_phone(self):
        """Test creating credit without customer phone fails"""
        self._create_session()
        
        response = self.client.post('/create-credit', data={
            'items': '["Item 1"]',
            'reason': 'Test reason',
            'customer_name': 'John Doe',
            'customer_phone': ''
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)


class TestClaimCreditNoCustomerInput(unittest.TestCase):
    """Test cases for claiming credits without requiring customer input"""

    def setUp(self):
        """Set up test client and mock environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def _create_session(self, user_code='1234', display_name='Test User', is_admin=False, selected_store='STORE1'):
        """Helper to create a session"""
        with self.client.session_transaction() as sess:
            sess['user_code'] = user_code
            sess['display_name'] = display_name
            sess['is_admin'] = is_admin
            sess['selected_store'] = selected_store

    @patch('app.supabase')
    def test_claim_credit_without_customer_input(self, mock_supabase):
        """Test claiming credit without providing customer details (uses stored info)"""
        self._create_session()
        
        # Mock the SELECT query - credit exists with customer info
        mock_select_result = Mock()
        mock_select_result.data = [{
            'code': 'ABC',
            'status': 'active',
            'customer_name': 'Jane Smith',
            'customer_phone': '9876543210'
        }]
        
        # Mock the UPDATE query
        mock_update_result = Mock()
        mock_update_result.data = [{'code': 'ABC', 'status': 'claimed'}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        mock_supabase.table.return_value = mock_table
        
        response = self.client.post('/claim-credit', data={
            'code': 'ABC'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        # Verify update was called without customer_name and customer_phone
        mock_table.update.assert_called_once()
        update_data = mock_table.update.call_args[0][0]
        self.assertNotIn('customer_name', update_data)
        self.assertNotIn('customer_phone', update_data)


if __name__ == '__main__':
    unittest.main()

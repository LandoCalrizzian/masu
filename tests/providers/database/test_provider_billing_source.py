#
# Copyright 2018 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""Test the ProviderBillingSourceDB utility object."""

from masu.providers.database.provider_billing_source import ProviderBillingSourceDB
from tests import MasuTestCase


class ProviderBillingSourceDBTest(MasuTestCase):
    """Test Cases for the ProviderBillingSourceDB object."""

    def test_initializer(self):
        """Test Initializer"""
        billing_source_id = '1'
        accessor = ProviderBillingSourceDB(billing_source_id)
        self.assertIsNotNone(accessor._session)
        self.assertTrue(accessor.does_db_entry_exist())

    def test_get_uuid(self):
        """Test uuid getter."""
        auth_id = '1'
        accessor = ProviderBillingSourceDB(auth_id)
        self.assertEqual('75b17096-319a-45ec-92c1-18dbd5e78f94', accessor.get_uuid())

    def test_get_provider_resource_name(self):
        """Test provider name getter."""
        auth_id = '1'
        accessor = ProviderBillingSourceDB(auth_id)
        self.assertEqual('test-bucket', accessor.get_bucket())

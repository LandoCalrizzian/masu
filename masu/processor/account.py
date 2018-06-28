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
"""Provider external interface for koku to consume."""


from masu.providers.database.accessors import ProviderDB


# pylint: disable=too-few-public-methods, fixme
class Account():
    """Interface for masu to use to get accounts."""

    # TODO: in the future, we will abstract this a bit, so that we can support
    # multiple types of accounts, and build-out provider-specific report
    # downloading flows.
    def __init__(self):
        """Construct an Account."""
        self.providers = ProviderDB().all()

    def all(self):
        """
        Retrieve all accounts from the database managed by Koku.

        This will return a list of dicts for the Orchestrator to use to download reports.

        Args:
            None

        Returns:
            ([{}]) : A list of dicts containing Account details

        """
        accounts = []
        for provider in self.providers:
            provider_accessor = ProviderDB(provider.uuid)
            auth_credential = provider_accessor.get_authentication()
            billing_source = provider_accessor.get_billing_source()
            customer_name = provider_accessor.get_customer_name()
            provider_type = provider_accessor.get_type()
            schema_name = provider_accessor.get_schema()
            account = {'authentication': auth_credential,
                       'billing_source': billing_source,
                       'customer': customer_name,
                       'provider': provider_type,
                       'schema': schema_name}
            accounts.append(account)
        return accounts

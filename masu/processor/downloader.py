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

from masu.config import Config
from masu.exceptions import MasuProviderError
from masu.providers.aws.downloader import AWSReportDownloader


# pylint: disable=too-few-public-methods, too-many-arguments, fixme
class ReportDownloader:
    """Top-level interface for masu to use for downloading reports."""

    # FIXME: this class interface will change once we teach it how to properly
    # introspect into the provider-specific Downloader objects

    def __init__(self, customer_name, access_credential, report_source, provider_type,
                 report_name=None):
        """Set the downloader based on the backend cloud provider."""
        self.customer_name = customer_name
        self.credential = access_credential
        self.report_source = report_source
        self.report_name = report_name
        self.provider_type = provider_type
        try:
            self._downloader = self._set_downloader()
        except Exception as err:
            raise MasuProviderError(str(err))

        if not self._downloader:
            raise MasuProviderError('Invalid provider type specified.')

    def _set_downloader(self):
        """
        Create the report downloader object.

        Downloader is specific to the provider's cloud service.

        Args:
            None

        Returns:
            (Object) : Some object that is a child of CURAccountsInterface

        """
        if self.provider_type == Config.AMAZON_WEB_SERVICES:
            return AWSReportDownloader(customer_name=self.customer_name,
                                       auth_credential=self.credential,
                                       bucket=self.report_source,
                                       report_name=self.report_name)

        return None

    def get_current_report(self):
        """
        Download the current cost usage report.

        Args:
            None

        Returns:
            (List) List of filenames downloaded.

        """
        return self._downloader.download_current_report()

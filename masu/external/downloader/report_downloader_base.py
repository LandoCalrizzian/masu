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
"""Report Downloader."""
from tempfile import mkdtemp


# pylint: disable=too-few-public-methods
class ReportDownloaderBase():
    """
    Download cost reports from a provider.

    Base object class for downloading cost reports from a cloud provider.
    """

    def __init__(self, download_path=None, provider_id=None):
        """
        Create a downloader.

        Args:
            download_path (String) filesystem path to store downloaded files
            provider_id (Int) reference ID of provider in Koku database
        """
        self.download_path = download_path if download_path else mkdtemp(prefix='masu')
        self.provider_id = provider_id if provider_id else None

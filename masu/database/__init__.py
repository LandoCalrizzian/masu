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
"""Database subpackage."""

AWS_CUR_TABLE_MAP = {
    'cost_entry': 'reporting_awscostentry',
    'bill': 'reporting_awscostentrybill',
    'line_item': 'reporting_awscostentrylineitem',
    'line_item_daily': 'reporting_awscostentrylineitem_daily',
    'line_item_daily_summary': 'reporting_awscostentrylineitem_daily_summary',
    'line_item_aggregates': 'reporting_awscostentrylineitem_aggregates',
    'product': 'reporting_awscostentryproduct',
    'pricing': 'reporting_awscostentrypricing',
    'reservation': 'reporting_awscostentryreservation',
}

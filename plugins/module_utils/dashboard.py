class DashboardMixin(object):
    """ Mixin for zabbix_dashboard and zabbix_dashboard_info. """

    def dashboard_id(self, name):
        result = self._zapi.dashboard.get({
            'filter': {'name': name},
            'output': ('dashboardid', )
        })

        return result and result[0]['dashboardid'] or None

    def dashboard(self, id):
        data = self._zapi.dashboard.get({
            'dashboardids': [id],
            'selectPages': 'extend',
            'selectUsers': 'extend',
            'selectUserGroups': 'extend',
        })[0]

        # Exclude instance-specific information
        data.pop('dashboardid')
        data.pop('uuid')

        for page in data['pages']:
            page.pop('dashboard_pageid')

            for widget in page['widgets']:
                widget.pop('widgetid')

        # The name is not included, as it is defined by the task
        data.pop('name')

        return data

    def exists(self, name):
        return self.dashboard_id(name) and True or False

#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2013-2014, Epic Games, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: zabbix_dashboard
short_description: Import Zabbix dashboards.
description:
    - See zabbix.community.zabbix_dashboard_info for the export part.
author:
    - "Denis Krienbühl (@href)"
requirements:
    - "python >= 2.6"
    - "zabbix-api >= 0.5.4"
options:
    name:
        description:
            - The name of the dashboard to import
        type: str
        required: true
    content:
        description:
            - The yaml or json data to import
        type: str
        required: true

extends_documentation_fragment:
- community.zabbix.zabbix

Note:
    Dashboards are currently updated by replacing them entirely
    (delete/create), which is easier to implement but changes all the
    dashboard IDs
'''

EXAMPLES = r'''
- name: Import Zabbix dashboard
  local_action:
    module: community.zabbix.zabbix_dashboard
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    dashboard: System Health
    content: lookup('file', 'system-health.yml')
  register: template_yaml
'''
import ansible_collections.community.zabbix.plugins.module_utils.helpers as zabbix_utils
import yaml

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.zabbix.plugins.module_utils.base import ZabbixBase
from ansible_collections.community.zabbix.plugins.module_utils.dashboard import DashboardMixin


class Dashboard(ZabbixBase, DashboardMixin):

    def load(self, content):
        if hasattr(yaml, 'safe_load'):
            load = yaml.safe_load
        else:
            load = yaml.load

        return load(content)

    def ensure(self, name, content):
        dashboard = self.load(content)
        dashboard_id = self.dashboard_id(name)

        if dashboard_id is None:
            if self._module.check_mode:
                self._module.exit_json(changed=True, diff={
                    'before': {},
                    'after': dashboard,
                })

            dashboard['name'] = name

            self._zapi.dashboard.create(dashboard)
            return True

        existing = self.dashboard(dashboard_id)

        if existing == dashboard:
            return False

        if self._module.check_mode:
            self._module.exit_json(changed=True, diff={
                'before': existing,
                'after': dashboard,
            })

        # To update, delete all pages, then recreate them
        self._zapi.dashboard.update({
            'dashboardid': dashboard_id,
            'pages': [{}],
        })

        dashboard['name'] = name
        dashboard['dashboardid'] = dashboard_id

        self._zapi.dashboard.update(dashboard)
        return True


def main():
    argument_spec = zabbix_utils.zabbix_common_argument_spec()
    argument_spec.update(dict(
        name=dict(type='str', required=True),
        content=dict(type='str', required=True)
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    dashboard = Dashboard(module)

    if dashboard.ensure(module.params['name'], module.params['content']):
        module.exit_json(changed=True)
    else:
        module.exit_json(changed=False)


if __name__ == "__main__":
    main()

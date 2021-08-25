#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2013-2014, Epic Games, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: zabbix_dashboard_info
short_description: Export Zabbix dashboards.
description:
    - The resulting YAML is a custom export that can be used to create a new
      dashboard using community.zabbix.zabbix_dashboard
author:
    - "Denis Krienbühl (@href)"
requirements:
    - "python >= 2.6"
    - "zabbix-api >= 0.5.4"
options:
    name:
        description:
            - The name of the dashboard to export
        type: str
        required: true
    format:
        description:
            - The export format
        type: str
        choices:
            - json
            - yaml
        required: true

extends_documentation_fragment:
- community.zabbix.zabbix
'''

EXAMPLES = r'''
# Create/update a screen.
- name: Export Zabbix dashboard
  local_action:
    module: community.zabbix.zabbix_dashboard_info
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    dashboard: System Health
    format: yaml
  register: template_yaml
'''
import ansible_collections.community.zabbix.plugins.module_utils.helpers as zabbix_utils
import json
import yaml

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.zabbix.plugins.module_utils.base import ZabbixBase
from ansible_collections.community.zabbix.plugins.module_utils.dashboard import DashboardMixin


def is_sort_keys_supported():
    """ Returns True if `sort_keys` is supported in the given yaml version. """

    if not hasattr(yaml, '__version__'):
        return False

    major, minor, patch = yaml.__version__.split('.')

    return int(major) >= 5 and int(minor) >= 1


class DashboardInfo(ZabbixBase, DashboardMixin):

    def export(self, id, format):
        data = self.dashboard(id)

        if format == 'yaml':
            if is_sort_keys_supported():
                params = {'sort_keys': False}
            else:
                params = {}

            return yaml.dump(data, **params)

        if format == 'json':
            return json.dumps(data, indent=4, sort_keys=False)

        raise NotImplementedError("Unsupported format: %s" % format)


def main():
    argument_spec = zabbix_utils.zabbix_common_argument_spec()
    argument_spec.update(dict(
        name=dict(type='str', required=True),
        format=dict(type='str', choices=['json', 'yaml'])
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False
    )

    info = DashboardInfo(module)

    dashboard_id = info.dashboard_id(module.params['name'])

    if dashboard_id is None:
        module.fail_json(msg='Dashboard not found: %s' % module.params['name'])

    export = info.export(dashboard_id, module.params['format'])
    module.exit_json(changed=False, export=export)


if __name__ == "__main__":
    main()

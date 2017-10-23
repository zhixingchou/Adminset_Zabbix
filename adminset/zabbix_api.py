# coding:utf8

from zabbix_client import ZabbixServerProxy
import json, traceback
import db, util, os
import zabbix_api


class Zabbix():
    def __init__(self, data):
        self.zb = ZabbixServerProxy(data['zabbix_url'])
        self.zb.user.login(user=data['zabbix_user'], password=data['zabbix_password'])

    def get_hosts(self):
        return self.zb.host.get(output=['hostid', 'host'])

    def get_host_tem(self):
        data = {
            "output": ["hostid", "name"],
            "selectParentTemplates": ["templateid", "name"]
        }
        ret = self.zb.host.get(**data)
        return ret

    def get_interface(self, hostids):
        data = self.zb.hostinterface.get(hostids=hostids, output=['hostid', 'ip'])
        ret = {}
        for d in data:
            ret[d['hostid']] = d['ip']
        return ret

    def get_hostgroup(self):
        return self.zb.hostgroup.get(output=['groupid', 'name'])

    def create_host(self, params):
        return self.zb.host.create(**params)

    def get_template(self):
        ret = self.zb.template.get(output=["templateid", "name"])
        return ret

    def link_template(self, hostid, templateids):
        data = {
            "hostid": hostid,
            "templates": templateids
        }
        ret = self.zb.host.update(data)
        return ret

    def unlink_template(self, hostid, templateid):
        return self.zb.host.update(hostid=hostid, templates_clear=[{"templateid": templateid}])

    def create_maintenance(self, params):
        return self.zb.maintenance.create(**params)

    def get_maintenance(self):
        data = {
            "output": "extend",
            "selectHosts": ["name"]
        }
        ret = self.zb.maintenance.get(**data)
        return ret

    def del_maintenance(self, maintenanceids):
        return self.zb.maintenance.delete(maintenanceids)

    def get_trigger(self, params):
        return self.zb.trigger.get(**params)

    def get_alerts(self, params):
        return self.zb.alert.get(**params)

    def host_status(self, hostid, status):
        return self.zb.host.update(hostid=hostid, status=status)

    def hostid_get_template(self, hostids):
        data = {
            "output": ["hostid"],
            "selectParentTemplates": ["templateid"],
            "hostids": hostids
        }

        return self.zb.host.get(**data)

    def get_graphid(self, hostid):
        data = {
                "output": ["graphid", "name"],
                "selectGraphs": ["graphid","name"],
                # "selectGraphs": ["extend"],
                "filter": {"hostid": hostid}
                }

        # ret = self.zb.host.get(**data)
        ret = self.zb.host.get(**data)
        # 测试 by zhouzx
        # util.write_log('api').debug('zabbix graph all %s' % ret)
        # util.write_log('api').debug('zabbix graph %s' % ret[0])
        return ret[0]['graphs']


# zabbix_server = Zabbix("http://192.168.63.233/zabbix","Admin","zabbix")


def init():
    # app.config['cursor'].execute_clean_sql('zbhost')
    work_dir = os.path.dirname(os.path.realpath(__file__))
    db.Cursor(util.get_config(os.path.join(work_dir, 'service.conf'), 'api')).execute_clean_sql('zbhost')
    init_zabbix()
    init_cmdb()


def init_cmdb():
    try:
        # 取host (在cmdb_host表里)
        # fields = ['id', 'hostname', 'ip', 'vm_status', 'st', 'uuid', 'manufacturers', 'server_type', 'server_cpu', 'os',
        #           'server_disk', 'server_mem', 'mac_address', 'manufacture_date', 'check_update_time', 'server_purpose',
        #           'server_run', 'expire', 'server_up_time']
        fields = ['id','hostname','ip']

        # 将角色对应的p_id都转为name,最终返回的结果p_id的值都是name
        hosts = db.Cursor(util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'),
                                          'api')).get_results('cmdb_host', fields)
        for h in hosts:
            data = {'cmdb_hostid': h['id']}
            where = {'ip': h['ip']}
            result = db.Cursor(
                util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'),
                                'api')).execute_update_sql('zbhost', data, where)
    # 更新到cache表， ip
    except:
        return ""


def init_zabbix():
    try:
        # 第一步 取出所有host,要ip,host,id
        # zb_hosts = app.config['zabbix'].get_hosts()
        zb_hosts = zabbix_api.Zabbix(
            util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'),
                            'zabbix')).get_hosts()
        zb_hosts_interface = zabbix_api.Zabbix(
            util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'),
                            'zabbix')).get_interface([z['hostid'] for z in zb_hosts])
        data = []
        ret = []
        for h in zb_hosts:
            h['ip'] = zb_hosts_interface[h['hostid']]
            data.append(h)
            ###数据插入数据库
        for i in data:
            result = db.Cursor(
                util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'),
                                'api')).execute_insert_sql('zbhost', i)

    except:
        return ""

def create_zabbix_host(hostid, groupid):
        ret = []
        for host in hostid:
            data = {
                "host": host,
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": host,
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": [
                    {
                        "groupid": groupid
                    }
                ]
            }
            ret.append(zabbix_api.Zabbix(
            util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'),
                            'zabbix')).create_host(data))
        return ret

def create_maintenance(name, start, stop, hostids, time):
        data = {
            "name": name,
            "active_since": start,
            "active_till": stop,
            "hostids": hostids,
            "timeperiods": [
                {
                    "timeperiod_type": 0,
                    "period": time
                }
            ]
        }
        ret = zabbix_api.Zabbix(
            util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'),
                            'zabbix')).create_maintenance(data)
        return ret

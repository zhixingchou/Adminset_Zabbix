#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import redirect
from jsonrpc import jsonrpc_method
from jsonrpc.proxy import ServiceProxy
from . import zabbix_api
import util
import os, json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import datetime

from zabbix_api import *
from zabbix_Graph_api import *


def index(request):
    return redirect('/navi/')


# zabbix api -- by zhouzx

def listapi(request):
    method = request.GET.get('method')
    # zbhost_allhost_getlist = method + ".getlist"
    # s = ServiceProxy('http://192.168.2.159:8400/json/')
    # data = s.zbhost_allhost.getlist()
    # print data
    print method
    if method == "zbhost_allhost":
        s = ServiceProxy('http://192.168.2.159:8000/json/')
        data = s.zbhost_allhost.getlist()
        print json.dumps(data)
        print type(json.dumps(data))
        # print ServiceProxy('http://192.168.2.159:8400/json/').zbhost_allhost.getlist()
        return HttpResponse(json.dumps(data), content_type='application/json; charset=utf-8')
    elif method == "zabbix_gettem":
        s = ServiceProxy('http://192.168.2.159:8000/json/')
        tem = s.zabbix_gettem.getlist()
        return HttpResponse(json.dumps(tem), content_type='application/json; charset=utf-8')
    elif method == "zabbix_tem":
        s = ServiceProxy('http://192.168.2.159:8000/json/')
        host_tem = s.zabbix_tem.getlist()
        return HttpResponse(json.dumps(host_tem), content_type='application/json; charset=utf-8')
    elif method == "zbhost":
        s = ServiceProxy('http://192.168.2.159:8000/json/')
        zbhost = s.zbhost.getlist()
        return HttpResponse(json.dumps(zbhost), content_type='application/json; charset=utf-8')
    elif method == "zabbix":
        s = ServiceProxy('http://192.168.2.159:8000/json/')
        zabbixhost = s.zabbix.getlist()
        return HttpResponse(json.dumps(zabbixhost), content_type='application/json; charset=utf-8')
    else:
        data = {
            u'result': u'{"code": 1, "result": [{"host": "Zabbix server", "hostid": "10084"}, {"host": "192.168.2.159", "hostid": "10107"}]}',
            u'jsonrpc': u'1.0', u'id': u'48e8787a-ad68-11e7-be94-000c29a6a1c8', u'error': None}
        data1 = json.dumps(data)
        type(data1)
        return HttpResponse(json.dumps(data))




def getapi(request):
    method = request.GET.get('method')
    print method
    data = {}
    data['method'] =  method + '.get'
    data['params'] = {
        "m_table":request.GET.get('m_table',None),
        'field': request.GET.get('field', None),
        's_table': request.GET.get('s_table', None),
        'where': {'id': int(request.GET.get('id'))}
    }
    if method == "graph":
        s = ServiceProxy('http://192.168.2.159:8000/json/')
        zbx_graph = s.graph.get(data)
        return HttpResponse(json.dumps(zbx_graph))


@csrf_exempt
def zabbixapi(request):
    method = request.POST.get('method')
    hostids = request.POST.get('hostids')
    groupid = request.POST.get('groupid')
    data = {}
    data['method'] = 'zabbix.' + method
    data['params'] = {
        "hostids": hostids,
        "groupid": groupid
    }
    # method = request.POST.get('method')
    print data['method']
    if data['method'] == "zabbix.link_tem":
        s = ServiceProxy('http://192.168.2.159:8000/json/')
        link_tem = s.zabbix.link_tem(data)
        return HttpResponse(json.dumps(link_tem))
    elif data['method'] == "zabbix.add":
        s = ServiceProxy('http://192.168.2.159:8000/json/')
        create_zbx_host = s.zabbix.add(data)
        return HttpResponse(json.dumps(create_zbx_host))


@csrf_exempt
def zabbix_template(request):
    method = request.POST.get('method')
    hostid = request.POST.get('hostid')
    templateid = request.POST.get('templateid')
    data = {}
    data['method'] = 'zabbix_template.' + method
    data['params'] = {
        "hostids": hostid,
        "templateid": templateid
    }
    # method = request.POST.get('method')
    print data['method']
    if data['method'] == "zabbix_template.unlink_tem":
        s = ServiceProxy('http://192.168.2.159:8000/json/')
        unlink_tem = s.zabbix_template.unlink_tem(data)
        return HttpResponse(json.dumps(unlink_tem))





@jsonrpc_method('graph.get')
def graph_get(request, arg1):
    ret = []
    stime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    data_where = {}
    # add centos7 "Network traffic on ens33"
    monitor_name = ["CPU load", "CPU utilization", "Memory usage", "Disk space usage /", "Network traffic on eth0",
                    "Network traffic on em1", "Network traffic on ens33"]
    output = ['id', 'hostid']
    data = arg1['params']
    # util.write_log('api').debug('data %s' % data)
    # {u'field': None, u'm_table': None, u'where': {u'id': 33}, u's_table': None}
    fields = data.get('output', output)  # Python 字典(Dictionary) get() 函数返回指定键的值，如果值不在字典中返回默认值。
    where = data.get('where', None)
    data_where['cmdb_hostid'] = where['id']
    if not where:
        return json.dumps({'code': 1, 'errmsg': 'must need a condition'})
    # util.graph_file(app.config['zabbix_img_url'])
    util.graph_file(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../static/zabbix'))
    result = db.Cursor( util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'), 'api')).get_one_result('zbhost', fields,
                                                 data_where)  # SELECT id,hostid FROM zbhost WHERE cmdb_hostid=33
    # util.write_log('api').debug('result is: %s' % result)
    grapsh_id = zabbix_api.Zabbix( util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'), 'zabbix')).get_graphid(str(result['hostid']))
    # grapsh_id = app.config['zabbix'].get_graphid("10107")
    for i in grapsh_id:
        if i['name'] in monitor_name:
            # util.write_log('api').debug('stime: %s' % stime)
            values = {"graphid": str(i['graphid']), "stime": stime, "period": 3600, "width": 800, "height": 200}
            graph = ZabbixGraph("http://192.168.2.22:6080/index.php", "Admin",
                                "zabbix")
            ret_data = graph.GetGraph("http://192.168.2.22:6080/chart2.php", values, os.path.join(os.path.dirname(os.path.realpath(__file__)),'../static/zabbix'))
            ret.append(ret_data)
    img_url = util.graph_img(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../static/zabbix'))
    return json.dumps({'code': 0, 'result': img_url})



@jsonrpc_method('zabbix.add')
def zabbix_add(request, arg1):
    data = arg1['params']
    hosts = data['hostids'].split(",")
    result = create_zabbix_host(hosts, data['groupid'])
    return json.dumps({'code': 0, 'result': 'create zabbix host %s scucess' % result[0]['hostids']})


@jsonrpc_method('zabbix.getlist')
def zabbix_select(request):
    hostgroup = zabbix_api.Zabbix(
            util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'),'zabbix')).get_hostgroup()
    return json.dumps({'code': 0, 'result': hostgroup})



@jsonrpc_method('zbhost.getlist')
def zbhost_select(request):
    datadict = {}
    ret = []

    # zbhost表关联cmdb_host by zhoux
    init()
    # update by zhouzx (delete 字段 host)
    fields = ['id', 'cmdb_hostid', 'hostid', 'host', 'ip']
    zabbix_hosts = db.Cursor(util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'),'api')).get_results('zbhost', fields)
    hostid = [str(zb["cmdb_hostid"]) for zb in zabbix_hosts]
    server_hosts = db.Cursor(util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'),'api')).get_results('cmdb_host', ["id"])
    for i in server_hosts:
        if str(i["id"]) not in hostid:
            datadict["id"] = i["id"]
            # all_host = app.config['cursor'].get_results('cmdb_host',["ip"],datadict)
            get_ip = db.Cursor(util.get_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'service.conf'),'api')).get_where_results('cmdb_host', ["id", "ip"], datadict)
            ret.append(get_ip[0])



    return json.dumps({'code': 0, 'result': ret})


@jsonrpc_method('zabbix_template.unlink_tem')
def zabbix_unlink_tem(request, arg1):
    work_dir = os.path.dirname(os.path.realpath(__file__))
    service_conf = os.path.join(work_dir, 'service.conf')
    zabbix_config = util.get_config(service_conf, 'zabbix')
    result = []
    data = arg1['params']
    print data

    data_host = data['hostids'].split(',')
    for i in data_host:
        result.append(zabbix_api.Zabbix(zabbix_config).unlink_template(int(i), data['templateid']))
    return json.dumps({'code': 0, 'result': result})


@jsonrpc_method('zabbix.link_tem')
def zabbix_link_tem(request, arg1):
    work_dir = os.path.dirname(os.path.realpath(__file__))
    service_conf = os.path.join(work_dir, 'service.conf')
    zabbix_config = util.get_config(service_conf, 'zabbix')
    result = []
    tem = []
    template = {}

    data = arg1['params']
    print data
    #       {u'hostids': [u'10157,10158'], u'groupid': u'10001'}
    data_host = data['hostids'].split(',')
    print data_host
    for i in data_host:
        if len(zabbix_api.Zabbix(zabbix_config).hostid_get_template(i)[0]['parentTemplates']) == 0:
            result.append(zabbix_api.Zabbix(zabbix_config).link_template(int(i), data['groupid']))
        else:
            template['templateid'] = data['groupid']
            data_mu = zabbix_api.Zabbix(zabbix_config).hostid_get_template(i)[0]['parentTemplates']
            data_mu.append(template)
            result.append(zabbix_api.Zabbix(zabbix_config).link_template(int(i), data_mu))
    return json.dumps({'code': 0, 'result': result})


@jsonrpc_method('zbhost_allhost.getlist')
def zbhost_allhost_select(request):
    work_dir = os.path.dirname(os.path.realpath(__file__))
    service_conf = os.path.join(work_dir, 'service.conf')
    zabbix_config = util.get_config(service_conf, 'zabbix')
    data = zabbix_api.Zabbix(zabbix_config).get_hosts()
    print json.dumps({'code': 0, 'result': data})
    return json.dumps({'code': 0, 'result': data})


@jsonrpc_method('zabbix_gettem.getlist')
def zabbix_gettem_select(request):
    work_dir = os.path.dirname(os.path.realpath(__file__))
    service_conf = os.path.join(work_dir, 'service.conf')
    zabbix_config = util.get_config(service_conf, 'zabbix')
    tem = zabbix_api.Zabbix(zabbix_config).get_template()
    print json.dumps({'code': 0, 'result': tem})
    return json.dumps({'code': 0, 'result': tem})


@jsonrpc_method('zabbix_tem.getlist')
def zabbix_gettem_select(request):
    work_dir = os.path.dirname(os.path.realpath(__file__))
    service_conf = os.path.join(work_dir, 'service.conf')
    zabbix_config = util.get_config(service_conf, 'zabbix')
    tem = zabbix_api.Zabbix(zabbix_config).get_host_tem()
    print json.dumps({'code': 0, 'result': tem})
    return json.dumps({'code': 0, 'result': tem})


@jsonrpc_method('myapp.sayHello')
def whats_the_time(request, name='Lester'):
    return "Hello %s" % name


@jsonrpc_method('myapp.gimmeThat', authenticated=True)
def something_special(request, secret_data):
    return {'sauce': ['authenticated', 'sauce']}

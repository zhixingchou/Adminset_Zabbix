# 开源自动化平台Adminset集成roncoo-cmdb

1、https://github.com/guohongze/adminset 先安装adminset

2、安装开源django jsonrpc
https://github.com/samuraisam/django-json-rpc

    Install django-json-rpc
    git clone git://github.com/samuraisam/django-json-rpc.git
    cd django-json-rpc
    python setup.py install

    # Add 'jsonrpc' to your INSTALLED_APPS in your settings.py file

3、集成roncoo-cmdb的ZABBIX https://github.com/roncoo/roncoo-cmdb

新增一下文件：
main/db.py
main/zabbix_Graph_api.py
main/zabbix_api.py
main/util.py
main/service.conf   【根据自己配置修改mysql,zabbix配置】
修改的文件：
main/urls.py
main/views.py

使用本项目的static目录覆盖adminset的static目录；

template/cmdb/index.html 覆盖
link_css.html 添加有说明
head_script.html 添加有说明
base.html 添加有说明

template/monitor目录新增template_zhouzx.html


main/monitor新增：
template_zhouzx.py

main/monitor更改：
urls.py --> url(r'^template/$', template_zhouzx.index, name='zbx_template'),










## 一、绑定、取消ZABBIX模板

![](https://i.imgur.com/4aEEwnv.png)



## 二、绑定Adminset CMDB主机到ZABBIX监控主机组

![](https://i.imgur.com/WmBoqHQ.png)

## 三、点击【监控】按钮查看主机的基础监控项图形

![](https://i.imgur.com/qgmTSBP.png)

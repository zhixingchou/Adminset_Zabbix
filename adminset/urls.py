from django.conf.urls import include,url
from django.contrib import admin
from django.conf import settings
import views
from jsonrpc import jsonrpc_site

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^cmdb/', include('cmdb.urls')),
    url(r'^navi/', include('navi.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^setup/', include('setup.urls')),
    url(r'^monitor/', include('monitor.urls')),
    url(r'^config/', include('config.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^appconf/', include('appconf.urls')),
    # zabbix api -- add templates -- by zhouzx
    url(r'^admin/', admin.site.urls),
    # url(r'^monitor$', views.monitor),
    url(r'^listapi', views.listapi),
    url(r'^zabbixapi', views.zabbixapi),
    url(r'^zabbix_template', views.zabbix_template),
    # zabbix api -- add asset to zabbix -- by zhouzx
    # zabbix api -- zbx monitor views -- by zhouzx
    url(r'^getapi', views.getapi),
    # django jsonrpc
    url(r'^json/browse/', 'jsonrpc.views.browse', name="jsonrpc_browser"),
    # for the graphical browser/web console only, omissible
    url(r'^json/', jsonrpc_site.dispatch, name="jsonrpc_mountpoint"),
    url(r'^json/(?P<method>[a-zA-Z0-9.]+)$', jsonrpc_site.dispatch)  # for HTTP GET only, also omissible
]
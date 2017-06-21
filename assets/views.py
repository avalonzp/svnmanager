# -*- coding: UTF-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from controller.public.pagination import *
from controller.core.ansiblehelp import *
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from models import *
import json
# Create your views here.

PAGE_SIZE = 10  # 每页显示条数
current_page_total = 10  # 分页下标


@login_required
def index(request):
    #  服务器列表
    project_name = request.GET.get('project_name', '')
    in_ip = request.GET.get('in_ip', '')
    position = request.GET.get('position', '')
    service = request.GET.get('service', '')
    host_name = request.GET.get('host_name', '')
    status = request.GET.get('status', '')

    # 设置查询条件
    filters = {}
    if project_name:
        filters['project_name__icontains'] = project_name
    if in_ip:
        filters['in_ip__icontains'] = in_ip
    if position:
        filters['position__icontains'] = position
    if host_name:
        filters['host_name__icontains'] = host_name
    if status:
        filters['status'] = True if status == "UP" else False

    page_num = int(request.GET.get('p', 1))  # 页码
    servers = Server.objects.filter(**filters)

    if service:  # 服务名或端口查询
        Q_like = Q(service_name=service) | Q(port=service)
        services = Service.objects.filter(Q_like)
        svcs = [svc.server for svc in services]
        new_servers = []
        # 比较服务器列表里的服务器实例和服务表里服务器外键（也就是服务器实例）
        for svr in servers:
            if svr in svcs:
                new_servers.append(svr)
        servers = new_servers

    paginator = Paginator_help(page_num, servers, PAGE_SIZE, current_page_total, request)

    # 重置当前页面列表对象
    app = []
    for obj in paginator.current_page.object_list:
        services = Service.objects.filter(server=obj)
        setattr(obj, 'services', services)
        app.append(obj)

    paginator.current_page.object_list = app
    return render(request,'cmdb/index.html',locals())
    #return HttpResponse("ok")




def server_add_page(request):
    # 新增机器页面
    return render(request,'cmdb/server_add.html', locals())




def server_add(request):
    # 新增机器
    response = HttpResponse()
    data = json.loads(request.GET.get('data', ''))

    server = Server()
    server.project_name = data['project_name']
    server.in_ip = data['in_ip']
    server.ex_ip = data['ex_ip']
    server.position = data['position']
    server.save()

    response.write(json.dumps(u'成功'))
    return response



def server_edit_page(request, id):
    # 编辑机器页面
    server = Server.objects.get(pk=id)
    return render(request,'cmdb/server_edit.html', locals())


def server_edit(request):
    # 编辑机器
    response = HttpResponse()
    data = json.loads(request.GET.get('data', ''))

    print data
    for i in data:
        print i, data[i]
    id = data['id']
    project_name = data['project_name']
    position = data['position']
    in_ip = data['in_ip']
    ex_ip = data['ex_ip']

    server = Server.objects.get(pk=id)
    server.project_name = project_name
    server.position = position
    server.in_ip = in_ip
    server.ex_ip = ex_ip
    server.save()

    response.write(json.dumps(u'成功'))
    return response




@login_required
def postmachineinfo(request):
    # 提交服务器信息
    response = HttpResponse()
    data = json.loads(request.GET.get('data', ''))
    id = int(data['id'])
    print 'update--->'
    server = Server.objects.get(pk=id)
    data = get_info(server.in_ip)
    server.os_version = data['sysinfo']
    server.host_name = data['host_name']
    server.os_kernel = data['os_kernel']
    server.cpu_model = data['cpu']
    server.cpu_count = data['cpu_count']
    server.cpu_cores = data['cpu_cores']
    server.mem = data['mem']
    server.disk = data['disk']
    server.status = True
    server.max_open_files = get_ulimit(server.in_ip)
    server.uptime = get_uptime(server.in_ip)
    server.save()

    # set_service_port(server)  # 设置服务端口信息
    response.write(json.dumps(u'成功'))
    return response


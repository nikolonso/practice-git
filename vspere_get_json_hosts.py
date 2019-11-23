#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pyVmomi import vim
from pyVim import connect
import json
from threading import Thread
import datetime

config_vcenter = 'vcenter.json'
out = {}

def Json_Parser(config_file):
    """ Json parser config (config_vcenter, config_network """
    config = json.loads(open(config_file).read())
    return config

def Connect_vCenter(vcenter_host):
    """ connect vcenter  """
    try:
        si = connect.SmartConnectNoSSL(host=vcenter_host, user=Json_Parser(config_vcenter)[vcenter_host][0],
                               pwd=Json_Parser(config_vcenter)[vcenter_host][1], port=443)
        content = si.RetrieveContent()
        return content
    except:
        print('Error connect: '+ vcenter_host)

def esxi_list(host, content):
    d = {}
    try:
        summary = host.summary
        stats = summary.quickStats
        hardware = host.hardware
        d.update({'HostName': host.name})
        d.update({'ClusterName': cluster_name(host)})
        d.update({'CpuUsage' : stats.overallCpuUsage})
        d.update({'MemoryUsage' : stats.overallMemoryUsage})
        d.update({'Ph_face': pnics(host)})
        d.update({'vmknic': vmknic(host)})
        d.update({'platform': platform(host)})
        d.update({'stats': State(host)})
        d.update({'LocalStore': localstore(host)})
        d.update({'MultiStore': MultiPathstore(host)})
        d.update({'Datacenter': folder_dict(host)[len(folder_dict(host)) - 1]})
        d.update({'vcenter': vcenterfqdn(content)})
        out.update({host.name: d})
        print(d)
    except Exception as error:
        print("Unable to access information for host: ", host.name)
        print(error)
        pass


def cluster_name(host):
    if host.parent.name != host.name:
        return host.parent.name
    else:
        pass



def pnics(host):

    cdp_vnic = {}
    vnic_list = {}
    network_info = host.configManager.networkSystem.networkInfo
    cdp_all = host.configManager.networkSystem.QueryNetworkHint()
    for c in range(0, len(network_info.pnic)):
        esxi_network = {}
        try:
            esxi_network.update({'speed': network_info.pnic[c].linkSpeed.speedMb})
            esxi_network.update({'mac': network_info.pnic[c].mac})
            vnic_list.update({network_info.pnic[c].device : esxi_network})
        except:
            pass


    for i in range(0, len(cdp_all)):
        cdp_list = {}
        try:
            cdp_list.update({'devId': cdp_all[i].connectedSwitchPort.devId})
            cdp_list.update({'portId': cdp_all[i].connectedSwitchPort.portId})
            cdp_list.update({'hardwarePlatform': cdp_all[i].connectedSwitchPort.hardwarePlatform})
            cdp_list.update({'mgmtAddr': cdp_all[i].connectedSwitchPort.mgmtAddr})
            cdp_vnic.update({cdp_all[i].device: cdp_list})
        except:
            pass

        for i in cdp_vnic:
            vnic_list[i].update(cdp_vnic[i])

    return vnic_list



def vmknic(host):
    vmknic_all = {}
    network_info = host.configManager.networkSystem.networkInfo.vnic
    try:
        for i in range(0, len(network_info)):
            vmk_dict = {}
            vmk_dict.update({'Ip': network_info[i].spec.ip.ipAddress })
            vmk_dict.update({'Mask': network_info[i].spec.ip.subnetMask})
            vmk_dict.update({'Mac': network_info[i].spec.mac})
            vmk_dict.update({'MTU': network_info[i].spec.mtu})
            vmknic_all.update({network_info[i].device : vmk_dict})
    except:
        pass
    return vmknic_all

def State(host):
    summary = host.summary
    hardware = host.hardware
    d = {}
    d.update({"Status": summary.runtime.connectionState})
    d.update({"Uptime": round(int(summary.quickStats.uptime) / 60 / 60 / 24)})
    d.update({"UUID": summary.hardware.uuid})
    return d


def platform(host):
    summary = host.summary
    hardware = host.hardware
    d = {}
    d.update({"vendor": summary.hardware.vendor })
    d.update({"model": summary.hardware.model })
    d.update({"cpuModel": summary.hardware.cpuModel})
    try:
        d.update({"bios" : [hardware.biosInfo.releaseDate.strftime("%d.%m.%Y"), hardware.biosInfo.biosVersion]})
    except:
        pass
    d.update({"esxi" : host.config.product.fullName})
    d.update({"Memory": round(hardware.memorySize / 1024 / 1024 / 1024 )})
    d.update({"CPU": summary.hardware.numCpuPkgs})
    d.update({"CpuCores": summary.hardware.numCpuCores})
    d.update({"CpuThreads": summary.hardware.numCpuThreads})
    d.update({"Nics": summary.hardware.numNics})
    return d


def localstore(host):
    lstore = {}
    for i in range(0, len(host.datastore)):
        d = {}
        if host.datastore[i].summary.multipleHostAccess != True:
            d.update({'capacity': host.datastore[i].summary.capacity})
            d.update({'freeSpace': host.datastore[i].summary.freeSpace})
            capacity = round(host.datastore[i].summary.capacity / 1024 / 1024 / 1024)
            freeSpace = round(host.datastore[i].summary.freeSpace / 1024 / 1024 / 1024)
            d.update({'Free%' : round(freeSpace * 100 / capacity)})


            lstore.update({host.datastore[i].name: d})
    return lstore


def MultiPathstore(host):
    lstore = {}
    for i in range(0, len(host.datastore)):
        d = {}
        if host.datastore[i].summary.multipleHostAccess == True:
            d.update({'capacity': host.datastore[i].summary.capacity})
            d.update({'freeSpace': host.datastore[i].summary.freeSpace})
            capacity = round(host.datastore[i].summary.capacity / 1024 / 1024 / 1024)
            freeSpace = round(host.datastore[i].summary.freeSpace / 1024 / 1024 / 1024)
            d.update({'Free%' : round(freeSpace * 100 / capacity)})


            lstore.update({host.datastore[i].name: d})
    return lstore


def folder_dict(host):
    d = {}
    key = 2
    i = host.parent
    d.update({1:i.name})
    while i !=  None:
        if hasattr(host, 'parent'):
            i = i.parent
            try:
                d.update({key: i.name})
                key += 1
            except:
                pass
    return d



def vcenterfqdn(content):
    vcenter_settings = content.setting.setting
    for item in vcenter_settings:
        key = getattr(item, 'key')
        if key == 'VirtualCenter.FQDN':
            vcenter_fqdn = getattr(item, 'value')
            return vcenter_fqdn


def start (vcenter_host):
    content = Connect_vCenter(vcenter_host)
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    for i in range(len(container.view)):
        esxi_list(container.view[i], content)

    return out

def main():
 #  vc_ext = Thread(target=start(vcenter_host='vc-ext.srv.local'))
    vc_linx = Thread(target=start(vcenter_host='vc-linx.srv.local'))
    vcsa = Thread(target=start(vcenter_host='vcsa.srv.local'))
    vc_khut = Thread(target=start(vcenter_host='vc-khut.srv.local'))
    vc1c = Thread(target=start(vcenter_host='vc1c.srv.local'))
#    vc_ext.start()
    vc_linx.start()
    vcsa.start()
    vc_khut.start()
    vc1c.start()
 #   vc_ext.join()
    vc_linx.join()
    vcsa.join()
    vc_khut.join()
    vc1c.join()


main()

with open('esxi.json', 'w') as json_file:
    json.dump(out, json_file)

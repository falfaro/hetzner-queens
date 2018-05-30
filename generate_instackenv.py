#!/usr/bin/python
#
# Copyright(C) 2015 Felipe Alfaro Solana
#
# Python script used to populate 'instackenv.json' file, which describes
# the Ironic nodes used to deploy an OpenStack Overcloud.
#
# This script supports both baremetal nodes and KVM-based virtual machines.

from collections import OrderedDict
from IPy import IP

import json
import netaddr
import os


# Prefix used to generate Overcloud host names.
PREFIX = 'esjc-ost2-'
HOME = os.path.expanduser('~')


class IpmiNode(object):

  def __init__(self, name, ip, port, mac, cpus, memory_mb, local_gb, capabilities,
               root_device=None):
    creds_file = os.path.join(HOME, '.ipmitool_credentials')
    IpmiNode.IPMITOOL_CREDENTIALS = eval(open(creds_file, 'r').read())
    self._name = name
    self._ip = ip
    self._port = port
    self._mac = mac
    self._cpus = cpus
    self._memory_mb = memory_mb
    self._local_gb = local_gb
    self._capabilities = capabilities
    self._root_device = root_device

  def json(self):
    d = {
      'capabilities': self._capabilities,
      'name': self._name,
      'pm_addr': self._ip,
      'pm_port': str(self._port),
      'pm_type': 'pxe_ipmitool',
      'mac': [str(self._mac)],
      'cpu': str(self._cpus),
      'memory': str(self._memory_mb),
      'disk': str(self._local_gb),
      'arch': 'x86_64',
      }

    if self._root_device:
      d.update({'root_device': self._root_device})
    d.update(self.IPMITOOL_CREDENTIALS)

    return d


class KvmNode(object):

  # Read the SSH private key used to connect to QEMU+SSH (to control KVM
  # virtual machines with libvirtd).
  SSH_KEY = '%s/.ssh/id_rsa' % HOME
  with open(SSH_KEY, 'r') as f:
    _ssh_key = ''.join(f.readlines())

  def __init__(self, name, ip, mac, cpus, memory_mb, local_gb, capabilities,
               root_device=None):
    self._name = name
    self._ip = ip
    self._mac = mac
    self._cpus = cpus
    self._memory_mb = memory_mb
    self._local_gb = local_gb
    self._capabilities = capabilities
    self._root_device = root_device

  def json(self):
    d = {
      'capabilities': self._capabilities,
      'name': self._name,
      'pm_addr': self._ip,
      'pm_type': 'pxe_ssh',
      'pm_user': 'falfaro',
      'pm_password': self._ssh_key,
      'mac': [str(self._mac)],
      'cpu': str(self._cpus),
      'memory': str(self._memory_mb),
      'disk': str(self._local_gb),
      'arch': 'x86_64',
      }

    if self._root_device:
      d.update({'root_device': self._root_device})

    return d


class Nodes(object):
  """Represents an Ironic node for the Overcloud."""

  _n = 0
  _nodes = []
  _flavors_to_nodes = {
    'control': 'controller',
    'networker': 'networker',
    'compute': 'compute',
    'ceph-storage': 'cephstorage',
    'swift-storage': 'swiftstorage',
  } 

  @classmethod
  def node_name(cls, profile, index):
    return '%s-%d' % (cls._flavors_to_nodes[profile], index)
 
  @classmethod
  def add(cls, node_class, prefix, profile, **kwargs):
    """Add a new Ironic node."""

    name = '%s%s%dp' % (PREFIX, prefix, cls._n + 1)
    capabilities = {
      'node': cls.node_name(profile=profile, index=cls._n),
      'profile': profile,
      'boot_option': 'local',
      }

    kwargs.update({'name': name})
    kwargs.update({'capabilities': ','.join(
      ['%s:%s' % (key, value) for (key, value) in capabilities.items()])})

    cls._nodes.append(node_class(**kwargs))
    cls._n += 1

  @classmethod
  def json(cls):
    """Generate information about Ironic nodes in JSON."""

    nodes = []
    for node in cls._nodes:
      nodes.append(node.json())
    return nodes


class ControlNodes(Nodes):
  """Controller nodes."""

  @classmethod
  def add(cls, node_class, ip, mac,
          cpus=12, memory_mb=96*1024, local_gb=1024, root_device=None, **kwargs):
    super(cls, ControlNodes).add(
      node_class, 'cc0', 'control',
      ip=ip, mac=mac, cpus=cpus, memory_mb=memory_mb, local_gb=local_gb,
      root_device=root_device, **kwargs)


class NetworkerNodes(Nodes):
  """Networker nodes."""

  @classmethod
  def add(cls, node_class, ip, mac,
          cpus=12, memory_mb=96*1024, local_gb=1024, root_device=None, **kwargs):
    super(cls, NetworkerNodes).add(
      node_class, 'nn0', 'networker',
      ip=ip, mac=mac, cpus=cpus, memory_mb=memory_mb, local_gb=local_gb,
      root_device=root_device, **kwargs)


class ComputeNodes(Nodes):
  """Compute nodes."""

  @classmethod
  def add(cls, node_class, ip, mac,
          cpus=24, memory_mb=256*1024, local_gb=1024, root_device=None, **kwargs):
    super(cls, ComputeNodes).add(
      node_class, 'cn0', 'compute',
      ip=ip, mac=mac, cpus=cpus, memory_mb=memory_mb, local_gb=local_gb,
      root_device=root_device, **kwargs)


class CephNodes(Nodes):
  """Ceph nodes."""

  @classmethod
  def add(cls, node_class, ip, mac,
          cpus=4, memory_mb=32*1024, local_gb=32, root_device=None, **kwargs):
    super(cls, CephNodes).add(
      node_class, 'sn0', 'ceph-storage',
      ip=ip, mac=mac, cpus=cpus, memory_mb=memory_mb, local_gb=local_gb,
      root_device=root_device, **kwargs)


class SwiftNodes(Nodes):
  """Swift nodes."""

  @classmethod
  def add(cls, node_class, ip, mac,
          cpus=2, memory_mb=8*1024, local_gb=32, root_device=None, **kwargs):
    super(cls, SwiftNodes).add(
      node_class, 'sn5', 'swift-storage',
      ip=ip, mac=mac, cpus=cpus, memory_mb=memory_mb, local_gb=local_gb,
      root_device=root_device, **kwargs)


# Controller nodes
ControlNodes.add(IpmiNode, '127.0.0.1', '52:54:00:4b:68:8e', port=6230) # ESJC-OST2-CC01P
ControlNodes.add(IpmiNode, '127.0.0.1', '52:54:00:11:c9:b5', port=6231) # ESJC-OST2-CC02P
ControlNodes.add(IpmiNode, '127.0.0.1', '52:54:00:8b:16:c6', port=6232) # ESJC-OST2-CC03P

# Networker nodes
NetworkerNodes.add(IpmiNode, '127.0.0.1', '52:54:00:7d:53:46', port=6233) # ESJC-OST2-NN01P
NetworkerNodes.add(IpmiNode, '127.0.0.1', '52:54:00:03:32:ef', port=6234) # ESJC-OST2-NN02P
NetworkerNodes.add(IpmiNode, '127.0.0.1', '52:54:00:5d:89:7e', port=6235) # ESJC-OST2-NN03P

# Compute nodes
ComputeNodes.add(IpmiNode, '127.0.0.1', '52:54:00:b3:06:0d', port=6236) # ESJC-OST2-CN01P
ComputeNodes.add(IpmiNode, '127.0.0.1', '52:54:00:e9:b7:5e', port=6237) # ESJC-OST2-CN02P
ComputeNodes.add(IpmiNode, '127.0.0.1', '52:54:00:88:9a:22', port=6238) # ESJC-OST2-CN03P

## Swift nodes
#SwiftNodes.add(KvmNode, '10.2.0.1', '52:54:00:5a:ef:44') # ESJC-OST2-SN51P
#SwiftNodes.add(KvmNode, '10.2.0.1', '52:54:00:99:cf:05') # ESJC-OST2-SN52P
#SwiftNodes.add(KvmNode, '10.2.0.1', '52:54:00:82:5d:80') # ESJC-OST2-SN53P

print (json.dumps({"nodes": Nodes.json()}, sort_keys=True, indent=2))

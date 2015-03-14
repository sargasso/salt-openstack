roles: 
  - "controller"
  - "network"
  - "storage"
  - "compute"
compute: 
  - "helios.juno"
controller: 
  - "ixchel.juno"
network: 
  - "ixchel.juno"
storage:
  - "ixchel.juno"
sls: 
  controller: 
    - "mysql"
    - "mysql.client"
    - "mysql.openstack_dbschema"
    - "queue.rabbit"
    - "keystone"
    - "keystone.openstack_tenants"
    - "keystone.openstack_users"
    - "keystone.openstack_services"
    - "nova"
    - "horizon"
    - "glance"
    - "glance.images"
    - "cinder"
  network: 
    - "mysql.client"
    - "neutron"
    - "neutron.service"
    - "neutron.openvswitch"
    - "neutron.ml2"
    - "neutron.guest_mtu"
    - "neutron.networks"
    - "neutron.routers"
    - "neutron.security_groups"
  compute: 
    - "mysql.client"
    - "nova.compute_kvm"
    - "neutron.openvswitch"
    - "neutron.ml2"
  storage:
    - "cinder.volume"

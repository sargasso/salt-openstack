

__virtualname__ = 'partition_free_disks'

def __virtual__():
    return __virtualname__

def free_disks(unmounted_partitions=True, free_space=True, min_disk_size='10',
               max_disk_size=None):
    """
    Retrieve a list of disk devices that are not active
    do not include unmounted partitions if unmounted_partitions=False
    do not include free spaces if free_space=False
    
    CLI Example:

    .. code-block:: bash

        salt '*' partition.free_disks
    """
    available_disks = []
    if unmounted_partitions:
        available_disks.extend(unmounted_partitions())
    if free_space:
        while find_free_spaces(min_disk_size, max_disk_size):
            __salt__['partition.mkpart'](free_space['device'], 'primary',
                                         start=free_space['start'],
                                         end=free_space['end'])
            __salt__['cmd.run']('partprobe')
            available_disks.append(free_space['device']+free_space['id'])
    return available_disks


def get_block_device():
    '''
    Retrieve a list of disk devices

    .. versionadded:: 2014.7.0

    CLI Example:

    .. code-block:: bash

        salt '*' partition.get_block_device
    '''
    cmd = 'lsblk -n -io KNAME -d -e 1,7,11 -l'
    devs = __salt__['cmd.run'](cmd).splitlines()
    return devs


def unmounted_partitions():
    '''
    Retrieve a list of unmounted partitions

    CLI Example:

    .. code-block:: bash

        salt '*' partition.unmounted_partitions
    '''
    unused_partitions = []
    active_mounts = __salt__['mount.active']()
    mounted_devices = [active_mounts[mount_point]['alt_device'] for mount_point in active_mounts]
    mounted_devices.extend(__salt__['mount.swaps']())
    for block_device in get_block_device():
        device_name = '/dev/%s' % block_device
        part_data = __salt__['partition.part_list'](device_name)
        for partition_id in part_data['partitions']:
            partition_name = device_name + partition_id
            if partition_name not in mounted_devices:
                unused_partitions.append(partition_name)
    return unused_partitions
        


def find_free_spaces(min_disk_size=10, max_disk_size=None):
    '''
    Retrieve a list of free space where partitions can be created
    returns device name, partition id when created, start and end sector
    returns only spaces greated than min_disk_size, which
    defaults to 10, units are in Gigabytes

    CLI Example:

    .. code-block:: bash

        salt '*' partition.find_free_spaces
    '''
    min_disk_size=int(min_disk_size)
    for block_device in get_block_device():
        device_name = '/dev/%s' % block_device
        part_data = __salt__['partition.part_list'](device_name, unit='s')
        sector_size = _sector_to_int(part_data['info']['logical sector'])
        disk_final_sector_int = _sector_to_int(part_data['info']['size'])
        last_device_id, last_allocated_sector_int = _last_allocated_sector(part_data['partitions'])
        disk_size_G = _sector_to_G(disk_final_sector_int-last_allocated_sector_int, sector_size)
        if disk_size_G > min_disk_size:
            start_sector_int = last_allocated_sector_int+1
            if max_disk_size and disk_size_G > max_disk_size:
                end_sector_int = start_sector_int + _G_to_sector(int(max_disk_size)) -1
            else:
                end_sector_int = disk_final_sector_int-1
            return {'device': device_name,
                    'id': str(last_device_id+1),
                    'start': _int_to_sector(start_sector_int),
                    'end': _int_to_sector(end_sector_int)}

def _last_allocated_sector(part_data):
    last_allocated_sector = 2048
    for partition_id, partition_data in part_data.iteritems():
        sector_end_in_int = _sector_to_int(partition_data['end'])
        if sector_end_in_int > last_allocated_sector:
            last_allocated_sector = sector_end_in_int
    return int(partition_id), last_allocated_sector
        
def _sector_to_int(sector):
    if sector[-1] == 's':
        return int(sector[:-1])
    return int(sector)

def _int_to_sector(int_sector):
    return str(int_sector) + 's'

def _G_to_sector(giga_bytes, sector_size):
    return (giga_bytes*1073741824)/sector_size

def _sector_to_G(sector_length, sector_size):
    return (sector_length*sector_size)/1073741824
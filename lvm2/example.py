"""Examples"""

import asyncio
from typing import List

async def run_async(cmd: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if proc.returncode:
        raise Exception(stderr.decode() if stderr else f'[{cmd!r} exited with {proc.returncode}]')

    return stdout.decode()

async def disk_space_usage():
    # cmd = "df --block-size=1K --output='source,fstype,itotal,iused,iavail,ipcent,size,used,avail,pcent,file,target'"
    cmd = "df --block-size=1K --output='size,used,source,target,fstype'"
    text = await run_async(cmd)
    lines: List[str] = text.split('\n')
    header = lines[0]
    size_start = 0
    size_end = header.index('1K-blocks') + len('1K-blocks')
    used_start = size_end + 1
    used_end = header.index('Used') + len('Used')
    source_start = header.index("Filesystem")
    source_end = header.index('Mounted on') - 1
    target_start = source_end + 1
    target_end = header.index('Type') - 1
    type_start = target_end + 1

    usage = []
    for line in lines[1:]:
        if not line:
            continue
        usage.append(dict(
            source = line[source_start:source_end].strip(),
            size = int(line[size_start:size_end].strip()) * 1024,
            used = int(line[used_start:used_end].strip()) * 1024,
            target = line[target_start:target_end].strip(),
            type = line[type_start:].strip()
        ))
    print(usage)
    return usage

async def volume_groups():
    cmd = "vgs -o 'vg_size,vg_free,vg_name' --units b --separator '|'"
    text = await run_async(cmd)
    lines: List[str] = text.split('\n')
    result = []
    for line in lines[1:]:
        if not line:
            continue
        vg_size, vg_free, vg_name = line.split('|')
        result.append(dict(
            vg_name=vg_name.strip(),
            vg_size=int(vg_size.strip()[:-1]),
            vg_free=int(vg_free.strip()[:-1])
        ))
    print(result)
    return result

async def logical_volumes():
    cmd = "lvs -o 'lv_name,vg_name,lv_dm_path,lv_size' --units b --separator '|'"
    text = await run_async(cmd)
    lines: List[str] = text.split('\n')
    result = []
    for line in lines[1:]:
        if not line:
            continue
        lv_name, vg_name, lv_dm_path, lv_size = line.split('|')
        result.append(dict(
            lv_name=lv_name.strip(),
            vg_name=vg_name.strip(),
            lv_dm_path=lv_dm_path.strip(),
            lv_size=int(lv_size.strip()[:-1])
        ))
    print(result)
    return result

async def physical_volumes():
    cmd = "pvs -o 'pv_name,vg_name,pv_size,pv_free' --units b --separator '|'"
    text = await run_async(cmd)
    lines: List[str] = text.split('\n')
    result = []
    for line in lines[1:]:
        if not line:
            continue
        pv_name, vg_name, pv_size, pv_free = line.split('|')
        result.append(dict(
            pv_name=pv_name.strip(),
            vg_name=vg_name.strip(),
            pv_size=int(pv_size.strip()[:-1]),
            pv_free=int(pv_free.strip()[:-1])
        ))
    print(result)
    return result

async def lvm_usage():
    dfs = await disk_space_usage()
    vgs = await volume_groups()
    lvs = await logical_volumes()
    pvs = await physical_volumes()

    usage = {}
    for vg in vgs:
        vg_name = vg['vg_name']
        vg_usage = usage.setdefault(vg_name, {
            'size': vg['vg_size'],
            'free': vg['vg_free'],
        })
        vg_usage['physical'] = {
            pv['pv_name']: dict(
                size=pv['pv_size'],
                free=pv['pv_free']
            )
            for pv in pvs if pv['vg_name'] == vg_name
        }
        vg_usage['logical'] = {
            lv['lv_name']: {
                'dm_path': lv['lv_dm_path'],
                'size': lv['lv_size']
            }
            for lv in lvs
            if lv['vg_name'] == vg_name
        }
        for lv in vg_usage['logical'].values():
            df = next((df for df in dfs if lv['dm_path'] == df['source']), {})
            lv.update({
                'free': lv['size'] - df.get('used', lv['size']),
                'path': df.get('target'),
                'type': df.get('type')
            })
            del lv['dm_path']
    print(usage)
    return usage


    
if __name__ == "__main__":
    # asyncio.run(disk_space_usage())
    # asyncio.run(volume_groups())
    # asyncio.run(logical_volumes())
    # asyncio.run(physical_volumes())
    asyncio.run(lvm_usage())

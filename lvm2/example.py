"""Examples"""

import asyncio
from typing import List

async def disk_space_usage():
    # cmd = "df --block-size=1K --output='source,fstype,itotal,iused,iavail,ipcent,size,used,avail,pcent,file,target'"
    cmd = "df --block-size=1K --output='size,used,source,target'"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if proc.returncode:
        raise Exception(stderr.decode() if stderr else f'[{cmd!r} exited with {proc.returncode}]')

    text = stdout.decode()
    lines: List[str] = text.split('\n')
    header = lines[0]
    size_start = 0
    size_end = header.index('1K-blocks') + len('1K-blocks')
    used_start = size_end + 1
    used_end = header.index('Used') + len('Used')
    source_start = header.index("Filesystem")
    source_end = header.index('Mounted on') - 1
    target_start = source_end + 1

    usage = []
    for line in lines[1:]:
        if not line:
            continue
        usage.append(dict(
            source = line[source_start:source_end].strip(),
            size = int(line[size_start:size_end].strip()),
            used = int(line[used_start:used_end].strip()),
            target = line[target_start:].strip()
        ))
    print(usage)

if __name__ == "__main__":
    asyncio.run(disk_space_usage())

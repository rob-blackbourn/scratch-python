"""A CPU Monitor"""

import asyncio
from typing import Dict, List

import aiofiles

async def _cpu_times() -> List[int]:
    """Return a list of cpu times

    :return: [description]
    :rtype: List[int]
    """
    async with aiofiles.open('/proc/stat') as f:
        line = await f.readline()

    return [int(x) for x in line.split()[1:]]

async def _cpu_time_deltas(sample_duration: float) -> List[int]:
    start_times = await _cpu_times()
    await asyncio.sleep(sample_duration)
    end_times = await _cpu_times()
    return [end - start for start, end in zip(start_times, end_times)]

async def cpu_percents(sample_duration: float = 1.0) -> Dict[str, float]:
    """Return a sample of the cpu
    
    :param sample_duration: The sample duration, defaults to 1.0
    :type sample_duration: float, optional
    :return: A dictionary of the stats
    :rtype: Dict[str, float]
    """ 
    deltas = await _cpu_time_deltas(sample_duration)
    total = sum(deltas)
    percents = [100 - (100 * (float(total - x) / total)) for x in deltas]

    return {
        'user': percents[0],
        'nice': percents[1],
        'system': percents[2],
        'idle': percents[3],
        'iowait': percents[4],
        'irq': percents[5],
        'softirq': percents[6],
        'steal': percents[7],
        'guest': percents[8],
        'nice': percents[9],
    }

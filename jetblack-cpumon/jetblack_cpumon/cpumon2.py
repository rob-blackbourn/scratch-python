"""A CPU Monitor"""

import asyncio
from typing import Dict, List, Optional, Tuple

import aiofiles

PROC_STAT_CPU_COLUMNS = [
    'user',
    'nice',
    'system',
    'idle',
    'iowait',
    'irq',
    'softirq',
    'steal',
    'guest',
    'nice'
]

async def _cpu_times() -> Dict[str, Dict[str, int]]:
    """Return a list of cpu times

    :return: [description]
    :rtype: List[int]
    """
    all_stats: Dict[str, Dict[str, int]] = {}
    async with aiofiles.open('/proc/stat') as f:
        while True:
            line = await f.readline()
            if not (line and line.startswith('cpu')):
                break
            cpu, _, values = line.partition(' ')
            stats = {
                key: int(value)
                for key, value in zip(
                    PROC_STAT_CPU_COLUMNS, values.split()
                )
            }
            all_stats[cpu] = stats

    return all_stats

async def _cpu_time_deltas(sample_duration: float) -> Dict[str, Dict[str, int]]:
    start_times = await _cpu_times()
    await asyncio.sleep(sample_duration)
    end_times = await _cpu_times()
    return {
        start_cpu: {
            start_metric: start_value - end_times[start_cpu][start_metric]
            for start_metric, start_value in start_metrics.items()
        }
        for start_cpu, start_metrics in start_times.items()
    }

def _cpu_summarize(deltas: Dict[str, int]) -> Dict[str, float]:
    total = sum(deltas.values())
    return {
        name: 100 - (100 * (float(total - value) / total))
        for name, value in deltas.items()
    }

async def cpu_percents(sample_duration: float = 1.0) -> Dict[str, Dict[str, float]]:
    """Return a sample of the cpu
    
    :param sample_duration: The sample duration, defaults to 1.0
    :type sample_duration: float, optional
    :return: A dictionary of the stats
    :rtype: Dict[str, float]
    """ 
    deltas = await _cpu_time_deltas(sample_duration)
    return {cpu: _cpu_summarize(values) for cpu, values in deltas.items()}

async def meminfo() -> Dict[str, Tuple[int, Optional[str]]]:
    """Returns memory info"""
    stats: Dict[str, Tuple[int, Optional[str]]] = {}
    async with aiofiles.open('/proc/meminfo') as f:
        while True:
            line = await f.readline()
            if not line:
                break
            name, _, rest = line.partition(':')
            values = rest.strip().split(' ')
            value = int(values[0].strip())
            unit = None if len(values) == 1 else values[1].strip()
            stats[name] = (value, unit)

    return stats

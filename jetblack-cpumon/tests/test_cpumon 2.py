"""Test cpumon"""

import pytest

from jetblack_cpumon.cpumon2 import _cpu_times, cpu_percents, meminfo

@pytest.mark.asyncio
async def test__cpu_times():
    """Test _cpu_times()"""
    times = await _cpu_times()
    assert times is not None

@pytest.mark.asyncio
async def test_cpu_percents():
    """Test cpu_percents()"""
    times = await cpu_percents(1.0)
    assert times is not None

@pytest.mark.asyncio
async def test_meminfo():
    """Test _meminfo()"""
    info = await meminfo()
    assert info is not None

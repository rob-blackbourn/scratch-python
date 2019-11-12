"""Test cpumon"""

import pytest

from jetblack_cpumon.cpumon import _cpu_times, cpu_percents

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


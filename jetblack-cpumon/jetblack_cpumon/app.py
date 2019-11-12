"""The Web Application"""

import logging

from bareasgi import Application

from .cpumon_controller import CPUMonController

LOGGER = logging.getLogger(__name__)

def create_application() -> Application:
    """Create the application"""
    app = Application()
    controller = CPUMonController()
    controller.add_routes(app)
    return app

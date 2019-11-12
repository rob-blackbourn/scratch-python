"""The service"""

import uvicorn

from jetblack_cpumon.app import create_application

app = create_application()
uvicorn.run(app, port=9009)
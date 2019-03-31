from jetblack_auth.server import make_app
import uvicorn

PORT = 9010

app = make_app(PORT)

uvicorn.run(app, port=PORT)

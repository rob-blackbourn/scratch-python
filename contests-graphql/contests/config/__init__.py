from easydict import EasyDict as edict

CONFIG = edict({
    'postgres': {
        'host': "localhost",
        'database': 'contests',
        'user': "rtb",
        'password': "trustno1"
    },
    'mongo': {
        'host': 'localhost',
        'port': 27017,
        'username': 'rtb',
        'password': 'trustno1',
        'auth_source': 'admin',
        'database': 'contests'
    }
})

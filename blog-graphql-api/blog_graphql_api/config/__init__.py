CONFIG = {
    'http': {
        'port': 3000
    },
    'authentication': {
        'salt_rounds': 12,
        'secret': '!!! CHANGE ME !!!',
        'issuer': 'example.com',
        'token_expiry': '24h',
        'admin_primary_email': 'admin@localhost',
        'admin_default_password': 'admin'
    },
    'authorization': {
        'default_roles': ['user:read', 'user:write', 'public:read'],
        'approved_roles': ['posts:write', 'comment:write']
    }
}

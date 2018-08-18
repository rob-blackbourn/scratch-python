from datetime import datetime

x = datetime.now()
y = x.replace(microsecond=round(x.microsecond, -3))

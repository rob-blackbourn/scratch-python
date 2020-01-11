import sqlite3

conn = sqlite3.connect('recipes.db')

cur = conn.cursor()
cur.execute("""
SELECT * FROM property_map
WHERE property_name = ?
""", ('keywords',))
for row in cur:
    print(row)

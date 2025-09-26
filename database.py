import psycopg2

DB_PARAMS = {
    "host": "ep-old-hat-a1wv6deq-pooler.ap-southeast-1.aws.neon.tech",
    "dbname": "neondb",
    "user": "neondb_owner",
    "password": "npg_BQjbY3noG7EU",
    "port": 5432,
    "sslmode": "require",
    "channel_binding": "require"
}

def query(sql_query, params=None):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        if params:
            cur.execute(sql_query, params)
        else:
            cur.execute(sql_query)

        
        if sql_query.strip().lower().startswith("select"):
            results = cur.fetchall()
        else:
            conn.commit()       
            results = []      

        cur.close()
        conn.close()
        return results

    except Exception as e:
        print("Database error:", e)
        return []

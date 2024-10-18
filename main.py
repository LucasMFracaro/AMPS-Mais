import psycopg2

conn = psycopg2.connect("\
    dbname=cadastro \
    user=postgres \
    host=adversely-appeasing-gopher.data-1.usw2.tembo.io \
    password=nuoSPb29LvVmwTAX \
")

cursor = conn.cursor()

cursor.execute("SELECT * FROM contas_resp")

cursor.fetchall()

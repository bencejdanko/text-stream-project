#from impala.dbapi import connect
from pyhive import hive
conn = hive.Connection(host='localhost', port=10000)

# chunks table schema
# agent_id, destination_uri, event_time, chunk

cursor = conn.cursor()

cursor.execute("INSERT INTO TABLE chunks VALUES ('Agent_1', '/file1', '2022-01-01T00:00:00', 'chunk1')")

# Fetch and display results
# df = pd.DataFrame(cursor.fetchall(), columns=['agent_id', 'destination_uri', 'event_time', 'chunk'])
# print(df)

# Close the connection
cursor.close()
conn.close()
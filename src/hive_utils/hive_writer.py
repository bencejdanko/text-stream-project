from pyhive import hive

class HiveWriter:
    def __init__(self, host: str, port: int, table: str):
        self.host = host
        self.port = port
        self.table = table

    def insert_into_hive(self, batch_df, batch_id):
        if batch_df.isEmpty():
            return
        with hive.Connection(host=self.host, port=self.port) as conn:
            with conn.cursor() as cursor:
                for row in batch_df.collect():
                    cursor.execute(f"""
                        INSERT INTO {self.table} VALUES 
                        ('{row.agent_id}', '{row.destination_uri}', '{row.event_time}', '{row.chunk}')
                    """)

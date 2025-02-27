from mrjob.job import MRJob
import json
from datetime import datetime

class MRRReconstructFiles(MRJob):

    def mapper(self, _, line):
        try:
            record = json.loads(line)
            dest_uri = record.get("destination_uri")
            chunk_content = record.get("chunk", "") 
            
            if dest_uri:
                yield dest_uri, (record.get("event_time", ""), chunk_content)

        except Exception:
            self.increment_counter("warn", "malformed_lines", 1)

    def reducer(self, destination_uri, records):

        sorted_records = sorted(records, key=lambda x: datetime.fromisoformat(x[0]) if x[0] else "")

        reconstructed_text = "".join(record[1] for record in sorted_records if record[1])

        filename = f"{destination_uri.replace('/', '')}.txt"
        yield filename, reconstructed_text

if __name__ == '__main__':
    MRRReconstructFiles.run()

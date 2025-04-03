#!/bin/bash
/usr/local/bin/docker-entrypoint.sh & # Start the original entrypoint script in the background
echo "Waiting for Elasticsearch to start..."
until curl -s -X GET 'http://localhost:9200/_cluster/health?wait_for_status=yellow&timeout=60s' > /dev/null; do
  echo 'Waiting for Elasticsearch...'
  sleep 5
 done
 echo "Elasticsearch is up. Running bulk data upload..."
 curl -X POST 'http://localhost:9200/_bulk?pretty' -H 'Content-Type: application/json' --data-binary @/usr/share/elasticsearch/config/bulk_data.json
 echo "Bulk data upload complete. Keeping container running..."
 tail -f /dev/null # Keeps the container running

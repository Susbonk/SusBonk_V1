TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
curl -s -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d "{\"@timestamp\":\"$TS\",\"service\":{\"name\":\"sh-worker\"},\"log\":{\"level\":\"INFO\"},\"message\":\"hello from curl\"}"

curl -s -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d "[
    {\"@timestamp\":\"$TS\",\"service\":{\"name\":\"sh-worker\"},\"log\":{\"level\":\"INFO\"},\"message\":\"hello 1\"},
    {\"@timestamp\":\"$TS\",\"service\":{\"name\":\"sh-worker\"},\"log\":{\"level\":\"WARN\"},\"message\":\"hello 2\"}
  ]"

curl -s -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d "{\"@timestamp\":\"$TS\",\"service\":{\"name\":\"sh-worker\"},\"log\":{\"level\":\"ERROR\"},\"message\":\"ERROR from curl\"}"

curl -s -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d "{\"@timestamp\":\"$TS\",\"service\":{\"name\":\"sh-worker\"},\"log\":{\"level\":\"DEBUG\"},\"message\":\"DEBUG from curl\"}"

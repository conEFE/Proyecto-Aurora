#!/bin/bash
# Uso: carga.sh etiqueta  (desde backend/, con el código a medir en el árbol de trabajo)
set -e
source ./env.sh
su postgres -c "psql -q -d aurora_bench -c \"TRUNCATE request_metrics; INSERT INTO request_metrics(method,path,status_code,duration_ms,created_at) SELECT 'GET','/cases',200,random()*2000, now()-random()*interval '30 days' FROM generate_series(1,60000); ANALYZE request_metrics;\""
taskset -c 0 uvicorn app.main:app --port 8077 --workers 1 --log-level warning > ./uv_$1.log 2>&1 &
PID=$!; sleep 4
AURORA_LOAD_RUT=11111111-1 AURORA_LOAD_PASSWORD=Clave-Prueba-123 taskset -c 1-3 python -m scripts.load_test --base-url http://127.0.0.1:8077 --users ${USERS:-50} --seconds 60 --out ./carga_$1.json > ./carga_$1.txt 2>&1
kill $PID; wait $PID 2>/dev/null || true
python3 -c "
import json;d=json.load(open('./carga_$1.json'));t=d['total'];print('$1', 'req/s',t['req_por_s'],'p50',t['p50_ms'],'p95',t['p95_ms'],'err',t['errors'])
for k,v in d['endpoints'].items(): print('  ',k,v['p95_ms'])"

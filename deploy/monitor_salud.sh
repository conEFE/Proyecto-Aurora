#!/bin/bash
# Chequeo de disponibilidad del sitio público (cada minuto desde el crontab de ec2-user):
#   * * * * * /opt/aurora/deploy/monitor_salud.sh >/dev/null 2>&1
# Consulta https://<PUBLIC_URL>/api/health (DNS, IP, Caddy, TLS y API) y deja una línea en CloudWatch Logs
# (/aurora/monitor, flujo "salud"): «SALUD OK <s>» o «SALUD FALLA codigo=<http> <s>». Un filtro de métrica cuenta los
# OK y una alarma avisa por correo (SNS) si en 5 minutos hay menos de 3 o si dejan de llegar (servidor caído).
# Permisos: los del rol AuroraEC2Role sobre /aurora/* (logs:CreateLogStream y logs:PutLogEvents).
set -u
cd "$(dirname "$0")/.." || exit 1
url="$(grep -E '^PUBLIC_URL=' deploy/.env | cut -d= -f2- | tr -d '"')/api/health"
group=/aurora/monitor; stream=salud; region=us-east-2
out=$(curl -s -o /dev/null -m 10 -w '%{http_code} %{time_total}' "$url" || true)
code=${out%% *}; secs=${out#* }
if [ "$code" = "200" ]; then msg="SALUD OK ${secs}s"; else msg="SALUD FALLA codigo=${code:-000} ${secs}s"; fi
events="[{\"timestamp\":$(($(date +%s%N) / 1000000)),\"message\":\"$msg\"}]"
put() { aws logs put-log-events --region "$region" --log-group-name "$group" --log-stream-name "$stream" \
        --log-events "$events" >/dev/null 2>&1; }
put || { aws logs create-log-stream --region "$region" --log-group-name "$group" --log-stream-name "$stream" \
         >/dev/null 2>&1; put; }

# Handoff — Actualizar los diagramas de arquitectura al estado real de AWS

**Fecha:** 27-11-2026 · **Rama de trabajo:** `claude/bold-maxwell-13fkwp` (idéntica a `main` al escribir esto) ·
**Pedido del equipo:** «todos los gráficos de arquitectura están desactualizados; que se contextualice el AWS como está
actualmente». Maestro **1.8-rc** (18c), registro **v0.27** (última sección 4.26), PDF de 197 páginas y 25 figuras.

Lee antes: `CLAUDE.md`, `docs/ESTADO_AWS.md` (fuente principal del estado de AWS), `docs/informe_final/HANDOFF_ITERACION_19.md`
y las secciones 4 a 6 de `HANDOFF_ITERACION_18.md` (cómo se edita el maestro).

## 1. Objetivo y Definición de Hecho

Que cada diagrama de arquitectura del informe y de la presentación muestre **lo que hoy existe en AWS** (y lo que está
fuera de AWS, como el PC con GPU), con nombres reales de los recursos, y nada que no exista. Lo planificado se dibuja en
punteado y se rotula «planificado».

Listo cuando:
1. Los diagramas de la sección 3 están verificados contra AWS (sección 4) y regenerados, con su fuente `.drawio`.
2. El maestro los incluye; el texto y las tablas que los describen dicen lo mismo (sección 5).
3. La presentación se regeneró con ellos.
4. DOCX validado, PDF exportado sin «Error! Reference», registro de revisiones con la sección **4.27** y
   `trabajo/ESTADO_ITERACION.md` actualizado.
5. Commit en la rama y en `main` (ver sección 7).

## 2. Qué es lo real hoy (según `docs/ESTADO_AWS.md`, actualizado al 25-11-2026; **verificar**, sección 4)

| Pieza | Estado |
|---|---|
| Proyecto de AWS | Nueva experiencia de AWS, plan gratuito con créditos, **región fija us-east-2 (Ohio)**. No admite recursos ni copias en otras regiones |
| Sitio | `https://demo.auroracare.cl` (y `https://13-184-207-158.sslip.io`). Versión desplegada **2.11.0** (`sha-8a5e19f…`). La 2.12.0 está en `main` pero **sin desplegar** |
| DNS | Route 53, zona `auroracare.cl`, registro `demo` → Elastic IP. Dominio inscrito y delegado en NIC Chile |
| Servidor | EC2 `aurora-prod` (`t4g.micro` arm64, Amazon Linux 2023, 10 GB gp3 cifrado, IMDSv2, 2 GB de swap), Elastic IP `13.184.207.158` |
| Contenedores en EC2 | `web` (Caddy: HTTPS Let's Encrypt, sitio React, proxy `/api`) y `backend` (FastAPI). El contenedor `db` está **apagado** desde el 16-11-2026: la base está en RDS |
| Firewall | Grupo `aurora-web`: TCP 80, TCP 443 y UDP 443 desde internet; **sin puerto 22**. Grupo `aurora-rds`: 5432 solo desde `aurora-web` |
| Base de datos | RDS `aurora-demo-db` (PostgreSQL 16.15, `db.t4g.micro`, cifrada, privada, grupo de subredes `aurora-db`), respaldo automático de 1 día. Clave maestra en **Secrets Manager** (gestionada por RDS) |
| Imágenes y respaldos | Bucket S3 privado `aurora-imagenes-7k3p9x`: imágenes cifradas con Fernet + SSE-KMS (`aws/s3`), versionado; `backups/` 35 días |
| Respaldo | `deploy/backup_db.sh` en el crontab de `ec2-user`, diario 03:15 hora de Chile, vuelca la RDS a S3 |
| Acceso | Session Manager (sin SSH). Rol `AuroraEC2Role` (S3 `images/*` y `backups/*`, logs `/aurora/*`, `AmazonSSMManagedInstanceCore`) |
| Registros | CloudWatch Logs `/aurora/prod` (contenedores) y `/aurora/monitor` (chequeos), 30 días |
| Monitoreo | `deploy/monitor_salud.sh` cada minuto → `/aurora/monitor` → métricas `Aurora/ChequeosOK` y `Aurora/ChequeosFallidos` → alarmas `aurora-demo-sin-respuesta` y `aurora-ec2-estado` → SNS `aurora-alertas` (correo). Todo en us-east-2 |
| Presupuesto | `aurora-mensual`: USD 15 al mes, alertas al 85 %, 100 % y pronóstico |
| Modelo de IA | **Fuera de AWS:** PC de Juan con GPU (`aurora-modelo`, `100.114.99.23:8080`) por **Tailscale** (agente en EC2: `aurora-ec2`, `100.83.18.31`); si no responde, IA simulada marcada |
| Respaldo del modelo en AWS | **Planificado, no creado** (`t4g.small`, `docs/inferencia_remota.md` 5.1). Dibujar en punteado o no dibujar |
| Integración continua | GitHub Actions (pruebas, ZAP, imágenes en GHCR `ghcr.io/conefe/proyecto-aurora-*`); el servidor descarga imágenes, no compila |
| Instituciones | `aurora-admin` crea una pila CloudFormation `aurora-inst-<id>` por institución (`<id>.auroracare.cl`). `hospital-norte` se dio de baja el 16-11-2026; revisar si hoy hay alguna |
| No adoptado | Cloudflare, São Paulo (sa-east-1), Prometheus, Grafana, AWS Backup, copias en otra región, gRPC, DICOM/PACS. **No deben aparecer en ningún diagrama** |

## 3. Diagramas que hay que actualizar

Todos se generan con `docs/informe_final/herramientas/diagramas_drawio.py` (usa `drawio_lib.py`; cada función es un
diagrama con coordenadas explícitas) y quedan en `figuras/drawio/<nombre>.drawio` + `.svg`. PNG:
`node herramientas/svg_a_png.cjs figuras/drawio/<n>.svg figuras/<n>.png 2`.

| Figura del informe (numeración actual) | Función / archivo PNG | Qué revisar |
|---|---|---|
| Figura 9. Diagrama de componentes | `cap10_componentes` | Que «PostgreSQL» diga Amazon RDS; correos en modo consola; respaldo del modelo en punteado |
| Figura 11. Topología de comunicaciones | `cap10_topologia` | Elastic IP, grupos `aurora-web`/`aurora-rds`, Route 53 + NIC Chile, Tailscale (nombres e IP), Session Manager, GitHub/GHCR; contenedor `db` apagado o no dibujado |
| Figura 12. Infraestructura cloud desplegada | `cap10_infraestructura` | **El principal.** Contexto AWS real: proyecto, región us-east-2, VPC por defecto o la que corresponda (verificar subredes y si RDS está en subred privada), EC2 `aurora-prod`, RDS `aurora-demo-db`, S3 `aurora-imagenes-7k3p9x`, CloudWatch (2 grupos de logs, 2 métricas, 2 alarmas), SNS `aurora-alertas`, presupuesto `aurora-mensual`, IAM `AuroraEC2Role`, Secrets Manager (clave de RDS), Session Manager, Route 53. Afuera: usuarios, GitHub/GHCR, PC con GPU por Tailscale, correo del equipo |
| Figura 13. Arquitectura de la solución | `cap10_arquitectura` | Columna de infraestructura con los nombres reales; versión desplegada 2.11.0 |
| Figura 14. Componente de análisis | `it15_cnn` | No es de AWS; solo confirmar que el PC con GPU es el que lo ejecuta |
| Presentación, diapositivas «Arquitectura de la solución» e «Infraestructura desplegada en AWS» | `presentacion/generar_presentacion.py` (usa `cap10_arquitectura.png` y `cap10_infraestructura.png`) | Regenerar con `python3 preparar_base.py && python3 generar_presentacion.py` y revisar textos y notas |

Opcional, si el equipo lo pide: una figura con las tres formas de instalación (demo en `aurora-prod`, instituciones con
`aurora-admin`, plantilla de consola `deploy/aws-consola/aurora-aws.yaml`, instalador local de prueba).

**Estilo (pedido del equipo):** que no parezcan hechos por IA. Notación estándar (UML de despliegue/componentes), aspecto
de draw.io, sin títulos ni párrafos dentro de la imagen (la leyenda va en el informe), etiquetas cortas. Para el diagrama
de AWS conviene usar los **grupos oficiales de AWS** (AWS Cloud, Region, VPC, subred pública/privada) y, si es posible,
los íconos oficiales (AWS Architecture Icons, disponibles en draw.io como `mxgraph.aws4.*`): en el `.drawio` se pueden
usar esos estilos aunque el SVG propio use cajas; o exportar el PNG desde draw.io. **Ojo:** en esta sesión no se pudo
instalar draw.io ni ejecutar su visor descargado (lo bloqueó el control de permisos); si se necesita, pedir permiso al
usuario.

## 4. Verificar contra AWS antes de dibujar

`docs/ESTADO_AWS.md` es del 25-11-2026. Confirma el estado actual con consultas **solo de lectura** (sin crear, modificar
ni borrar nada; cualquier cambio requiere aprobación explícita del usuario). Se necesitan credenciales del proyecto
(`aws login --region us-east-2 --profile aurora`, lo hace el usuario; en la sesión anterior no había credenciales).
Revisa us-east-2 y, para logs/WAF, también us-east-1:

```bash
aws ec2 describe-instances --region us-east-2 --query 'Reservations[].Instances[].[InstanceId,InstanceType,State.Name,Tags[?Key==`Name`]|[0].Value,PublicIpAddress,VpcId,SubnetId]' --output table
aws ec2 describe-security-groups --region us-east-2 --query 'SecurityGroups[].[GroupName,GroupId]' --output table
aws rds describe-db-instances --region us-east-2 --query 'DBInstances[].[DBInstanceIdentifier,DBInstanceClass,EngineVersion,PubliclyAccessible,DBSubnetGroup.DBSubnetGroupName]' --output table
aws ec2 describe-subnets --region us-east-2 --query 'Subnets[].[SubnetId,VpcId,AvailabilityZone,MapPublicIpOnLaunch]' --output table
aws s3api list-buckets --query 'Buckets[].Name'
aws logs describe-log-groups --region us-east-2 --query 'logGroups[].logGroupName'
aws cloudwatch describe-alarms --region us-east-2 --query 'MetricAlarms[].[AlarmName,StateValue]' --output table
aws sns list-topics --region us-east-2
aws cloudformation list-stacks --region us-east-2 --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --query 'StackSummaries[].StackName'
aws route53 list-resource-record-sets --hosted-zone-id Z0628464DNWEOT5ICYNC --query 'ResourceRecordSets[].[Name,Type]' --output table
aws budgets describe-budgets --account-id "$(aws sts get-caller-identity --query Account --output text)" --query 'Budgets[].BudgetName'
```

Si algo difiere de la sección 2, **dibuja lo real** y anota la diferencia en `docs/ESTADO_AWS.md`. Si no hay credenciales,
dibuja según la sección 2 y dilo en el registro («según ESTADO_AWS.md del 25-11-2026, sin verificación en vivo»).

## 5. Texto del informe que debe quedar coherente

En el capítulo X: párrafos y tablas junto a las Figuras 11, 12 y 13, en especial la **Tabla «Componentes de
infraestructura»** (`_Ref_T_infra_tab`) y la fila «Servicio de inferencia de respaldo (planificado)». También revisar las
menciones en VII (tecnologías), XIII (disponibilidad, continuidad, monitoreo) y XIV (costos: ≈ USD 26 al mes de la
demostración). No inventar cifras ni recursos; si un dato no está en AWS ni en el repositorio, preguntar.

## 6. Cómo se edita el maestro (resumen)

1. Respaldo: `cp trabajo/Proyecto_Aurora_Informe_Final_Maestro.docx respaldos/Proyecto_Aurora_Informe_Final_Maestro_pre-it19.docx`.
2. Descomprimir en un directorio temporal; reemplazar imágenes y texto con un script `herramientas/iter19_*.py` (modelo:
   `iter18b_diagramas.py` para imágenes, `iter18c_sin_disenos.py` para párrafos; funciones en `maestro_lib.py`).
3. `zip -XrDqy` + `zip -d '*/'`; validar con `/mnt/skills/public/docx/scripts/office/validate.py`; exportar con
   `python3 herramientas/exportar_pdf.py <docx> trabajo/Proyecto_Aurora_Informe_Final.pdf`; buscar «Error! Reference».
4. Registro: script `herramientas/iter19_registro.py` (modelo: `iter18c_registro.py`), sección 4.27; versión del maestro
   1.8-rc (19) o 1.9-rc.

## 7. Reglas

- No inventar: nada «desplegado», «medido» o «creado» sin evidencia. El respaldo del modelo en AWS **no existe**.
- No crear ni cambiar recursos de AWS sin aprobación explícita del usuario. Solo región us-east-2.
- Commits en `main`: **un commit con autoría de Felipe Campos Delgado** y **sin coautoría de Claude** (ver `CLAUDE.md`);
  sin `push --force`. Mantener la rama `claude/bold-maxwell-13fkwp` sincronizada con `main`.
- Textos en español; mostrar al usuario el resultado (PNG o PDF) antes de cerrar.

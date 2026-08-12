.PHONY: all up build run logs down clean ports monitoring-user verify psql wait

HDBSQL := /usr/sap/HXE/HDB90/exe/hdbsql
HANA_PASSWORD ?= HXEHana1

# Start SAP HANA Express + the load generator.
# First boot takes ~10 minutes. Track it with `make logs` or `make wait`.
up:
	docker compose up -d

# Build the Python load generator image.
build:
	docker build -t saphana-loadgen ./load-generator

# Run the load generator on its own (compose already starts one).
run:
	docker run --network=saphana-load-generator_saphana-network --rm saphana-loadgen

# Show live container logs.
logs:
	docker compose logs -f

# Block until HANA reports healthy. Useful in scripts before `monitoring-user`.
wait:
	@echo "waiting for SAP HANA to become healthy (first boot takes ~10 min)..."
	@until [ "$$(docker inspect -f '{{.State.Health.Status}}' saphana-db 2>/dev/null)" = "healthy" ]; do \
	  printf '.'; sleep 10; \
	done; echo " healthy."

# Show the REAL SQL ports as HANA reports them. Never guess these — the
# tenant port varies by build and by tenant creation order.
ports:
	@docker exec saphana-db $(HDBSQL) -n localhost:39013 -d SYSTEMDB -u SYSTEM -p '$(HANA_PASSWORD)' \
	  "SELECT DATABASE_NAME, SERVICE_NAME, SQL_PORT FROM SYS_DATABASES.M_SERVICES WHERE SQL_PORT > 0"

# Create the restricted monitoring user on the HXE TENANT (39041).
monitoring-user:
	@# Two hdbsql quirks are worked around here, both of which produce
	@# misleading errors:
	@#
	@#  1. `hdbsql -I` does NOT understand `--` comments. It treats each comment
	@#     line as a statement and fails with "sql syntax error". So strip
	@#     comments and blank lines, letting the .sql file stay documented.
	@#
	@#  2. Piping into `-I /dev/stdin` MANGLES the stream: the first two bytes
	@#     are consumed, so CREATE becomes EATE and you get
	@#     `incorrect syntax near "EATE"` followed by a cascade of
	@#     `invalid user name` errors from every later GRANT. Copy a real file
	@#     into the container and point -I at that path instead.
	@sed -e 's/--.*$$//' -e '/^[[:space:]]*$$/d' setup_monitoring_user.sql > .monitoring_user.tmp.sql
	@docker cp .monitoring_user.tmp.sql saphana-db:/tmp/monitoring_user.sql >/dev/null
	@rm -f .monitoring_user.tmp.sql
	@docker exec saphana-db $(HDBSQL) -n localhost:39041 -d HXE -u SYSTEM -p '$(HANA_PASSWORD)' -I /tmp/monitoring_user.sql
	@# Best-effort: `docker cp` lands the file as root while the container runs
	@# as uid 12000, so the in-container user cannot delete it. Not worth
	@# failing the target over — it contains no secret beyond the password
	@# already in this file, and the volume is discarded by `make down`.
	@-docker exec --user root saphana-db rm -f /tmp/monitoring_user.sql 2>/dev/null || true
	@echo
	@echo "OTEL_MONITORING_USER ready on tenant HXE (port 39041)."
	@echo "Re-running this target is safe: 'user/role already exists' above just"
	@echo "means it was created earlier. The grants are re-applied either way."
	@echo "Confirm with: make verify"

# Prove the monitoring user works: connect AS that user and read the views.
# A missing grant surfaces here as an authorization error on that view,
# rather than as a silently absent metric later.
verify:
	@echo "=== connected as ==="
	@docker exec saphana-db $(HDBSQL) -n localhost:39041 -d HXE -u OTEL_MONITORING_USER -p '$(HANA_PASSWORD)' \
	  "SELECT CURRENT_USER FROM DUMMY"
	@echo
	@echo "=== monitoring views readable ==="
	@docker exec saphana-db $(HDBSQL) -n localhost:39041 -d HXE -u OTEL_MONITORING_USER -p '$(HANA_PASSWORD)' \
	  "SELECT 'M_CONNECTIONS' AS VIEW_NAME, COUNT(*) AS ROWS FROM SYS.M_CONNECTIONS \
	   UNION ALL SELECT 'M_SERVICE_MEMORY', COUNT(*) FROM SYS.M_SERVICE_MEMORY \
	   UNION ALL SELECT 'M_SERVICE_STATISTICS', COUNT(*) FROM SYS.M_SERVICE_STATISTICS \
	   UNION ALL SELECT 'M_CS_TABLES', COUNT(*) FROM SYS.M_CS_TABLES \
	   UNION ALL SELECT 'M_HOST_RESOURCE_UTILIZATION', COUNT(*) FROM SYS.M_HOST_RESOURCE_UTILIZATION \
	   UNION ALL SELECT 'M_WORKLOAD', COUNT(*) FROM SYS.M_WORKLOAD"
	@echo
	@echo "=== demo data ==="
	@docker exec saphana-db $(HDBSQL) -n localhost:39013 -d HXE -u SYSTEM -p '$(HANA_PASSWORD)' \
	  "SELECT TABLE_NAME, RECORD_COUNT, MEMORY_SIZE_IN_TOTAL FROM SYS.M_CS_TABLES WHERE SCHEMA_NAME = 'DEMO'"

# Interactive hdbsql shell against the tenant.
psql:
	docker exec -it saphana-db $(HDBSQL) -n localhost:39013 -d HXE -u SYSTEM -p '$(HANA_PASSWORD)'

# Stop and remove containers + volumes. This discards the HANA data volume,
# so the next `make up` pays the full ~10 minute first boot again.
down:
	docker compose down -v

clean: down

# Full flow: start, wait for HANA, create the monitoring user.
all: up wait monitoring-user
	@echo
	@echo "SAP HANA is ready. Point the Middleware agent at <host>:39041"
	@echo "with user OTEL_MONITORING_USER. See README.md."

-- Monitoring user for the Middleware SAP HANA integration.
--
-- Mirrors Steps 1-3 of the official setup guide:
-- https://docs.middleware.io/integrations/saphana-integration
--
-- Applied by:  make monitoring-user
--
-- IMPORTANT: run this against the HXE TENANT (port 39041), not SYSTEMDB.
-- The agent reads only the plain SYS.* views of whichever database it connects
-- to, so an endpoint aimed at SYSTEMDB collects the nameserver's own
-- near-empty metrics instead of the tenant's workload. It connects and
-- reports success either way, which makes this easy to miss.
--
-- On a multitenant system, repeat this for every tenant you want to monitor:
-- each tenant has its own SYS schema, users, and roles.

-- Step 1 — the restricted user.
--
-- NO FORCE_FIRST_PASSWORD_CHANGE is required. By default HANA forces a
-- password change on first login, which an unattended agent cannot perform,
-- so without it every connection attempt fails.
--
-- Keep the double quotes: an unquoted password is upper-cased by HANA and
-- will not match what you configure in the agent.
--
-- Password characters: the agent passes the password inside a connection URL
-- that is percent-decoded before use. Avoid / ? # % < > [ ] { } | \ ^ ` "
-- and spaces. @ and : are safe. % is the most dangerous because it fails
-- SILENTLY -- %41 decodes to "A", so the agent authenticates with a different
-- password than you set, with no error naming the password as the cause.
CREATE RESTRICTED USER OTEL_MONITORING_USER PASSWORD "HXEHana1" NO FORCE_FIRST_PASSWORD_CHANGE;

-- A lab user whose password silently expires in 182 days turns into a
-- confusing outage later.
ALTER USER OTEL_MONITORING_USER DISABLE PASSWORD LIFETIME;

-- Step 2 — enable client connections.
-- A restricted user can only connect over HTTP/HTTPS until this is granted;
-- it has no SQL connectivity at all by default.
ALTER USER OTEL_MONITORING_USER ENABLE CLIENT CONNECT;
GRANT RESTRICTED_USER_JDBC_ACCESS TO OTEL_MONITORING_USER;

-- Step 3 — the monitoring role.
-- One GRANT SELECT per monitoring view the integration reads. Grant all of
-- them: removing one silently drops the metrics sourced from that view.
CREATE ROLE OTEL_MONITORING;

GRANT CATALOG READ TO OTEL_MONITORING;

GRANT SELECT ON SYS.M_BACKUP_CATALOG TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_BLOCKED_TRANSACTIONS TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_CONNECTIONS TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_CS_ALL_COLUMNS TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_CS_TABLES TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_DATABASE TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_DISKS TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_HOST_RESOURCE_UTILIZATION TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_LICENSES TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_RS_TABLES TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_SERVICE_COMPONENT_MEMORY TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_SERVICE_MEMORY TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_SERVICE_REPLICATION TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_SERVICE_STATISTICS TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_SERVICE_THREADS TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_SERVICES TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_VOLUME_IO_TOTAL_STATISTICS TO OTEL_MONITORING;
GRANT SELECT ON SYS.M_WORKLOAD TO OTEL_MONITORING;
GRANT SELECT ON _SYS_STATISTICS.STATISTICS_CURRENT_ALERTS TO OTEL_MONITORING;

GRANT OTEL_MONITORING TO OTEL_MONITORING_USER;

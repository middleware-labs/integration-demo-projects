# Use the official Cassandra image as a base
FROM cassandra:latest

# This is for illustration of cassandra demo; for porduction clusters please add ssl authentication

# Update the cassandra-env.sh file to configure JMX options and remove the password
RUN sed -i 's/JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.authenticate=true"/JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote.authenticate=false"/g' /etc/cassandra/cassandra-env.sh \
    && sed -i '/password/d' /etc/cassandra/cassandra-env.sh \
    && echo 'JVM_OPTS="$JVM_OPTS -Dcom.sun.management.jmxremote=true -Dcom.sun.management.jmxremote.local.only=false -Dcom.sun.management.jmxremote.port=7199 -Dcom.sun.management.jmxremote.rmi.port=7199 -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false -Djava.rmi.server.hostname=localhost"' >> /etc/cassandra/cassandra-env.sh

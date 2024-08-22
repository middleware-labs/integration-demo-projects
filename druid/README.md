### Step 1 - Download and extract druid

 Download Druid binary from [here](https://www.apache.org/dyn/closer.cgi?path=/druid/30.0.0/apache-druid-30.0.0-bin.tar.gz)

 After downloading, extract it by running:

``` bash
tar xvfz apache-druid-30.0.0-bin.tar.gz -C <DESTINATION-DIRECTORY>
```

Now to run Druid, cd into the `apache-druid-30.0.0` directory and run one of its quick start  demo project.

```  bash
cd apache-druid-30.0.0
```

``` bash
./bin/start-nano-quickstart
```


NOTE: For the purpose of this demo we will be using single-server/nano-quickstart. This is meant for testing and development related purposes.

This should output:
```
[Tue Aug 20 11:17:33 2024] Starting Apache Druid.
[Tue Aug 20 11:17:33 2024] Open http://localhost:8888/ or http://naman-Vostro-3500:8888/ in your browser to access the web console.
[Tue Aug 20 11:17:33 2024] Or, if you have enabled TLS, use https on port 9088.
[Tue Aug 20 11:17:33 2024] Starting services with log directory [/home/naman/experiments/druid-demo/apache-druid-30.0.0/log].
[Tue Aug 20 11:17:33 2024] Running command[zk]: bin/run-zk conf
[Tue Aug 20 11:17:33 2024] Running command[coordinator-overlord]: bin/run-druid coordinator-overlord conf/druid/single-server/nano-quickstart
[Tue Aug 20 11:17:33 2024] Running command[broker]: bin/run-druid broker conf/druid/single-server/nano-quickstart
[Tue Aug 20 11:17:33 2024] Running command[router]: bin/run-druid router conf/druid/single-server/nano-quickstart
[Tue Aug 20 11:17:33 2024] Running command[historical]: bin/run-druid historical conf/druid/single-server/nano-quickstart
[Tue Aug 20 11:17:33 2024] Running command[middleManager]: bin/run-druid middleManager conf/druid/single-server/nano-quickstart

```

You can access the web UI at `http://localhost:8888/`


### Step 2: Configure Druid to emit metrics

All the config files for respective components are preset in their respective server setups of the `conf` directory. For purpose we can find the config files under `conf/druid/single-server/nano-quickstart`. 

Replace the `conf` directory in the root of your Druid project with the `conf` directory found at `druid/conf` in this repo.

You can start druid again with:
```
./bin/start-nano-quickstart
```

### (Alternatively) Step 2:
All the config files for respective components are preset in their respective server setups of the `conf` directory. For purpose we can find the config files under `conf/druid/single-server/nano-quickstart`. 

If you have any additional configs in the conf directory and/or do not want to change complete `conf` directory, you can apply the following changes.
CD into this directory to start configuring druid to send metrics. 

```
cd conf/druid/single-server/nano-quickstart/
```

#### Common 
This folder contains common configuration files shared across different Druid processes.

Open `_common/common.runtime.properties` and change/add the following:

To add monitors change `druid.monitoring.monitors`:
```
druid.monitoring.monitors=["org.apache.druid.server.metrics.MetricsModule", "org.apache.druid.client
    .cache.CacheMonitor", "org.apache.druid.java.util.metrics.JvmMonitor", "org.apache.druid.java.util.m
    etrics.CpuAcctDeltaMonitor", "org.apache.druid.java.util.metrics.JvmThreadsMonitor", "org.apache.dru
    id.server.metrics.EventReceiverFirehoseMonitor", "org.apache.druid.server.metrics.QueryCountStatsMon
    itor", "org.apache.druid.segment.realtime.RealtimeMetricsMonitor", "org.apache.druid.server.metrics.
    HistoricalMetricsMonitor", "org.apache.druid.server.metrics.CoordinatorMetricsMonitor", "org.apache.
    druid.server.metrics.OverlordMetricsMonitor", "org.apache.druid.server.metrics.MiddleManagerMonitor"
    , "org.apache.druid.server.metrics.RouterMetricsMonitor"
```

To configure emitter add:
```
druid.emitter=http
druid.emitter.http.recipientBaseUrl=http://localhost:8081/metrics
druid.emitter.http.flushMillis=60000
druid.emitter.http.flushCount=500
```

#### Broker
The broker is essentially the "smart endpoint" of a Druid cluster. It abstracts away the complexity of the distributed system from the client's perspective, presenting Druid as a unified query engine despite its distributed nature.

Open `broker/runtime.properties` and change the following:

Plaintext port to 8090:

```
druid.plaintextPort=8090
```

And add the following monitors to generate metrics:
\
```
 druid.monitoring.monitors=["org.apache.druid.client.cache.CacheMonitor", "org.apache.druid.java.util.metrics.JvmMonitor", "org.apache.druid.java.util.metrics.CpuAcctDeltaMonitor", "org.apache.druid.java.ut
    il.metrics.JvmThreadsMonitor", "org.apache.druid.server.metrics.EventReceiverFirehoseMonitor", "org.apache.druid.server.metrics.QueryCountStatsMonitor"]
```

#### Coordinator-Overlord
The Coordinator manages data availability and retention, overseeing the distribution of data segments across Historical nodes, ensuring proper replication, and handling load balancing. It also manages the rules for data retention and tiering. The Overlord, on the other hand, manages the ingestion workflow, supervising real-time data ingestion tasks run by MiddleManagers. It distributes ingestion tasks, monitors their progress, and handles task failures. In smaller Druid deployments, these two roles are often combined into a single process (hence "coordinator-overlord") to simplify the architecture and reduce resource usage, while still providing the essential functions of data management and ingestion coordination for the entire Druid cluster.

Open `coordinator-overlord/runtime.properties` and change the following:

Plaintext port to 8091:

```
druid.plaintextPort=8091
```

Add the following monitors to generate metrics:

```
druid.monitoring.monitors=["org.apache.druid.client.cache.CacheMonitor", "org.apache.druid.java.util
    .metrics.JvmMonitor", "org.apache.druid.java.util.metrics.CpuAcctDeltaMonitor", "org.apache.druid.ja
    va.util.metrics.JvmThreadsMonitor", "org.apache.druid.server.metrics.EventReceiverFirehoseMonitor",
    "org.apache.druid.server.metrics.TaskCountStatsMonitor"]
```

#### Middle-Manager
The MiddleManager in Druid is responsible for executing data ingestion tasks. It runs on nodes that handle the actual ingestion of data into the system, launching task processes that parse incoming data and create segments. MiddleManagers work under the direction of the Overlord, which assigns them ingestion tasks. They also report task statuses and handle the persistence of newly created segments before they're handed off to Historical nodes for querying.

Open `middleManager/runtime.properties`
```
druid.plaintextPort=8092
```

Add the following monitors to generate metrics:
```
druid.monitoring.monitors=["org.apache.druid.client.cache.CacheMonitor", "org.apache.druid.java.util
    .metrics.JvmMonitor", "org.apache.druid.java.util.metrics.CpuAcctDeltaMonitor", "org.apache.druid.ja
    va.util.metrics.JvmThreadsMonitor", "org.apache.druid.server.metrics.EventReceiverFirehoseMonitor"]
```


#### Historical
Historical nodes in Druid are responsible for storing and serving immutable data segments. They download segments from deep storage, keep them in memory or on local disks for fast querying, and respond to queries from Broker nodes. Historical nodes form the backbone of Druid's querying capabilities for historical data, efficiently managing large volumes of immutable data while ensuring quick access and query performance.


Open `historical/runtime.properties`
```
druid.plaintextPort=8093
```


Add the following monitors to generate metrics:
```
druid.monitoring.monitors=["org.apache.druid.client.cache.CacheMonitor", "org.apache.druid.java.util
    .metrics.JvmMonitor", "org.apache.druid.java.util.metrics.CpuAcctDeltaMonitor", "org.apache.druid.ja
    va.util.metrics.JvmThreadsMonitor", "org.apache.druid.server.metrics.EventReceiverFirehoseMonitor"]
```

#### Router

Open `historical/runtime.properties`
```
druid.plaintextPort=9999
```


Add the following monitors to generate metrics:
```
druid.monitoring.monitors=["org.apache.druid.client.cache.CacheMonitor", "org.apache.druid.java.util
    .metrics.JvmMonitor", "org.apache.druid.java.util.metrics.CpuAcctDeltaMonitor", "org.apache.druid.ja
    va.util.metrics.JvmThreadsMonitor", "org.apache.druid.server.metrics.EventReceiverFirehoseMonitor",
    "org.apache.druid.server.metrics.QueryCountStatsMonitor"]
```


 


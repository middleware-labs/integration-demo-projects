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


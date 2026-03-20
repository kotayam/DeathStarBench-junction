# Scripts

## Setting up Docker Swarm

Run the following command on the manager node.

```
docker swarm init --advertise-addr <Private IP> --data-path-addr <Private IP>
```

On the worker nodes, run the `docker swarm join` command with the token.

## Setting up tiers

Run the following scripts on the manager node.

1. Assign tiers to each node.

```
./scripts/assign_tiers.sh
```

2. Deploy the stack.

```
./scripts/deploy_stack.sh
```

3. Verify the topology.

```
./scripts/verify_topology.sh
```

## Running workloads

1. Start monitoring dirty page rates on the target nodes.

```
./scripts/monitor_service.sh <service name>
```

2. Generate the workload on the client node.

```
./scripts/run_workload.sh -r 1000 -c 128 -t 40 -d 120s
```

## Generating graphs

- `generate_graph.py`
- `generate_multigraph.py`: x-axis based on timestamp.
- `generate_benchmark_graphs.py`
- `compare_workloads.py`: x-axis based on elapsed time.

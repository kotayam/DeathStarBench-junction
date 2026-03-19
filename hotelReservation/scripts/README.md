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


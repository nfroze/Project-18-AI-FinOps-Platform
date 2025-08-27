# Project 18: AI FinOps Platform

## Overview

Apache Kafka streaming platform on Kubernetes for cost event processing. Strimzi operator manages Kafka cluster on AWS EKS. OpenCost, Prometheus, and Grafana provide cost monitoring and visualisation.

## Architecture

```
GPU Metrics ──┐
              ├──> Kafka Broker ──> Stream Processing ──> Anomaly Detection
API Costs ────┘    (3 brokers)                           
                        ↓
                   Cost Topics
            (Partitioned by volume)
```

## Technologies Used

### Core Platform
- Kubernetes: EKS 1.28 - Container orchestration
- Apache Kafka: v3.5.0 via Strimzi operator v0.39.0
- Terraform: v1.5 - Infrastructure as Code
- AWS: EKS, VPC, ELB (eu-west-2)

### Monitoring Stack
- OpenCost: v1.25 - Kubernetes cost allocation
- Prometheus: v2.46 - Metrics collection
- Grafana: v10.0 - Visualisation
- kube-prometheus-stack: Complete monitoring solution

## Project Structure

```
project-18-ai-finops/
├── terraform/
│   ├── main.tf              # EKS cluster configuration
│   ├── variables.tf         # Variable definitions
│   └── outputs.tf           # Output values
├── kafka/
│   ├── strimzi-operator.yaml    # Kafka operator deployment
│   ├── kafka-cluster.yaml       # 3-broker cluster config
│   └── topics/
│       ├── gpu-utilization-events.yaml    # 10 partitions
│       ├── ai-api-costs.yaml              # 10 partitions
│       └── cost-anomalies.yaml            # 3 partitions
└── monitoring/
    ├── prometheus-stack.yaml    # Monitoring deployment
    ├── opencost.yaml            # Cost allocation
    └── grafana-dashboards.yaml  # Dashboard configurations
```

## Implementation

### Kafka Cluster Configuration

The platform uses Strimzi operator to manage a 3-broker Kafka cluster with Zookeeper ensemble. Three topics handle different event types:

- gpu-utilization-events: 10 partitions for GPU metrics
- ai-api-costs: 10 partitions for API token tracking
- cost-anomalies: 3 partitions for anomaly events

### Infrastructure Components

- EKS cluster with 3 t3.large nodes
- VPC with private subnets
- Application load balancer
- Security groups and IAM roles

### Monitoring Stack

- Prometheus scrapes metrics every 15 seconds
- OpenCost calculates Kubernetes resource costs
- Grafana provides dashboards for visualisation
- Pod-level cost granularity

## Kafka Topics

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: gpu-utilization-events
spec:
  partitions: 10
  replicas: 3
  config:
    retention.ms: 86400000  # 24 hour retention
```

## Screenshots

1. [EKS cluster with 3 nodes](screenshots/eks-cluster.png)
2. [Kafka topics with partition configuration](screenshots/kafka-topics.png)
3. [Grafana dashboard showing resource utilisation](screenshots/grafana-dashboard.png)
4. [OpenCost UI for cost allocation](screenshots/opencost-ui.png)
5. [All platform pods running](screenshots/pods-running.png)

## Deployment Process

1. Terraform creates EKS cluster and networking
2. Strimzi operator deployed to cluster
3. Kafka cluster and topics created
4. Prometheus stack installed via Helm
5. OpenCost connected to Prometheus
6. Grafana dashboards configured

## Features

### Event Streaming
- Kafka cluster with 3 brokers
- 23 total partitions across topics
- 24-hour event retention
- Topic monitoring

### Cost Monitoring
- Kubernetes resource cost tracking
- Namespace-based allocation
- Pod-level granularity
- Real-time metrics collection

### Infrastructure
- Managed Kubernetes on EKS
- Production-grade networking
- Terraform-managed resources
- GitOps-ready configurations
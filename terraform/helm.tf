# Configure Kubernetes and Helm providers
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}

# Strimzi Kafka Operator
resource "helm_release" "strimzi_operator" {
  name             = "strimzi-operator"
  repository       = "https://strimzi.io/charts/"
  chart            = "strimzi-kafka-operator"
  namespace        = "kafka"
  create_namespace = true
  version          = "0.39.0"

  depends_on = [module.eks]
}

# Prometheus Stack for monitoring
resource "helm_release" "prometheus_stack" {
  name             = "monitoring"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true
  version          = "55.5.0"

  values = [
    <<-EOT
    prometheus:
      prometheusSpec:
        serviceMonitorSelectorNilUsesHelmValues: false
        storageSpec:
          volumeClaimTemplate:
            spec:
              accessModes: ["ReadWriteOnce"]
              resources:
                requests:
                  storage: 10Gi
    grafana:
      adminPassword: "${var.grafana_admin_password}"
      service:
        type: LoadBalancer
    EOT
  ]

  depends_on = [module.eks]
}

# OpenCost for K8s cost monitoring
resource "helm_release" "opencost" {
  name             = "opencost"
  repository       = "https://opencost.github.io/opencost-helm-chart"
  chart            = "opencost"
  namespace        = "opencost"
  create_namespace = true
  version          = "1.25.0"

  values = [
    <<-EOT
    opencost:
      prometheus:
        internal:
          serviceName: monitoring-kube-prometheus-prometheus
          namespaceName: monitoring
          port: 9090
      ui:
        enabled: true
        service:
          type: LoadBalancer
    EOT
  ]

  depends_on = [helm_release.prometheus_stack]
}

# NVIDIA GPU Operator for GPU monitoring
resource "helm_release" "gpu_operator" {
  name             = "gpu-operator"
  repository       = "https://helm.ngc.nvidia.com/nvidia"
  chart            = "gpu-operator"
  namespace        = "gpu-operator"
  create_namespace = true
  version          = "v23.9.1"

  values = [
    <<-EOT
    operator:
      defaultRuntime: containerd
    dcgmExporter:
      enabled: true
      serviceMonitor:
        enabled: true
    EOT
  ]

  depends_on = [module.eks]
}
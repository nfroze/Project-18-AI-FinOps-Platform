#!/usr/bin/env python3
"""
GPU Metrics Collector for AI FinOps Platform
Streams real-time GPU utilization and cost data to Kafka
"""

import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPUMetricsCollector:
    def __init__(self, kafka_bootstrap_servers='localhost:9092', prometheus_url='http://localhost:9090'):
        """Initialize GPU metrics collector"""
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='gzip'
        )
        self.prometheus_url = prometheus_url
        
        # GPU pricing per hour
        self.gpu_costs = {
            'nvidia-t4': 0.526,
            'nvidia-v100': 2.48,
            'nvidia-a100': 3.06,
            'nvidia-h100': 4.50
        }
    
    def fetch_gpu_metrics(self):
        """Fetch GPU metrics from Prometheus"""
        try:
            # Query for GPU utilization
            query = 'DCGM_FI_DEV_GPU_UTIL'
            response = requests.get(f'{self.prometheus_url}/api/v1/query', 
                                   params={'query': query})
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('result', [])
            else:
                logger.warning(f"Failed to fetch metrics: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return []
    
    def generate_mock_metrics(self):
        """Generate mock GPU metrics for demo purposes"""
        nodes = ['node-gpu-1', 'node-gpu-2']
        metrics = []
        
        for node in nodes:
            for gpu_id in range(2):  # 2 GPUs per node
                metrics.append({
                    'node': node,
                    'gpu_id': f'gpu-{gpu_id}',
                    'gpu_type': 'nvidia-t4',
                    'utilization': random.uniform(20, 95),
                    'memory_used_gb': random.uniform(4, 16),
                    'temperature': random.uniform(40, 80),
                    'power_draw': random.uniform(50, 150)
                })
        
        return metrics
    
    def calculate_cost(self, metric):
        """Calculate cost based on GPU utilization"""
        gpu_type = metric.get('gpu_type', 'nvidia-t4')
        utilization = metric.get('utilization', 0)
        
        hourly_cost = self.gpu_costs.get(gpu_type, 1.0)
        actual_cost = hourly_cost * (utilization / 100)
        
        return {
            'hourly_cost': hourly_cost,
            'actual_cost': actual_cost,
            'waste_cost': hourly_cost - actual_cost
        }
    
    def send_to_kafka(self, metrics):
        """Send metrics to Kafka"""
        for metric in metrics:
            event = {
                'timestamp': datetime.utcnow().isoformat(),
                'node': metric['node'],
                'gpu_id': metric['gpu_id'],
                'gpu_type': metric['gpu_type'],
                'utilization': metric['utilization'],
                'memory_used_gb': metric['memory_used_gb'],
                'temperature': metric['temperature'],
                'power_draw': metric['power_draw'],
                **self.calculate_cost(metric),
                'team': f'team-{random.choice(["ml", "data", "research"])}'
            }
            
            # Send to Kafka
            self.producer.send('gpu-utilization-events', value=event)
            
            # Check for anomalies
            if metric['utilization'] < 20:
                anomaly = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'underutilized_gpu',
                    'severity': 'warning',
                    'node': metric['node'],
                    'gpu_id': metric['gpu_id'],
                    'utilization': metric['utilization'],
                    'waste_cost_per_hour': event['waste_cost'],
                    'message': f"GPU {metric['gpu_id']} is only {metric['utilization']:.1f}% utilized"
                }
                self.producer.send('cost-anomalies', value=anomaly)
        
        self.producer.flush()
        logger.info(f"Sent {len(metrics)} metrics to Kafka")
    
    def run(self, use_mock=True, interval=10):
        """Main collection loop"""
        logger.info("Starting GPU metrics collection...")
        logger.info(f"Using {'mock' if use_mock else 'real'} data")
        logger.info(f"Sending to Kafka every {interval} seconds")
        
        while True:
            try:
                if use_mock:
                    metrics = self.generate_mock_metrics()
                else:
                    metrics = self.fetch_gpu_metrics()
                
                if metrics:
                    self.send_to_kafka(metrics)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    import sys
    
    # Parse arguments
    kafka_servers = sys.argv[1] if len(sys.argv) > 1 else 'localhost:9092'
    use_mock = '--mock' in sys.argv
    
    collector = GPUMetricsCollector(kafka_bootstrap_servers=kafka_servers)
    collector.run(use_mock=use_mock)
#!/usr/bin/env python3
"""
Test Data Generator for AI FinOps Platform
Generates realistic cost events for demo purposes
"""

import json
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDataGenerator:
    def __init__(self, kafka_bootstrap_servers='localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        self.models = ['gpt-4', 'gpt-3.5-turbo', 'claude-3-opus', 'claude-3-sonnet']
        self.teams = ['ml-team', 'data-team', 'research', 'product', 'engineering']
        self.gpu_types = ['nvidia-t4', 'nvidia-v100', 'nvidia-a100']
        
    def generate_gpu_events(self, count=100):
        """Generate GPU utilization events"""
        logger.info(f"Generating {count} GPU events...")
        
        for i in range(count):
            # Simulate different utilization patterns
            if i % 10 == 0:
                # Idle GPU (waste!)
                utilization = random.uniform(0, 10)
            elif i % 5 == 0:
                # Underutilized
                utilization = random.uniform(10, 40)
            else:
                # Normal usage
                utilization = random.uniform(50, 95)
            
            event = {
                'timestamp': (datetime.utcnow() - timedelta(minutes=random.randint(0, 60))).isoformat(),
                'node': f'node-gpu-{random.randint(1, 5)}',
                'gpu_id': f'gpu-{random.randint(0, 7)}',
                'gpu_type': random.choice(self.gpu_types),
                'utilization': utilization,
                'memory_used_gb': random.uniform(4, 32),
                'temperature': random.uniform(40, 85),
                'power_draw': random.uniform(50, 300),
                'team': random.choice(self.teams),
                'hourly_cost': random.uniform(0.5, 4.5),
                'actual_cost': utilization / 100 * random.uniform(0.5, 4.5)
            }
            
            self.producer.send('gpu-utilization-events', value=event)
            
            # Generate anomalies for idle GPUs
            if utilization < 20:
                anomaly = {
                    'timestamp': event['timestamp'],
                    'type': 'gpu_waste',
                    'severity': 'high' if utilization < 10 else 'medium',
                    'message': f"GPU {event['gpu_id']} only {utilization:.1f}% utilized",
                    'waste_cost': event['hourly_cost'] * (1 - utilization/100),
                    'team': event['team']
                }
                self.producer.send('cost-anomalies', value=anomaly)
        
        logger.info(f"Generated {count} GPU events")
    
    def generate_api_costs(self, count=200):
        """Generate AI API cost events"""
        logger.info(f"Generating {count} API cost events...")
        
        for i in range(count):
            model = random.choice(self.models)
            
            # Simulate different usage patterns
            if i % 20 == 0:
                # Spike (potential runaway)
                tokens = random.randint(10000, 50000)
            else:
                # Normal usage
                tokens = random.randint(100, 2000)
            
            event = {
                'timestamp': (datetime.utcnow() - timedelta(minutes=random.randint(0, 120))).isoformat(),
                'model': model,
                'prompt_tokens': int(tokens * 0.7),
                'completion_tokens': int(tokens * 0.3),
                'total_tokens': tokens,
                'team': random.choice(self.teams),
                'cost': tokens / 1000 * random.uniform(0.01, 0.06),
                'request_id': f'req-{i}',
                'user': f'user-{random.randint(1, 20)}'
            }
            
            self.producer.send('ai-api-costs', value=event)
            
            # Generate anomaly for spikes
            if tokens > 10000:
                anomaly = {
                    'timestamp': event['timestamp'],
                    'type': 'api_spike',
                    'severity': 'critical',
                    'message': f"Unusual API usage: {tokens} tokens in single request",
                    'cost': event['cost'],
                    'team': event['team'],
                    'model': model
                }
                self.producer.send('cost-anomalies', value=anomaly)
        
        logger.info(f"Generated {count} API cost events")
    
    def generate_cost_summary(self):
        """Generate summary cost events"""
        logger.info("Generating cost summary events...")
        
        for team in self.teams:
            summary = {
                'timestamp': datetime.utcnow().isoformat(),
                'team': team,
                'gpu_cost_24h': random.uniform(100, 1000),
                'api_cost_24h': random.uniform(50, 500),
                'total_cost_24h': random.uniform(150, 1500),
                'cost_trend': random.choice(['increasing', 'stable', 'decreasing']),
                'budget_remaining': random.uniform(0, 5000),
                'budget_percentage_used': random.uniform(20, 95)
            }
            
            self.producer.send('ai-api-costs', value=summary)
    
    def run(self):
        """Generate all test data"""
        logger.info("Starting test data generation...")
        
        # Generate different types of events
        self.generate_gpu_events(100)
        self.generate_api_costs(200)
        self.generate_cost_summary()
        
        self.producer.flush()
        logger.info("Test data generation complete!")
        
        # Show some stats
        logger.info("\nGenerated:")
        logger.info("- 100 GPU utilization events")
        logger.info("- 200 AI API cost events")
        logger.info("- Cost anomalies for idle GPUs and API spikes")
        logger.info("- Team cost summaries")
        logger.info("\nData should now be visible in Grafana and OpenCost!")

if __name__ == "__main__":
    import sys
    
    kafka_servers = sys.argv[1] if len(sys.argv) > 1 else 'localhost:9092'
    
    generator = TestDataGenerator(kafka_bootstrap_servers=kafka_servers)
    generator.run()
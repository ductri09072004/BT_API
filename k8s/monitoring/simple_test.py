#!/usr/bin/env python3
"""
Simple Load Test - Test đơn giản nhất
"""

import requests
import time
import random

def simple_test():
    """Test đơn giản - gửi requests liên tục"""
    print("🔥 Simple Load Test Started!")
    print("📊 Sending requests to all services...")
    print("📈 Watch Grafana Dashboard for activity!")
    print("-" * 50)
    
    endpoints = [
        "http://localhost:8000/",           # Template
        "http://localhost:8001/orders",      # Order  
        "http://localhost:8002/customers",  # Customer
    ]
    
    request_count = 0
    
    try:
        while True:
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    request_count += 1
                    
                    status = "✅" if response.status_code == 200 else "❌"
                    print(f"{status} {endpoint} - #{request_count} - {response.status_code}")
                    
                except Exception as e:
                    print(f"💥 {endpoint} - Error: {e}")
                
                # Random delay
                time.sleep(random.uniform(0.5, 2.0))
                
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped after {request_count} requests")
        print("📊 Check Grafana Dashboard: http://localhost:3000")

if __name__ == "__main__":
    simple_test()

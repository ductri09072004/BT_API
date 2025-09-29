#!/usr/bin/env python3
"""
Quick Load Test - Test nhanh để tạo traffic
"""

import requests
import time
import threading
import random

def test_endpoint(url, duration=30):
    """Test một endpoint trong thời gian nhất định"""
    start_time = time.time()
    request_count = 0
    
    print(f"🚀 Testing {url} for {duration} seconds...")
    
    while time.time() - start_time < duration:
        try:
            response = requests.get(url, timeout=5)
            request_count += 1
            
            if response.status_code == 200:
                print(f"✅ {url} - Request #{request_count} - {response.status_code}")
            else:
                print(f"❌ {url} - Request #{request_count} - {response.status_code}")
                
        except Exception as e:
            print(f"💥 {url} - Error: {e}")
        
        # Random delay 0.1-1 giây
        time.sleep(random.uniform(0.1, 1.0))
    
    print(f"🏁 {url} - Completed {request_count} requests")

def main():
    print("🔥 Quick Load Test - BT_API Services")
    print("="*50)
    
    # Endpoints để test
    endpoints = [
        "http://localhost:8000/",           # Template service
        "http://localhost:8001/orders",     # Order service
        "http://localhost:8002/customers",  # Customer service
    ]
    
    duration = 60  # Test trong 60 giây
    
    print(f"⏱️  Duration: {duration} seconds")
    print(f"🎯 Endpoints: {len(endpoints)}")
    print("🚀 Starting load test...")
    print("-" * 50)
    
    # Tạo threads cho mỗi endpoint
    threads = []
    for endpoint in endpoints:
        thread = threading.Thread(target=test_endpoint, args=(endpoint, duration))
        threads.append(thread)
        thread.start()
    
    # Chờ tất cả threads hoàn thành
    for thread in threads:
        thread.join()
    
    print("\n🎉 Load test completed!")
    print("📊 Check Grafana Dashboard: http://localhost:3000")
    print("📈 You should see CPU and Memory graphs moving!")

if __name__ == "__main__":
    main()

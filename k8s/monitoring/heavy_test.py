#!/usr/bin/env python3
"""
Heavy Load Test - Tạo nhiều traffic để xem biểu đồ lên xuống rõ ràng
"""

import requests
import time
import threading
import random
import sys

def heavy_request(url, thread_id, duration=120):
    """Gửi requests nặng để tạo traffic"""
    start_time = time.time()
    request_count = 0
    
    print(f"🚀 Thread {thread_id} started - {url}")
    
    while time.time() - start_time < duration:
        try:
            # Gửi request
            response = requests.get(url, timeout=10)
            request_count += 1
            
            # In kết quả mỗi 10 requests
            if request_count % 10 == 0:
                status = "✅" if response.status_code == 200 else "❌"
                print(f"Thread {thread_id}: {status} {url} - #{request_count} - {response.status_code}")
            
        except Exception as e:
            print(f"Thread {thread_id}: 💥 {url} - Error: {e}")
        
        # Delay ngắn để tạo nhiều requests
        time.sleep(random.uniform(0.1, 0.5))
    
    print(f"🏁 Thread {thread_id} completed - {request_count} requests")

def main():
    print("🔥 HEAVY LOAD TEST - BT_API Services")
    print("="*60)
    print("📊 This will create heavy traffic to see graphs moving!")
    print("📈 Watch Grafana Dashboard: http://localhost:3000")
    print("⏱️  Duration: 2 minutes")
    print("🧵 Threads: 5 per service")
    print("-" * 60)
    
    # Endpoints
    endpoints = [
        "http://localhost:8000/",           # Template
        "http://localhost:8001/orders",      # Order
        "http://localhost:8002/customers",  # Customer
    ]
    
    # Tạo threads
    threads = []
    thread_id = 1
    
    for endpoint in endpoints:
        # 5 threads cho mỗi endpoint
        for i in range(5):
            thread = threading.Thread(
                target=heavy_request, 
                args=(endpoint, thread_id, 120)  # 2 phút
            )
            threads.append(thread)
            thread.start()
            thread_id += 1
    
    print(f"🚀 Started {len(threads)} threads")
    print("📊 Generating heavy traffic...")
    print("📈 Check Grafana Dashboard now!")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        # Chờ tất cả threads
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping load test...")
        print("📊 Check Grafana Dashboard for results!")

if __name__ == "__main__":
    main()

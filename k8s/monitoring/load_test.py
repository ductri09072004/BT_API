#!/usr/bin/env python3
"""
Load Testing Script cho BT_API Services
Test độ chịu tải và tạo traffic để xem biểu đồ lên xuống
"""

import asyncio
import aiohttp
import time
import random
import argparse
from datetime import datetime
import json

class LoadTester:
    def __init__(self, base_url="http://localhost", concurrent_users=10, duration=60):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.duration = duration
        self.results = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
        
        # API endpoints để test
        self.endpoints = [
            "/customers",      # Customer service
            "/orders",         # Order service  
            "/",               # Template service
        ]
        
        # Ports của các services
        self.ports = [8000, 8001, 8002]
    
    async def make_request(self, session, endpoint, port):
        """Thực hiện một request"""
        url = f"{self.base_url}:{port}{endpoint}"
        start_time = time.time()
        
        try:
            async with session.get(url, timeout=10) as response:
                response_time = time.time() - start_time
                self.results['response_times'].append(response_time)
                
                if response.status == 200:
                    self.results['successful_requests'] += 1
                    print(f"✅ {url} - {response.status} - {response_time:.3f}s")
                else:
                    self.results['failed_requests'] += 1
                    print(f"❌ {url} - {response.status} - {response_time:.3f}s")
                
                self.results['total_requests'] += 1
                
        except Exception as e:
            self.results['failed_requests'] += 1
            self.results['errors'].append(str(e))
            print(f"💥 {url} - ERROR: {e}")
    
    async def user_simulation(self, session, user_id):
        """Mô phỏng một user thực hiện requests"""
        start_time = time.time()
        
        while time.time() - start_time < self.duration:
            # Random endpoint và port
            endpoint = random.choice(self.endpoints)
            port = random.choice(self.ports)
            
            # Random delay giữa các requests (0.1-2 giây)
            delay = random.uniform(0.1, 2.0)
            await asyncio.sleep(delay)
            
            await self.make_request(session, endpoint, port)
    
    async def run_load_test(self):
        """Chạy load test"""
        print(f"🚀 Bắt đầu Load Test")
        print(f"📊 Concurrent Users: {self.concurrent_users}")
        print(f"⏱️  Duration: {self.duration} seconds")
        print(f"🎯 Endpoints: {self.endpoints}")
        print(f"🔌 Ports: {self.ports}")
        print("-" * 50)
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Tạo tasks cho concurrent users
            tasks = []
            for user_id in range(self.concurrent_users):
                task = asyncio.create_task(
                    self.user_simulation(session, user_id)
                )
                tasks.append(task)
            
            # Chạy tất cả tasks đồng thời
            await asyncio.gather(*tasks)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        # Tính toán kết quả
        self.calculate_results(actual_duration)
        self.print_results()
    
    def calculate_results(self, actual_duration):
        """Tính toán kết quả test"""
        self.results['actual_duration'] = actual_duration
        self.results['requests_per_second'] = self.results['total_requests'] / actual_duration
        
        if self.results['response_times']:
            self.results['avg_response_time'] = sum(self.results['response_times']) / len(self.results['response_times'])
            self.results['min_response_time'] = min(self.results['response_times'])
            self.results['max_response_time'] = max(self.results['response_times'])
        else:
            self.results['avg_response_time'] = 0
            self.results['min_response_time'] = 0
            self.results['max_response_time'] = 0
        
        self.results['success_rate'] = (self.results['successful_requests'] / self.results['total_requests']) * 100 if self.results['total_requests'] > 0 else 0
    
    def print_results(self):
        """In kết quả test"""
        print("\n" + "="*60)
        print("📈 LOAD TEST RESULTS")
        print("="*60)
        print(f"⏱️  Duration: {self.results['actual_duration']:.2f} seconds")
        print(f"📊 Total Requests: {self.results['total_requests']}")
        print(f"✅ Successful: {self.results['successful_requests']}")
        print(f"❌ Failed: {self.results['failed_requests']}")
        print(f"📈 Success Rate: {self.results['success_rate']:.2f}%")
        print(f"🚀 Requests/sec: {self.results['requests_per_second']:.2f}")
        print(f"⚡ Avg Response Time: {self.results['avg_response_time']:.3f}s")
        print(f"🏃 Min Response Time: {self.results['min_response_time']:.3f}s")
        print(f"🐌 Max Response Time: {self.results['max_response_time']:.3f}s")
        
        if self.results['errors']:
            print(f"\n💥 Errors ({len(self.results['errors'])}):")
            for error in self.results['errors'][:5]:  # Chỉ hiển thị 5 lỗi đầu
                print(f"   - {error}")
        
        print("\n🎯 Check Grafana Dashboard để xem biểu đồ lên xuống!")
        print("🌐 http://localhost:3000")

def main():
    parser = argparse.ArgumentParser(description='Load Test cho BT_API Services')
    parser.add_argument('--users', '-u', type=int, default=10, help='Số concurrent users (default: 10)')
    parser.add_argument('--duration', '-d', type=int, default=60, help='Thời gian test (seconds, default: 60)')
    parser.add_argument('--base-url', '-b', default='http://localhost', help='Base URL (default: http://localhost)')
    
    args = parser.parse_args()
    
    print("🔥 BT_API Load Testing Tool")
    print("="*40)
    
    # Tạo và chạy load test
    load_tester = LoadTester(
        base_url=args.base_url,
        concurrent_users=args.users,
        duration=args.duration
    )
    
    try:
        asyncio.run(load_tester.run_load_test())
    except KeyboardInterrupt:
        print("\n⏹️  Load test bị dừng bởi user")
    except Exception as e:
        print(f"\n💥 Lỗi: {e}")

if __name__ == "__main__":
    main()

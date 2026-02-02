"""
Resource Monitor
Monitor system resources for Raspberry Pi
"""

import psutil
import time
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ResourceMonitor:
    """
    Monitor system resources (CPU, RAM, Disk, Network)
    
    Features:
    - Real-time resource monitoring
    - Resource usage alerts
    - Performance logging
    - System health checks
    """
    
    def __init__(self,
                 cpu_threshold: float = 80.0,
                 memory_threshold: float = 80.0,
                 disk_threshold: float = 90.0):
        """
        Initialize resource monitor
        
        Args:
            cpu_threshold: CPU usage alert threshold (%)
            memory_threshold: Memory usage alert threshold (%)
            disk_threshold: Disk usage alert threshold (%)
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        
        logger.info("✅ Resource monitor initialized")
    
    def get_cpu_stats(self) -> Dict:
        """Get CPU statistics"""
        return {
            'percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count(),
            'freq_mhz': psutil.cpu_freq().current if psutil.cpu_freq() else 0
        }
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        mem = psutil.virtual_memory()
        
        return {
            'total_mb': mem.total / (1024 * 1024),
            'available_mb': mem.available / (1024 * 1024),
            'used_mb': mem.used / (1024 * 1024),
            'percent': mem.percent
        }
    
    def get_disk_stats(self, path: str = '/') -> Dict:
        """Get disk statistics"""
        disk = psutil.disk_usage(path)
        
        return {
            'total_gb': disk.total / (1024 * 1024 * 1024),
            'used_gb': disk.used / (1024 * 1024 * 1024),
            'free_gb': disk.free / (1024 * 1024 * 1024),
            'percent': disk.percent
        }
    
    def get_network_stats(self) -> Dict:
        """Get network statistics"""
        net = psutil.net_io_counters()
        
        return {
            'bytes_sent_mb': net.bytes_sent / (1024 * 1024),
            'bytes_recv_mb': net.bytes_recv / (1024 * 1024),
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv,
            'errors_in': net.errin,
            'errors_out': net.errout
        }
    
    def get_process_stats(self) -> Dict:
        """Get current process statistics"""
        process = psutil.Process()
        
        return {
            'cpu_percent': process.cpu_percent(interval=0.1),
            'memory_mb': process.memory_info().rss / (1024 * 1024),
            'memory_percent': process.memory_percent(),
            'num_threads': process.num_threads(),
            'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0
        }
    
    def get_temperature(self) -> Optional[float]:
        """Get CPU temperature (if available)"""
        try:
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps:
                return temps['cpu_thermal'][0].current
            elif 'coretemp' in temps:
                return temps['coretemp'][0].current
        except:
            pass
        return None
    
    def check_health(self) -> Dict:
        """
        Check system health
        
        Returns:
            Dictionary with health status and alerts
        """
        cpu = self.get_cpu_stats()
        memory = self.get_memory_stats()
        disk = self.get_disk_stats()
        
        alerts = []
        
        # Check CPU
        if cpu['percent'] > self.cpu_threshold:
            alerts.append(f"⚠️ High CPU usage: {cpu['percent']:.1f}%")
        
        # Check memory
        if memory['percent'] > self.memory_threshold:
            alerts.append(f"⚠️ High memory usage: {memory['percent']:.1f}%")
        
        # Check disk
        if disk['percent'] > self.disk_threshold:
            alerts.append(f"⚠️ High disk usage: {disk['percent']:.1f}%")
        
        # Get temperature
        temp = self.get_temperature()
        if temp and temp > 80.0:
            alerts.append(f"⚠️ High temperature: {temp:.1f}°C")
        
        return {
            'healthy': len(alerts) == 0,
            'alerts': alerts,
            'cpu_percent': cpu['percent'],
            'memory_percent': memory['percent'],
            'disk_percent': disk['percent'],
            'temperature': temp
        }
    
    def print_stats(self):
        """Print comprehensive resource statistics"""
        print("\n" + "="*70)
        print("📊 SYSTEM RESOURCE MONITOR")
        print("="*70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # CPU
        cpu = self.get_cpu_stats()
        print(f"\n🖥️ CPU:")
        print(f"  Usage:               {cpu['percent']:>8.1f}%")
        print(f"  Cores:               {cpu['count']:>8}")
        if cpu['freq_mhz'] > 0:
            print(f"  Frequency:           {cpu['freq_mhz']:>8.0f} MHz")
        
        # Temperature
        temp = self.get_temperature()
        if temp:
            print(f"  Temperature:         {temp:>8.1f}°C")
        
        # Memory
        memory = self.get_memory_stats()
        print(f"\n💾 Memory:")
        print(f"  Total:               {memory['total_mb']:>8.0f} MB")
        print(f"  Used:                {memory['used_mb']:>8.0f} MB")
        print(f"  Available:           {memory['available_mb']:>8.0f} MB")
        print(f"  Usage:               {memory['percent']:>8.1f}%")
        
        # Disk
        disk = self.get_disk_stats()
        print(f"\n💿 Disk:")
        print(f"  Total:               {disk['total_gb']:>8.1f} GB")
        print(f"  Used:                {disk['used_gb']:>8.1f} GB")
        print(f"  Free:                {disk['free_gb']:>8.1f} GB")
        print(f"  Usage:               {disk['percent']:>8.1f}%")
        
        # Network
        network = self.get_network_stats()
        print(f"\n🌐 Network:")
        print(f"  Sent:                {network['bytes_sent_mb']:>8.1f} MB")
        print(f"  Received:            {network['bytes_recv_mb']:>8.1f} MB")
        print(f"  Errors (in/out):     {network['errors_in']:>4}/{network['errors_out']:<4}")
        
        # Process
        process = self.get_process_stats()
        print(f"\n🤖 Bot Process:")
        print(f"  CPU:                 {process['cpu_percent']:>8.1f}%")
        print(f"  Memory:              {process['memory_mb']:>8.1f} MB ({process['memory_percent']:.1f}%)")
        print(f"  Threads:             {process['num_threads']:>8}")
        if process['num_fds'] > 0:
            print(f"  File Descriptors:    {process['num_fds']:>8}")
        
        # Health check
        health = self.check_health()
        print(f"\n🏥 Health Status:")
        if health['healthy']:
            print("  ✅ All systems normal")
        else:
            print("  ⚠️ Alerts detected:")
            for alert in health['alerts']:
                print(f"     {alert}")
        
        print("\n" + "="*70 + "\n")
    
    def monitor_continuous(self, interval: int = 60, duration: Optional[int] = None):
        """
        Continuous monitoring
        
        Args:
            interval: Seconds between checks
            duration: Total duration in seconds (None = infinite)
        """
        start_time = time.time()
        
        print(f"🔍 Starting continuous monitoring (interval={interval}s)")
        
        try:
            while True:
                self.print_stats()
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    break
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")


if __name__ == "__main__":
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("RESOURCE MONITOR TEST")
    print("="*70)
    
    # Initialize monitor
    monitor = ResourceMonitor(
        cpu_threshold=80.0,
        memory_threshold=80.0,
        disk_threshold=90.0
    )
    
    # Show current stats
    monitor.print_stats()
    
    # Check health
    health = monitor.check_health()
    if not health['healthy']:
        print("\n⚠️ System health alerts:")
        for alert in health['alerts']:
            print(f"  {alert}")
    
    # Continuous monitoring (if requested)
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        monitor.monitor_continuous(interval=interval)
    
    print("\n✅ Test completed!")

import psutil
import time
import platform
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

class SystemMonitor:
    """
    Comprehensive system monitoring class for Windows systems
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.cpu_history = []
        self.memory_history = []
        self.disk_history = []
        self.network_history = []
        self.max_history = 100  # Keep last 100 readings
        
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_history.append({
                'timestamp': datetime.now(),
                'value': cpu_percent
            })
            
            # Keep only recent history
            if len(self.cpu_history) > self.max_history:
                self.cpu_history.pop(0)
                
            return cpu_percent
        except Exception as e:
            raise Exception(f"Error getting CPU usage: {e}")
    
    def get_cpu_details(self) -> Dict[str, Any]:
        """Get detailed CPU information"""
        try:
            return {
                'percent': psutil.cpu_percent(interval=1),
                'count_logical': psutil.cpu_count(logical=True),
                'count_physical': psutil.cpu_count(logical=False),
                'freq_current': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'freq_max': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
                'per_cpu': psutil.cpu_percent(interval=1, percpu=True),
                'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            raise Exception(f"Error getting CPU details: {e}")
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_data = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent,
                'free': memory.free,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent
            }
            
            self.memory_history.append({
                'timestamp': datetime.now(),
                'value': memory.percent
            })
            
            # Keep only recent history
            if len(self.memory_history) > self.max_history:
                self.memory_history.pop(0)
                
            return memory_data
        except Exception as e:
            raise Exception(f"Error getting memory usage: {e}")
    
    def get_disk_usage(self) -> List[Dict[str, Any]]:
        """Get disk usage for all mounted drives"""
        try:
            disk_info = []
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
                    })
                except PermissionError:
                    # Skip drives that are not accessible
                    continue
                    
            return disk_info
        except Exception as e:
            raise Exception(f"Error getting disk usage: {e}")
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network interface statistics"""
        try:
            network_io = psutil.net_io_counters()
            network_if = psutil.net_if_stats()
            
            network_data = {
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv,
                'errors_in': network_io.errin,
                'errors_out': network_io.errout,
                'drops_in': network_io.dropin,
                'drops_out': network_io.dropout,
                'interfaces': {}
            }
            
            for interface, stats in network_if.items():
                network_data['interfaces'][interface] = {
                    'is_up': stats.isup,
                    'speed': stats.speed,
                    'mtu': stats.mtu
                }
                
            return network_data
        except Exception as e:
            raise Exception(f"Error getting network stats: {e}")
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Get list of running processes with detailed information"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'status', 'create_time', 'username']):
                try:
                    process_info = proc.info
                    
                    # Get additional process details
                    try:
                        process_info['cmdline'] = ' '.join(proc.cmdline())
                    except:
                        process_info['cmdline'] = 'N/A'
                    
                    try:
                        process_info['exe'] = proc.exe()
                    except:
                        process_info['exe'] = 'N/A'
                    
                    # Format memory info
                    if process_info['memory_info']:
                        process_info['memory_mb'] = process_info['memory_info'].rss / 1024 / 1024
                    else:
                        process_info['memory_mb'] = 0
                    
                    # Format create time
                    if process_info['create_time']:
                        process_info['create_time_formatted'] = datetime.fromtimestamp(
                            process_info['create_time']
                        ).strftime('%Y-%m-%d %H:%M:%S')
                    
                    processes.append(process_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            return sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)
        except Exception as e:
            raise Exception(f"Error getting running processes: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'platform': platform.platform(),
                'system': platform.system(),
                'node': platform.node(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                'uptime': str(uptime).split('.')[0],  # Remove microseconds
                'users': [{'name': user.name, 'terminal': user.terminal, 
                          'host': user.host, 'started': datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')} 
                         for user in psutil.users()]
            }
        except Exception as e:
            raise Exception(f"Error getting system info: {e}")
    
    def get_temperature_sensors(self) -> Dict[str, Any]:
        """Get temperature sensor readings (if available)"""
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                return temps if temps else {}
            return {}
        except Exception:
            return {}
    
    def get_battery_info(self) -> Dict[str, Any]:
        """Get battery information (for laptops)"""
        try:
            if hasattr(psutil, 'sensors_battery'):
                battery = psutil.sensors_battery()
                if battery:
                    return {
                        'percent': battery.percent,
                        'power_plugged': battery.power_plugged,
                        'seconds_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                    }
            return {}
        except Exception:
            return {}
    
    def detect_issues(self) -> List[Dict[str, Any]]:
        """Detect system issues based on thresholds"""
        issues = []
        
        try:
            # CPU usage check
            cpu_percent = self.get_cpu_usage()
            if cpu_percent > 90:
                issues.append({
                    'type': 'critical',
                    'category': 'cpu',
                    'message': f'Critical CPU usage: {cpu_percent:.1f}%',
                    'severity': 'high',
                    'timestamp': datetime.now().isoformat()
                })
            elif cpu_percent > 75:
                issues.append({
                    'type': 'warning',
                    'category': 'cpu',
                    'message': f'High CPU usage: {cpu_percent:.1f}%',
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Memory usage check
            memory = self.get_memory_usage()
            if memory['percent'] > 95:
                issues.append({
                    'type': 'critical',
                    'category': 'memory',
                    'message': f'Critical memory usage: {memory["percent"]:.1f}%',
                    'severity': 'high',
                    'timestamp': datetime.now().isoformat()
                })
            elif memory['percent'] > 85:
                issues.append({
                    'type': 'warning',
                    'category': 'memory',
                    'message': f'High memory usage: {memory["percent"]:.1f}%',
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Disk usage check
            disks = self.get_disk_usage()
            for disk in disks:
                if disk['percent'] > 95:
                    issues.append({
                        'type': 'critical',
                        'category': 'disk',
                        'message': f'Critical disk usage on {disk["device"]}: {disk["percent"]:.1f}%',
                        'severity': 'high',
                        'timestamp': datetime.now().isoformat()
                    })
                elif disk['percent'] > 85:
                    issues.append({
                        'type': 'warning',
                        'category': 'disk',
                        'message': f'High disk usage on {disk["device"]}: {disk["percent"]:.1f}%',
                        'severity': 'medium',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Check for unresponsive processes
            processes = self.get_running_processes()
            for proc in processes:
                if proc.get('status') == 'zombie':
                    issues.append({
                        'type': 'warning',
                        'category': 'process',
                        'message': f'Zombie process detected: {proc["name"]} (PID: {proc["pid"]})',
                        'severity': 'medium',
                        'timestamp': datetime.now().isoformat()
                    })
                elif proc.get('cpu_percent', 0) > 50 and proc.get('name') not in ['System Idle Process', 'System']:
                    issues.append({
                        'type': 'warning',
                        'category': 'process',
                        'message': f'High CPU process: {proc["name"]} using {proc["cpu_percent"]:.1f}% CPU',
                        'severity': 'medium',
                        'timestamp': datetime.now().isoformat()
                    })
                    
        except Exception as e:
            issues.append({
                'type': 'error',
                'category': 'system',
                'message': f'Error during system monitoring: {e}',
                'severity': 'high',
                'timestamp': datetime.now().isoformat()
            })
        
        return issues
    
    def generate_system_report(self) -> str:
        """Generate a comprehensive system report"""
        try:
            report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            report = f"""
SYSTEM MONITORING REPORT
Generated: {report_time}
{'='*50}

SYSTEM INFORMATION:
{'-'*20}
"""
            
            # System info
            sys_info = self.get_system_info()
            for key, value in sys_info.items():
                if key != 'users':
                    report += f"{key.replace('_', ' ').title()}: {value}\n"
            
            # CPU Information
            report += f"\nCPU INFORMATION:\n{'-'*20}\n"
            cpu_info = self.get_cpu_details()
            report += f"Usage: {cpu_info['percent']:.1f}%\n"
            report += f"Logical Cores: {cpu_info['count_logical']}\n"
            report += f"Physical Cores: {cpu_info['count_physical']}\n"
            if cpu_info['freq_current']:
                report += f"Current Frequency: {cpu_info['freq_current']:.0f} MHz\n"
            
            # Memory Information
            report += f"\nMEMORY INFORMATION:\n{'-'*20}\n"
            memory_info = self.get_memory_usage()
            report += f"Total: {memory_info['total'] / (1024**3):.2f} GB\n"
            report += f"Used: {memory_info['used'] / (1024**3):.2f} GB ({memory_info['percent']:.1f}%)\n"
            report += f"Available: {memory_info['available'] / (1024**3):.2f} GB\n"
            
            # Disk Information
            report += f"\nDISK INFORMATION:\n{'-'*20}\n"
            disk_info = self.get_disk_usage()
            for disk in disk_info:
                report += f"Drive {disk['device']}: {disk['used'] / (1024**3):.2f} GB / {disk['total'] / (1024**3):.2f} GB ({disk['percent']:.1f}%)\n"
            
            # Network Information
            report += f"\nNETWORK INFORMATION:\n{'-'*20}\n"
            network_info = self.get_network_stats()
            report += f"Bytes Sent: {network_info['bytes_sent'] / (1024**2):.2f} MB\n"
            report += f"Bytes Received: {network_info['bytes_recv'] / (1024**2):.2f} MB\n"
            
            # Top Processes
            report += f"\nTOP PROCESSES (by CPU usage):\n{'-'*20}\n"
            processes = self.get_running_processes()[:10]
            for proc in processes:
                report += f"{proc['name']} (PID: {proc['pid']}): CPU {proc.get('cpu_percent', 0):.1f}%, Memory {proc.get('memory_percent', 0):.1f}%\n"
            
            # Current Issues
            report += f"\nCURRENT ISSUES:\n{'-'*20}\n"
            issues = self.detect_issues()
            if issues:
                for issue in issues:
                    report += f"[{issue['type'].upper()}] {issue['message']}\n"
            else:
                report += "No issues detected.\n"
            
            report += f"\n{'='*50}\nReport End\n"
            
            return report
            
        except Exception as e:
            return f"Error generating system report: {e}"

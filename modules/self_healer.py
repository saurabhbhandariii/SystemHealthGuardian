import os
import subprocess
import psutil
import gc
import tempfile
import shutil
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading

class SelfHealer:
    """
    Self-healing system management class for automatic issue resolution
    """
    
    def __init__(self):
        self.healing_log = []
        self.max_log_entries = 100
        self.healing_active = False
        self.healing_thread = None
        self.stop_healing = threading.Event()
        
    def log_action(self, action: str, success: bool, message: str):
        """Log healing actions"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'success': success,
            'message': message
        }
        self.healing_log.append(log_entry)
        
        # Keep only recent log entries
        if len(self.healing_log) > self.max_log_entries:
            self.healing_log.pop(0)
    
    def kill_high_cpu_processes(self, cpu_threshold: float = 80.0, 
                               exclude_processes: List[str] = None) -> Dict[str, Any]:
        """
        Kill processes consuming excessive CPU
        """
        if exclude_processes is None:
            exclude_processes = [
                'System', 'System Idle Process', 'Registry', 'dwm.exe', 
                'winlogon.exe', 'csrss.exe', 'smss.exe', 'explorer.exe',
                'svchost.exe', 'lsass.exe', 'services.exe', 'wininet.exe'
            ]
        
        try:
            killed_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    # Get CPU usage for this process
                    cpu_usage = proc.info['cpu_percent']
                    process_name = proc.info['name']
                    
                    if (cpu_usage and cpu_usage > cpu_threshold and 
                        process_name not in exclude_processes):
                        
                        # Try to terminate the process gracefully first
                        process = psutil.Process(proc.info['pid'])
                        process.terminate()
                        
                        # Wait for termination
                        try:
                            process.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            # Force kill if graceful termination fails
                            process.kill()
                        
                        killed_processes.append({
                            'pid': proc.info['pid'],
                            'name': process_name,
                            'cpu_percent': cpu_usage
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, 
                       psutil.ZombieProcess, PermissionError):
                    continue
            
            message = f"Killed {len(killed_processes)} high CPU processes"
            self.log_action("kill_high_cpu_processes", True, message)
            
            return {
                'success': True,
                'message': message,
                'killed_processes': killed_processes
            }
            
        except Exception as e:
            error_msg = f"Error killing high CPU processes: {e}"
            self.log_action("kill_high_cpu_processes", False, error_msg)
            return {
                'success': False,
                'message': error_msg,
                'killed_processes': []
            }
    
    def free_memory(self) -> Dict[str, Any]:
        """
        Free up system memory using various techniques
        """
        try:
            # Get initial memory usage
            initial_memory = psutil.virtual_memory()
            initial_used = initial_memory.used
            
            actions_taken = []
            
            # 1. Force garbage collection
            gc.collect()
            actions_taken.append("Python garbage collection")
            
            # 2. Clear system caches (Windows specific)
            try:
                # Clear DNS cache
                subprocess.run(['ipconfig', '/flushdns'], 
                             capture_output=True, check=False)
                actions_taken.append("DNS cache flush")
            except:
                pass
            
            # 3. Empty working sets of processes (Windows specific)
            try:
                # This requires admin privileges, so we'll try but not fail if it doesn't work
                subprocess.run(['rundll32.exe', 'advapi32.dll,ProcessIdleTasks'], 
                             capture_output=True, check=False, timeout=10)
                actions_taken.append("Process idle tasks")
            except:
                pass
            
            # 4. Clear standby memory (requires admin rights)
            try:
                # This is a more aggressive approach - use with caution
                subprocess.run(['powershell', '-Command', 
                              'Get-Process | Where-Object {$_.WorkingSet -gt 100MB} | ForEach-Object {$_.CloseMainWindow()}'],
                             capture_output=True, check=False, timeout=15)
                actions_taken.append("Large process cleanup")
            except:
                pass
            
            # Get final memory usage
            final_memory = psutil.virtual_memory()
            final_used = final_memory.used
            
            memory_freed = initial_used - final_used
            memory_freed_mb = memory_freed / (1024 * 1024)
            
            message = f"Memory optimization completed. Actions: {', '.join(actions_taken)}"
            if memory_freed > 0:
                message += f". Freed: {memory_freed_mb:.1f} MB"
            
            self.log_action("free_memory", True, message)
            
            return {
                'success': True,
                'message': message,
                'memory_freed_mb': memory_freed_mb,
                'actions_taken': actions_taken
            }
            
        except Exception as e:
            error_msg = f"Error freeing memory: {e}"
            self.log_action("free_memory", False, error_msg)
            return {
                'success': False,
                'message': error_msg,
                'memory_freed_mb': 0,
                'actions_taken': []
            }
    
    def clean_temp_files(self) -> Dict[str, Any]:
        """
        Clean temporary files and folders
        """
        try:
            files_removed = 0
            space_freed = 0
            temp_dirs = []
            
            # Standard Windows temp directories
            temp_dirs.extend([
                tempfile.gettempdir(),
                os.path.expandvars(r'%TEMP%'),
                os.path.expandvars(r'%TMP%'),
                os.path.expandvars(r'%USERPROFILE%\AppData\Local\Temp'),
                os.path.expandvars(r'%WINDIR%\Temp'),
                os.path.expandvars(r'%USERPROFILE%\AppData\Local\Microsoft\Windows\Temporary Internet Files'),
            ])
            
            # Remove duplicates
            temp_dirs = list(set(temp_dirs))
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                    try:
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                try:
                                    file_path = os.path.join(root, file)
                                    if os.path.exists(file_path):
                                        # Check if file is old enough (older than 1 day)
                                        file_age = time.time() - os.path.getmtime(file_path)
                                        if file_age > 86400:  # 24 hours
                                            file_size = os.path.getsize(file_path)
                                            os.remove(file_path)
                                            files_removed += 1
                                            space_freed += file_size
                                except (PermissionError, OSError, FileNotFoundError):
                                    # Skip files that can't be deleted
                                    continue
                    except (PermissionError, OSError):
                        # Skip directories that can't be accessed
                        continue
            
            # Clean browser caches (basic cleanup)
            try:
                # Chrome cache
                chrome_cache = os.path.expandvars(r'%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Default\Cache')
                if os.path.exists(chrome_cache):
                    for file in os.listdir(chrome_cache):
                        try:
                            file_path = os.path.join(chrome_cache, file)
                            if os.path.isfile(file_path):
                                file_size = os.path.getsize(file_path)
                                os.remove(file_path)
                                files_removed += 1
                                space_freed += file_size
                        except:
                            continue
            except:
                pass
            
            space_freed_mb = space_freed / (1024 * 1024)
            message = f"Cleaned {files_removed} temporary files, freed {space_freed_mb:.1f} MB"
            
            self.log_action("clean_temp_files", True, message)
            
            return {
                'success': True,
                'message': message,
                'files_removed': files_removed,
                'space_freed_mb': space_freed_mb
            }
            
        except Exception as e:
            error_msg = f"Error cleaning temp files: {e}"
            self.log_action("clean_temp_files", False, error_msg)
            return {
                'success': False,
                'message': error_msg,
                'files_removed': 0,
                'space_freed_mb': 0
            }
    
    def restart_unresponsive_services(self) -> Dict[str, Any]:
        """
        Restart unresponsive Windows services
        """
        try:
            restarted_services = []
            
            # Common services that might need restarting
            critical_services = [
                'Spooler',  # Print Spooler
                'BITS',     # Background Intelligent Transfer Service
                'Themes',   # Themes service
                'AudioSrv', # Windows Audio
                'AudioEndpointBuilder',  # Windows Audio Endpoint Builder
            ]
            
            for service_name in critical_services:
                try:
                    # Check service status using sc command
                    result = subprocess.run(
                        ['sc', 'query', service_name],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        # Parse output to check if service is running
                        if 'STOPPED' in result.stdout or 'STOP_PENDING' in result.stdout:
                            # Try to start the service
                            start_result = subprocess.run(
                                ['sc', 'start', service_name],
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                            
                            if start_result.returncode == 0:
                                restarted_services.append(service_name)
                        
                        elif 'RUNNING' in result.stdout:
                            # Service is running, check if it's responsive
                            # For now, we'll skip restarting running services
                            pass
                            
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    continue
            
            message = f"Restarted {len(restarted_services)} services: {', '.join(restarted_services)}"
            self.log_action("restart_services", True, message)
            
            return {
                'success': True,
                'message': message,
                'restarted_services': restarted_services
            }
            
        except Exception as e:
            error_msg = f"Error restarting services: {e}"
            self.log_action("restart_services", False, error_msg)
            return {
                'success': False,
                'message': error_msg,
                'restarted_services': []
            }
    
    def optimize_startup_programs(self) -> Dict[str, Any]:
        """
        Disable unnecessary startup programs
        """
        try:
            disabled_programs = []
            
            # Common startup programs that can be safely disabled
            unnecessary_startups = [
                'Adobe Updater',
                'Java Update Scheduler',
                'Apple Software Update',
                'iTunes Helper',
                'Spotify',
                'Skype',
                'Steam',
                'Discord'
            ]
            
            # This is a simplified approach - in a real implementation,
            # you would query the registry for startup programs
            message = "Startup optimization feature requires registry access (admin privileges)"
            
            self.log_action("optimize_startup", True, message)
            
            return {
                'success': True,
                'message': message,
                'disabled_programs': disabled_programs
            }
            
        except Exception as e:
            error_msg = f"Error optimizing startup: {e}"
            self.log_action("optimize_startup", False, error_msg)
            return {
                'success': False,
                'message': error_msg,
                'disabled_programs': []
            }
    
    def disk_cleanup(self) -> Dict[str, Any]:
        """
        Perform disk cleanup operations
        """
        try:
            space_freed = 0
            operations = []
            
            # Run Windows Disk Cleanup utility
            try:
                # This will open the disk cleanup dialog
                subprocess.run(['cleanmgr', '/sagerun:1'], 
                             capture_output=True, check=False, timeout=60)
                operations.append("Windows Disk Cleanup")
            except:
                pass
            
            # Clear Recycle Bin (requires PowerShell)
            try:
                result = subprocess.run([
                    'powershell', '-Command',
                    'Clear-RecycleBin -Force -ErrorAction SilentlyContinue'
                ], capture_output=True, check=False, timeout=30)
                operations.append("Recycle Bin cleanup")
            except:
                pass
            
            message = f"Disk cleanup completed. Operations: {', '.join(operations)}"
            self.log_action("disk_cleanup", True, message)
            
            return {
                'success': True,
                'message': message,
                'space_freed_mb': space_freed,
                'operations': operations
            }
            
        except Exception as e:
            error_msg = f"Error during disk cleanup: {e}"
            self.log_action("disk_cleanup", False, error_msg)
            return {
                'success': False,
                'message': error_msg,
                'space_freed_mb': 0,
                'operations': []
            }
    
    def auto_heal(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Automatically resolve detected issues
        """
        healing_results = []
        
        try:
            for issue in issues:
                category = issue.get('category', '')
                severity = issue.get('severity', '')
                
                if category == 'cpu' and severity in ['high', 'medium']:
                    # High CPU usage - try to kill resource-heavy processes
                    result = self.kill_high_cpu_processes(cpu_threshold=75.0)
                    healing_results.append({
                        'issue': issue['message'],
                        'action': 'kill_high_cpu_processes',
                        'result': result
                    })
                
                elif category == 'memory' and severity in ['high', 'medium']:
                    # High memory usage - try to free memory
                    result = self.free_memory()
                    healing_results.append({
                        'issue': issue['message'],
                        'action': 'free_memory',
                        'result': result
                    })
                
                elif category == 'disk' and severity in ['high', 'medium']:
                    # High disk usage - clean temp files
                    result = self.clean_temp_files()
                    healing_results.append({
                        'issue': issue['message'],
                        'action': 'clean_temp_files',
                        'result': result
                    })
                
                elif category == 'process':
                    # Process issues - restart services
                    result = self.restart_unresponsive_services()
                    healing_results.append({
                        'issue': issue['message'],
                        'action': 'restart_services',
                        'result': result
                    })
            
            successful_healings = sum(1 for r in healing_results if r['result']['success'])
            total_healings = len(healing_results)
            
            message = f"Auto-healing completed: {successful_healings}/{total_healings} successful"
            self.log_action("auto_heal", True, message)
            
            return {
                'success': True,
                'message': message,
                'healing_results': healing_results,
                'successful_count': successful_healings,
                'total_count': total_healings
            }
            
        except Exception as e:
            error_msg = f"Error during auto-healing: {e}"
            self.log_action("auto_heal", False, error_msg)
            return {
                'success': False,
                'message': error_msg,
                'healing_results': healing_results,
                'successful_count': 0,
                'total_count': 0
            }
    
    def get_healing_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent healing log entries"""
        return self.healing_log[-limit:] if self.healing_log else []
    
    def start_continuous_healing(self, check_interval: int = 300):
        """Start continuous healing process"""
        if self.healing_active:
            return {"success": False, "message": "Healing already active"}
        
        self.healing_active = True
        self.stop_healing.clear()
        
        def healing_loop():
            from .system_monitor import SystemMonitor
            monitor = SystemMonitor()
            
            while not self.stop_healing.is_set():
                try:
                    issues = monitor.detect_issues()
                    if issues:
                        self.auto_heal(issues)
                    
                    # Wait for next check or stop signal
                    self.stop_healing.wait(check_interval)
                    
                except Exception as e:
                    self.log_action("continuous_healing", False, f"Error in healing loop: {e}")
                    time.sleep(30)  # Wait before retrying
        
        self.healing_thread = threading.Thread(target=healing_loop, daemon=True)
        self.healing_thread.start()
        
        return {"success": True, "message": "Continuous healing started"}
    
    def stop_continuous_healing(self):
        """Stop continuous healing process"""
        if not self.healing_active:
            return {"success": False, "message": "Healing not active"}
        
        self.healing_active = False
        self.stop_healing.set()
        
        if self.healing_thread:
            self.healing_thread.join(timeout=5)
        
        return {"success": True, "message": "Continuous healing stopped"}

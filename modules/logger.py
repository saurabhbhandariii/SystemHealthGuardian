import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
from logging.handlers import RotatingFileHandler

class SystemLogger:
    """
    Comprehensive logging system for system monitoring activities
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.ensure_log_directory()
        self.loggers = {}
        self.activity_log = []
        self.max_activity_entries = 1000
        self.setup_loggers()
        
    def ensure_log_directory(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def setup_loggers(self):
        """Setup different loggers for various components"""
        
        # Main system logger
        self.loggers['system'] = self._create_logger(
            'system', 
            os.path.join(self.log_dir, 'system.log'),
            logging.INFO
        )
        
        # Monitoring logger
        self.loggers['monitoring'] = self._create_logger(
            'monitoring',
            os.path.join(self.log_dir, 'monitoring.log'),
            logging.DEBUG
        )
        
        # Healing logger
        self.loggers['healing'] = self._create_logger(
            'healing',
            os.path.join(self.log_dir, 'healing.log'),
            logging.INFO
        )
        
        # Alert logger
        self.loggers['alerts'] = self._create_logger(
            'alerts',
            os.path.join(self.log_dir, 'alerts.log'),
            logging.INFO
        )
        
        # Error logger
        self.loggers['errors'] = self._create_logger(
            'errors',
            os.path.join(self.log_dir, 'errors.log'),
            logging.ERROR
        )
        
        # Performance logger
        self.loggers['performance'] = self._create_logger(
            'performance',
            os.path.join(self.log_dir, 'performance.log'),
            logging.INFO
        )
    
    def _create_logger(self, name: str, filename: str, level: int) -> logging.Logger:
        """Create a logger with rotating file handler"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create rotating file handler (max 10MB, keep 5 backups)
        handler = RotatingFileHandler(
            filename, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def log_system_event(self, event_type: str, message: str, details: Dict[str, Any] = None):
        """Log a system event"""
        self.loggers['system'].info(f"[{event_type}] {message}")
        
        if details:
            self.loggers['system'].debug(f"Details: {json.dumps(details, indent=2)}")
        
        self._add_to_activity_log('system', event_type, message, details)
    
    def log_monitoring_data(self, component: str, data: Dict[str, Any]):
        """Log monitoring data"""
        message = f"Monitoring data for {component}"
        self.loggers['monitoring'].debug(f"{message}: {json.dumps(data, default=str)}")
        
        self._add_to_activity_log('monitoring', component, message, data)
    
    def log_healing_action(self, action: str, success: bool, message: str, details: Dict[str, Any] = None):
        """Log a healing action"""
        level = 'INFO' if success else 'WARNING'
        status = 'SUCCESS' if success else 'FAILED'
        
        log_message = f"[{action}] {status}: {message}"
        
        if success:
            self.loggers['healing'].info(log_message)
        else:
            self.loggers['healing'].warning(log_message)
        
        if details:
            self.loggers['healing'].debug(f"Details: {json.dumps(details, default=str)}")
        
        self._add_to_activity_log('healing', action, message, {
            'success': success,
            'details': details
        })
    
    def log_alert(self, alert: Dict[str, Any]):
        """Log an alert"""
        message = f"[{alert['severity'].upper()}] {alert['category']}: {alert['message']}"
        
        if alert['severity'] == 'critical':
            self.loggers['alerts'].error(message)
        elif alert['severity'] == 'warning':
            self.loggers['alerts'].warning(message)
        else:
            self.loggers['alerts'].info(message)
        
        self._add_to_activity_log('alerts', alert['category'], alert['message'], alert)
    
    def log_error(self, component: str, error: Exception, context: str = ""):
        """Log an error"""
        error_message = f"[{component}] {context}: {str(error)}"
        self.loggers['errors'].error(error_message, exc_info=True)
        
        self._add_to_activity_log('errors', component, error_message, {
            'error_type': type(error).__name__,
            'context': context
        })
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "", 
                              component: str = "system"):
        """Log a performance metric"""
        message = f"[{component}] {metric_name}: {value} {unit}".strip()
        self.loggers['performance'].info(message)
        
        self._add_to_activity_log('performance', metric_name, message, {
            'value': value,
            'unit': unit,
            'component': component
        })
    
    def _add_to_activity_log(self, log_type: str, category: str, message: str, 
                            details: Dict[str, Any] = None):
        """Add entry to in-memory activity log"""
        activity_entry = {
            'timestamp': datetime.now().isoformat(),
            'log_type': log_type,
            'category': category,
            'message': message,
            'details': details or {}
        }
        
        self.activity_log.append(activity_entry)
        
        # Keep only recent entries
        if len(self.activity_log) > self.max_activity_entries:
            self.activity_log.pop(0)
    
    def get_recent_activity(self, limit: int = 50, log_type: str = None) -> List[Dict[str, Any]]:
        """Get recent activity log entries"""
        filtered_log = self.activity_log
        
        if log_type:
            filtered_log = [entry for entry in filtered_log if entry['log_type'] == log_type]
        
        # Sort by timestamp (newest first)
        filtered_log.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return filtered_log[:limit]
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        stats = {
            'total_entries': len(self.activity_log),
            'last_hour': 0,
            'last_day': 0,
            'by_type': {},
            'by_category': {},
            'log_files': {}
        }
        
        # Count entries by time period and type
        for entry in self.activity_log:
            entry_time = datetime.fromisoformat(entry['timestamp'])
            
            if entry_time > last_hour:
                stats['last_hour'] += 1
            if entry_time > last_day:
                stats['last_day'] += 1
            
            # Count by type
            log_type = entry['log_type']
            stats['by_type'][log_type] = stats['by_type'].get(log_type, 0) + 1
            
            # Count by category
            category = entry['category']
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        # Get log file sizes
        for log_name in self.loggers.keys():
            log_file = os.path.join(self.log_dir, f"{log_name}.log")
            if os.path.exists(log_file):
                size_bytes = os.path.getsize(log_file)
                stats['log_files'][log_name] = {
                    'size_bytes': size_bytes,
                    'size_mb': size_bytes / (1024 * 1024),
                    'last_modified': datetime.fromtimestamp(
                        os.path.getmtime(log_file)
                    ).isoformat()
                }
        
        return stats
    
    def search_logs(self, query: str, log_type: str = None, 
                   start_date: datetime = None, end_date: datetime = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """Search log entries"""
        results = []
        
        for entry in self.activity_log:
            # Filter by log type
            if log_type and entry['log_type'] != log_type:
                continue
            
            # Filter by date range
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if start_date and entry_time < start_date:
                continue
            if end_date and entry_time > end_date:
                continue
            
            # Search in message and details
            if (query.lower() in entry['message'].lower() or
                query.lower() in str(entry['details']).lower()):
                results.append(entry)
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return results[:limit]
    
    def export_logs(self, log_type: str = None, format: str = 'json', 
                   start_date: datetime = None, end_date: datetime = None) -> str:
        """Export log entries"""
        entries = self.get_recent_activity(limit=self.max_activity_entries, log_type=log_type)
        
        # Filter by date range if specified
        if start_date or end_date:
            filtered_entries = []
            for entry in entries:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if start_date and entry_time < start_date:
                    continue
                if end_date and entry_time > end_date:
                    continue
                filtered_entries.append(entry)
            entries = filtered_entries
        
        if format.lower() == 'json':
            return json.dumps(entries, indent=2, default=str)
        elif format.lower() == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            if entries:
                fieldnames = ['timestamp', 'log_type', 'category', 'message']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for entry in entries:
                    row = {
                        'timestamp': entry['timestamp'],
                        'log_type': entry['log_type'],
                        'category': entry['category'],
                        'message': entry['message']
                    }
                    writer.writerow(row)
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old log entries from memory"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        self.activity_log = [
            entry for entry in self.activity_log
            if datetime.fromisoformat(entry['timestamp']) > cutoff_date
        ]
        
        self.log_system_event('cleanup', f"Cleaned up log entries older than {days} days")
    
    def get_log_file_content(self, log_name: str, lines: int = 100) -> str:
        """Get recent content from a log file"""
        log_file = os.path.join(self.log_dir, f"{log_name}.log")
        
        if not os.path.exists(log_file):
            return f"Log file {log_name}.log not found"
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                # Read all lines and return the last N lines
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(recent_lines)
        except Exception as e:
            return f"Error reading log file: {e}"

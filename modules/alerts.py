import smtplib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time

class AlertManager:
    """
    Alert management system for system monitoring
    """
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = self.load_default_rules()
        self.notification_settings = self.load_notification_settings()
        self.max_alerts = 1000
        self.alert_thread = None
        self.alert_active = False
        
    def load_default_rules(self) -> Dict[str, Any]:
        """Load default alerting rules"""
        return {
            'cpu': {
                'warning_threshold': 75.0,
                'critical_threshold': 90.0,
                'check_interval': 60,  # seconds
                'consecutive_checks': 2
            },
            'memory': {
                'warning_threshold': 85.0,
                'critical_threshold': 95.0,
                'check_interval': 60,
                'consecutive_checks': 2
            },
            'disk': {
                'warning_threshold': 85.0,
                'critical_threshold': 95.0,
                'check_interval': 300,  # 5 minutes
                'consecutive_checks': 1
            },
            'process': {
                'max_cpu_per_process': 80.0,
                'max_memory_per_process': 2048,  # MB
                'check_interval': 120,
                'consecutive_checks': 3
            },
            'network': {
                'max_error_rate': 5.0,  # percentage
                'check_interval': 180,
                'consecutive_checks': 2
            }
        }
    
    def load_notification_settings(self) -> Dict[str, Any]:
        """Load notification settings"""
        return {
            'email': {
                'enabled': False,
                'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'username': os.getenv('EMAIL_USERNAME', ''),
                'password': os.getenv('EMAIL_PASSWORD', ''),
                'recipients': os.getenv('EMAIL_RECIPIENTS', '').split(',') if os.getenv('EMAIL_RECIPIENTS') else []
            },
            'desktop': {
                'enabled': True,
                'show_warnings': True,
                'show_critical': True
            },
            'sound': {
                'enabled': True,
                'warning_sound': True,
                'critical_sound': True
            }
        }
    
    def add_alert(self, alert_type: str, category: str, message: str, 
                  severity: str = 'info', metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a new alert"""
        alert = {
            'id': f"{int(time.time())}-{len(self.alerts)}",
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'category': category,
            'message': message,
            'severity': severity,
            'acknowledged': False,
            'resolved': False,
            'metadata': metadata or {}
        }
        
        self.alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        # Send notifications
        self._send_notifications(alert)
        
        return alert
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_at'] = datetime.now().isoformat()
                return True
        return False
    
    def resolve_alert(self, alert_id: str, resolution_note: str = "") -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['resolved'] = True
                alert['resolved_at'] = datetime.now().isoformat()
                alert['resolution_note'] = resolution_note
                return True
        return False
    
    def get_alerts(self, category: str = None, severity: str = None, 
                   resolved: bool = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering"""
        filtered_alerts = self.alerts
        
        if category:
            filtered_alerts = [a for a in filtered_alerts if a['category'] == category]
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a['severity'] == severity]
        
        if resolved is not None:
            filtered_alerts = [a for a in filtered_alerts if a['resolved'] == resolved]
        
        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return filtered_alerts[:limit]
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return self.get_alerts(limit=limit)
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get unresolved alerts"""
        return self.get_alerts(resolved=False)
    
    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Get critical severity alerts"""
        return self.get_alerts(severity='critical', resolved=False)
    
    def clear_old_alerts(self, days: int = 7):
        """Clear alerts older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        self.alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_date
        ]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        now = datetime.now()
        
        # Count alerts by time period
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        last_week = now - timedelta(weeks=1)
        
        stats = {
            'total_alerts': len(self.alerts),
            'active_alerts': len(self.get_active_alerts()),
            'critical_alerts': len(self.get_critical_alerts()),
            'alerts_last_hour': 0,
            'alerts_last_day': 0,
            'alerts_last_week': 0,
            'by_category': {},
            'by_severity': {}
        }
        
        # Count by time periods and categories
        for alert in self.alerts:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            
            if alert_time > last_hour:
                stats['alerts_last_hour'] += 1
            if alert_time > last_day:
                stats['alerts_last_day'] += 1
            if alert_time > last_week:
                stats['alerts_last_week'] += 1
            
            # Count by category
            category = alert['category']
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            # Count by severity
            severity = alert['severity']
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
        
        return stats
    
    def _send_notifications(self, alert: Dict[str, Any]):
        """Send notifications for an alert"""
        try:
            # Desktop notification
            if self.notification_settings['desktop']['enabled']:
                self._send_desktop_notification(alert)
            
            # Sound notification
            if self.notification_settings['sound']['enabled']:
                self._play_alert_sound(alert)
            
            # Email notification
            if self.notification_settings['email']['enabled']:
                self._send_email_notification(alert)
                
        except Exception as e:
            print(f"Error sending notifications: {e}")
    
    def _send_desktop_notification(self, alert: Dict[str, Any]):
        """Send desktop notification (Windows)"""
        try:
            import subprocess
            
            # Use PowerShell to show Windows toast notification
            title = f"System Alert - {alert['severity'].title()}"
            message = alert['message']
            
            # Create PowerShell script for toast notification
            ps_script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.SystemIcons]::Warning
            $notification.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Warning
            $notification.BalloonTipText = "{message}"
            $notification.BalloonTipTitle = "{title}"
            $notification.Visible = $true
            $notification.ShowBalloonTip(5000)
            """
            
            subprocess.run([
                'powershell', '-Command', ps_script
            ], capture_output=True, check=False, timeout=10)
            
        except Exception as e:
            print(f"Error sending desktop notification: {e}")
    
    def _play_alert_sound(self, alert: Dict[str, Any]):
        """Play alert sound"""
        try:
            import winsound
            
            severity = alert['severity']
            
            if severity == 'critical':
                # Play system error sound
                winsound.MessageBeep(winsound.MB_ICONHAND)
            elif severity == 'warning':
                # Play system warning sound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            else:
                # Play system info sound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
                
        except Exception as e:
            print(f"Error playing alert sound: {e}")
    
    def _send_email_notification(self, alert: Dict[str, Any]):
        """Send email notification"""
        try:
            if not self.notification_settings['email']['recipients']:
                return
            
            smtp_server = self.notification_settings['email']['smtp_server']
            smtp_port = self.notification_settings['email']['smtp_port']
            username = self.notification_settings['email']['username']
            password = self.notification_settings['email']['password']
            recipients = self.notification_settings['email']['recipients']
            
            if not all([smtp_server, username, password, recipients]):
                return
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"System Alert - {alert['severity'].title()}: {alert['category'].title()}"
            
            body = f"""
System Alert Notification

Timestamp: {alert['timestamp']}
Severity: {alert['severity'].title()}
Category: {alert['category'].title()}
Message: {alert['message']}

Alert ID: {alert['id']}

This is an automated message from the Self-Healing System Monitor.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            text = msg.as_string()
            server.sendmail(username, recipients, text)
            server.quit()
            
        except Exception as e:
            print(f"Error sending email notification: {e}")
    
    def check_thresholds(self, system_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check system data against alert thresholds"""
        new_alerts = []
        
        try:
            # CPU threshold checks
            if 'cpu_percent' in system_data:
                cpu_percent = system_data['cpu_percent']
                cpu_rules = self.alert_rules['cpu']
                
                if cpu_percent >= cpu_rules['critical_threshold']:
                    alert = self.add_alert(
                        'threshold', 'cpu', 
                        f'Critical CPU usage: {cpu_percent:.1f}%',
                        'critical',
                        {'value': cpu_percent, 'threshold': cpu_rules['critical_threshold']}
                    )
                    new_alerts.append(alert)
                elif cpu_percent >= cpu_rules['warning_threshold']:
                    alert = self.add_alert(
                        'threshold', 'cpu',
                        f'High CPU usage: {cpu_percent:.1f}%',
                        'warning',
                        {'value': cpu_percent, 'threshold': cpu_rules['warning_threshold']}
                    )
                    new_alerts.append(alert)
            
            # Memory threshold checks
            if 'memory_percent' in system_data:
                memory_percent = system_data['memory_percent']
                memory_rules = self.alert_rules['memory']
                
                if memory_percent >= memory_rules['critical_threshold']:
                    alert = self.add_alert(
                        'threshold', 'memory',
                        f'Critical memory usage: {memory_percent:.1f}%',
                        'critical',
                        {'value': memory_percent, 'threshold': memory_rules['critical_threshold']}
                    )
                    new_alerts.append(alert)
                elif memory_percent >= memory_rules['warning_threshold']:
                    alert = self.add_alert(
                        'threshold', 'memory',
                        f'High memory usage: {memory_percent:.1f}%',
                        'warning',
                        {'value': memory_percent, 'threshold': memory_rules['warning_threshold']}
                    )
                    new_alerts.append(alert)
            
            # Disk threshold checks
            if 'disk_usage' in system_data:
                disk_rules = self.alert_rules['disk']
                
                for disk in system_data['disk_usage']:
                    disk_percent = disk.get('percent', 0)
                    device = disk.get('device', 'Unknown')
                    
                    if disk_percent >= disk_rules['critical_threshold']:
                        alert = self.add_alert(
                            'threshold', 'disk',
                            f'Critical disk usage on {device}: {disk_percent:.1f}%',
                            'critical',
                            {'value': disk_percent, 'threshold': disk_rules['critical_threshold'], 'device': device}
                        )
                        new_alerts.append(alert)
                    elif disk_percent >= disk_rules['warning_threshold']:
                        alert = self.add_alert(
                            'threshold', 'disk',
                            f'High disk usage on {device}: {disk_percent:.1f}%',
                            'warning',
                            {'value': disk_percent, 'threshold': disk_rules['warning_threshold'], 'device': device}
                        )
                        new_alerts.append(alert)
            
            return new_alerts
            
        except Exception as e:
            error_alert = self.add_alert(
                'system', 'monitoring',
                f'Error checking thresholds: {e}',
                'warning'
            )
            return [error_alert]
    
    def update_alert_rules(self, new_rules: Dict[str, Any]):
        """Update alerting rules"""
        self.alert_rules.update(new_rules)
    
    def update_notification_settings(self, new_settings: Dict[str, Any]):
        """Update notification settings"""
        self.notification_settings.update(new_settings)
    
    def export_alerts(self, format: str = 'json') -> str:
        """Export alerts in specified format"""
        if format.lower() == 'json':
            return json.dumps(self.alerts, indent=2)
        elif format.lower() == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            if self.alerts:
                fieldnames = ['timestamp', 'type', 'category', 'message', 'severity', 'acknowledged', 'resolved']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for alert in self.alerts:
                    row = {field: alert.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")

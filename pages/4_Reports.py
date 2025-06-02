import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import time
from datetime import datetime, timedelta
import io

# Page configuration
st.set_page_config(
    page_title="System Reports",
    page_icon="📊",
    layout="wide"
)

st.title("📊 System Reports")
st.markdown("### Comprehensive System Analysis and Reporting")

# Initialize session state components
if 'monitor' not in st.session_state:
    from modules.system_monitor import SystemMonitor
    from modules.self_healer import SelfHealer
    from modules.alerts import AlertManager
    from modules.logger import SystemLogger
    
    st.session_state.monitor = SystemMonitor()
    st.session_state.healer = SelfHealer()
    st.session_state.alert_manager = AlertManager()
    st.session_state.logger = SystemLogger()

# Sidebar controls
with st.sidebar:
    st.header("📋 Report Options")
    
    # Report type selection
    report_type = st.selectbox(
        "Report Type",
        [
            "Complete System Report",
            "Performance Summary", 
            "Alert Analysis",
            "Healing Activity Report",
            "System Health Trend"
        ]
    )
    
    # Time range selection
    st.subheader("📅 Time Range")
    time_range = st.selectbox(
        "Time Period",
        ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week", "Custom Range"]
    )
    
    if time_range == "Custom Range":
        start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=7))
        end_date = st.date_input("End Date", datetime.now().date())
        start_time = st.time_input("Start Time", datetime.now().time())
        end_time = st.time_input("End Time", datetime.now().time())
    
    # Export format
    st.subheader("💾 Export Options")
    export_format = st.selectbox("Export Format", ["HTML", "JSON", "CSV", "Text"])
    
    # Generate report button
    if st.button("📄 Generate Report", type="primary"):
        st.session_state.generate_report = True
        st.session_state.report_timestamp = datetime.now()

# Main content area
if hasattr(st.session_state, 'generate_report') and st.session_state.generate_report:
    
    # Calculate time range
    now = datetime.now()
    if time_range == "Last Hour":
        start_datetime = now - timedelta(hours=1)
        end_datetime = now
    elif time_range == "Last 6 Hours":
        start_datetime = now - timedelta(hours=6)
        end_datetime = now
    elif time_range == "Last 24 Hours":
        start_datetime = now - timedelta(hours=24)
        end_datetime = now
    elif time_range == "Last Week":
        start_datetime = now - timedelta(weeks=1)
        end_datetime = now
    else:  # Custom Range
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
    
    st.header(f"📊 {report_type}")
    st.markdown(f"**Report Period:** {start_datetime.strftime('%Y-%m-%d %H:%M')} to {end_datetime.strftime('%Y-%m-%d %H:%M')}")
    st.markdown(f"**Generated:** {st.session_state.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        if report_type == "Complete System Report":
            # System Information Section
            st.subheader("💻 System Information")
            system_info = st.session_state.monitor.get_system_info()
            
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.write(f"**Platform:** {system_info['platform']}")
                st.write(f"**System:** {system_info['system']}")
                st.write(f"**Node:** {system_info['node']}")
                st.write(f"**Processor:** {system_info['processor']}")
            
            with info_col2:
                st.write(f"**Release:** {system_info['release']}")
                st.write(f"**Machine:** {system_info['machine']}")
                st.write(f"**Boot Time:** {system_info['boot_time']}")
                st.write(f"**Uptime:** {system_info['uptime']}")
            
            # Current System Status
            st.subheader("⚡ Current System Status")
            
            status_col1, status_col2, status_col3 = st.columns(3)
            
            with status_col1:
                cpu_data = st.session_state.monitor.get_cpu_details()
                st.metric("CPU Usage", f"{cpu_data['percent']:.1f}%")
                st.write(f"Logical Cores: {cpu_data['count_logical']}")
                st.write(f"Physical Cores: {cpu_data['count_physical']}")
            
            with status_col2:
                memory_data = st.session_state.monitor.get_memory_usage()
                st.metric("Memory Usage", f"{memory_data['percent']:.1f}%")
                st.write(f"Total: {memory_data['total'] / (1024**3):.2f} GB")
                st.write(f"Available: {memory_data['available'] / (1024**3):.2f} GB")
            
            with status_col3:
                disk_data = st.session_state.monitor.get_disk_usage()
                avg_disk = sum(d['percent'] for d in disk_data) / len(disk_data) if disk_data else 0
                st.metric("Avg Disk Usage", f"{avg_disk:.1f}%")
                st.write(f"Drives Monitored: {len(disk_data)}")
            
            # Process Information
            st.subheader("🔍 Process Analysis")
            processes = st.session_state.monitor.get_running_processes()
            
            if processes:
                process_df = pd.DataFrame(processes)
                
                # Top CPU processes
                top_cpu = process_df.nlargest(5, 'cpu_percent')[['name', 'pid', 'cpu_percent']]
                
                # Top Memory processes
                top_memory = process_df.nlargest(5, 'memory_mb')[['name', 'pid', 'memory_mb']]
                
                proc_col1, proc_col2 = st.columns(2)
                
                with proc_col1:
                    st.write("**Top CPU Processes:**")
                    for _, proc in top_cpu.iterrows():
                        st.write(f"- {proc['name']} (PID: {proc['pid']}): {proc['cpu_percent']:.1f}%")
                
                with proc_col2:
                    st.write("**Top Memory Processes:**")
                    for _, proc in top_memory.iterrows():
                        st.write(f"- {proc['name']} (PID: {proc['pid']}): {proc['memory_mb']:.1f} MB")
            
            # Disk Usage Details
            st.subheader("💾 Disk Usage Details")
            if disk_data:
                disk_df = pd.DataFrame(disk_data)
                st.dataframe(
                    disk_df[['device', 'fstype', 'total', 'used', 'free', 'percent']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "total": st.column_config.NumberColumn("Total (Bytes)", format="%d"),
                        "used": st.column_config.NumberColumn("Used (Bytes)", format="%d"),
                        "free": st.column_config.NumberColumn("Free (Bytes)", format="%d"),
                        "percent": st.column_config.ProgressColumn("Usage %", min_value=0, max_value=100)
                    }
                )
        
        elif report_type == "Performance Summary":
            st.subheader("📈 Performance Metrics")
            
            # Get current performance data
            cpu_data = st.session_state.monitor.get_cpu_details()
            memory_data = st.session_state.monitor.get_memory_usage()
            
            # Performance summary table
            perf_data = {
                "Metric": ["CPU Usage", "Memory Usage", "CPU Cores (Logical)", "CPU Cores (Physical)", "Total Memory", "Available Memory"],
                "Value": [
                    f"{cpu_data['percent']:.1f}%",
                    f"{memory_data['percent']:.1f}%",
                    f"{cpu_data['count_logical']}",
                    f"{cpu_data['count_physical']}",
                    f"{memory_data['total'] / (1024**3):.2f} GB",
                    f"{memory_data['available'] / (1024**3):.2f} GB"
                ],
                "Status": [
                    "🟢 Normal" if cpu_data['percent'] < 75 else "🟡 High" if cpu_data['percent'] < 90 else "🔴 Critical",
                    "🟢 Normal" if memory_data['percent'] < 80 else "🟡 High" if memory_data['percent'] < 95 else "🔴 Critical",
                    "ℹ️ Info",
                    "ℹ️ Info", 
                    "ℹ️ Info",
                    "ℹ️ Info"
                ]
            }
            
            perf_df = pd.DataFrame(perf_data)
            st.dataframe(perf_df, use_container_width=True, hide_index=True)
            
            # Performance history charts
            if hasattr(st.session_state.monitor, 'cpu_history') and st.session_state.monitor.cpu_history:
                st.subheader("📊 Performance Trends")
                
                # CPU trend
                cpu_history_df = pd.DataFrame(st.session_state.monitor.cpu_history)
                cpu_history_df['timestamp'] = pd.to_datetime(cpu_history_df['timestamp'])
                
                fig_cpu = px.line(cpu_history_df, x='timestamp', y='value', 
                                title='CPU Usage Trend', labels={'value': 'CPU %', 'timestamp': 'Time'})
                fig_cpu.add_hline(y=75, line_dash="dash", line_color="orange")
                fig_cpu.add_hline(y=90, line_dash="dash", line_color="red")
                st.plotly_chart(fig_cpu, use_container_width=True)
                
                # Memory trend
                if hasattr(st.session_state.monitor, 'memory_history') and st.session_state.monitor.memory_history:
                    memory_history_df = pd.DataFrame(st.session_state.monitor.memory_history)
                    memory_history_df['timestamp'] = pd.to_datetime(memory_history_df['timestamp'])
                    
                    fig_memory = px.line(memory_history_df, x='timestamp', y='value',
                                       title='Memory Usage Trend', labels={'value': 'Memory %', 'timestamp': 'Time'})
                    fig_memory.add_hline(y=80, line_dash="dash", line_color="orange")
                    fig_memory.add_hline(y=95, line_dash="dash", line_color="red")
                    st.plotly_chart(fig_memory, use_container_width=True)
        
        elif report_type == "Alert Analysis":
            st.subheader("🚨 Alert Statistics and Analysis")
            
            # Get alert statistics
            alert_stats = st.session_state.alert_manager.get_alert_statistics()
            
            # Alert summary metrics
            alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)
            
            with alert_col1:
                st.metric("Total Alerts", alert_stats['total_alerts'])
            with alert_col2:
                st.metric("Active Alerts", alert_stats['active_alerts'])
            with alert_col3:
                st.metric("Critical Alerts", alert_stats['critical_alerts'])
            with alert_col4:
                st.metric("Last 24h Alerts", alert_stats['alerts_last_day'])
            
            # Alert distribution charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                if alert_stats['by_category']:
                    fig_category = px.pie(
                        values=list(alert_stats['by_category'].values()),
                        names=list(alert_stats['by_category'].keys()),
                        title="Alerts by Category"
                    )
                    st.plotly_chart(fig_category, use_container_width=True)
            
            with chart_col2:
                if alert_stats['by_severity']:
                    fig_severity = px.pie(
                        values=list(alert_stats['by_severity'].values()),
                        names=list(alert_stats['by_severity'].keys()),
                        title="Alerts by Severity"
                    )
                    st.plotly_chart(fig_severity, use_container_width=True)
            
            # Recent alerts table
            st.subheader("Recent Alerts")
            recent_alerts = st.session_state.alert_manager.get_recent_alerts(20)
            
            if recent_alerts:
                alerts_df = pd.DataFrame(recent_alerts)
                display_alerts = alerts_df[['timestamp', 'type', 'category', 'message', 'severity', 'resolved']]
                display_alerts['timestamp'] = pd.to_datetime(display_alerts['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                st.dataframe(display_alerts, use_container_width=True, hide_index=True)
            else:
                st.info("No alerts found in the specified time range")
        
        elif report_type == "Healing Activity Report":
            st.subheader("🛠️ Self-Healing Activity Analysis")
            
            # Get healing log
            healing_log = st.session_state.healer.get_healing_log(100)
            
            if healing_log:
                healing_df = pd.DataFrame(healing_log)
                healing_df['timestamp'] = pd.to_datetime(healing_df['timestamp'])
                
                # Filter by time range
                filtered_healing = healing_df[
                    (healing_df['timestamp'] >= start_datetime) & 
                    (healing_df['timestamp'] <= end_datetime)
                ]
                
                # Healing statistics
                total_actions = len(filtered_healing)
                successful_actions = len(filtered_healing[filtered_healing['success'] == True])
                failed_actions = total_actions - successful_actions
                success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
                
                heal_col1, heal_col2, heal_col3, heal_col4 = st.columns(4)
                
                with heal_col1:
                    st.metric("Total Actions", total_actions)
                with heal_col2:
                    st.metric("Successful", successful_actions)
                with heal_col3:
                    st.metric("Failed", failed_actions)
                with heal_col4:
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                
                # Healing actions by type
                if not filtered_healing.empty:
                    action_counts = filtered_healing['action'].value_counts()
                    
                    fig_actions = px.bar(
                        x=action_counts.values,
                        y=action_counts.index,
                        orientation='h',
                        title="Healing Actions by Type",
                        labels={'x': 'Count', 'y': 'Action Type'}
                    )
                    st.plotly_chart(fig_actions, use_container_width=True)
                    
                    # Success rate by action type
                    success_by_action = filtered_healing.groupby('action')['success'].agg(['count', 'sum']).reset_index()
                    success_by_action['success_rate'] = (success_by_action['sum'] / success_by_action['count'] * 100)
                    
                    fig_success_rate = px.bar(
                        success_by_action,
                        x='action',
                        y='success_rate',
                        title="Success Rate by Action Type",
                        labels={'success_rate': 'Success Rate (%)', 'action': 'Action Type'}
                    )
                    st.plotly_chart(fig_success_rate, use_container_width=True)
                    
                    # Detailed healing log
                    st.subheader("Detailed Healing Log")
                    display_healing = filtered_healing[['timestamp', 'action', 'message', 'success']].copy()
                    display_healing['timestamp'] = display_healing['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    display_healing['status'] = display_healing['success'].apply(lambda x: '✅ Success' if x else '❌ Failed')
                    
                    st.dataframe(
                        display_healing[['timestamp', 'action', 'message', 'status']],
                        use_container_width=True,
                        hide_index=True
                    )
            else:
                st.info("No healing activities found in the specified time range")
        
        elif report_type == "System Health Trend":
            st.subheader("📈 System Health Trend Analysis")
            
            # Current system health score calculation
            cpu_data = st.session_state.monitor.get_cpu_details()
            memory_data = st.session_state.monitor.get_memory_usage()
            disk_data = st.session_state.monitor.get_disk_usage()
            
            # Calculate health scores (0-100, higher is better)
            cpu_health = max(0, 100 - cpu_data['percent'])
            memory_health = max(0, 100 - memory_data['percent'])
            
            avg_disk_usage = sum(d['percent'] for d in disk_data) / len(disk_data) if disk_data else 0
            disk_health = max(0, 100 - avg_disk_usage)
            
            overall_health = (cpu_health + memory_health + disk_health) / 3
            
            # Health metrics
            health_col1, health_col2, health_col3, health_col4 = st.columns(4)
            
            with health_col1:
                st.metric("Overall Health", f"{overall_health:.1f}/100")
            with health_col2:
                st.metric("CPU Health", f"{cpu_health:.1f}/100")
            with health_col3:
                st.metric("Memory Health", f"{memory_health:.1f}/100")
            with health_col4:
                st.metric("Disk Health", f"{disk_health:.1f}/100")
            
            # Health status indicators
            health_status = "🟢 Excellent" if overall_health >= 80 else "🟡 Good" if overall_health >= 60 else "🟠 Fair" if overall_health >= 40 else "🔴 Poor"
            st.write(f"**System Health Status:** {health_status}")
            
            # Health recommendations
            st.subheader("💡 Health Recommendations")
            
            recommendations = []
            
            if cpu_health < 50:
                recommendations.append("🔴 **CPU**: High CPU usage detected. Consider closing unnecessary applications or upgrading hardware.")
            elif cpu_health < 70:
                recommendations.append("🟡 **CPU**: Moderate CPU usage. Monitor for performance issues.")
            
            if memory_health < 50:
                recommendations.append("🔴 **Memory**: High memory usage detected. Consider adding more RAM or closing memory-intensive applications.")
            elif memory_health < 70:
                recommendations.append("🟡 **Memory**: Moderate memory usage. Consider memory optimization.")
            
            if disk_health < 50:
                recommendations.append("🔴 **Disk**: Low disk space detected. Clean up unnecessary files or add more storage.")
            elif disk_health < 70:
                recommendations.append("🟡 **Disk**: Moderate disk usage. Consider regular cleanup maintenance.")
            
            if not recommendations:
                st.success("🟢 No immediate health concerns detected. System is performing optimally!")
            else:
                for rec in recommendations:
                    st.warning(rec)
        
        # Export functionality
        st.markdown("---")
        st.subheader("💾 Export Report")
        
        # Prepare export data based on report type
        export_data = {
            "report_type": report_type,
            "generated_at": st.session_state.report_timestamp.isoformat(),
            "time_range": {
                "start": start_datetime.isoformat(),
                "end": end_datetime.isoformat()
            }
        }
        
        if export_format == "JSON":
            # Add relevant data to export
            try:
                export_data["system_info"] = st.session_state.monitor.get_system_info()
                export_data["current_status"] = {
                    "cpu": st.session_state.monitor.get_cpu_details(),
                    "memory": st.session_state.monitor.get_memory_usage(),
                    "disk": st.session_state.monitor.get_disk_usage()
                }
                export_data["alerts"] = st.session_state.alert_manager.get_recent_alerts(50)
                export_data["healing_log"] = st.session_state.healer.get_healing_log(50)
                
                export_content = json.dumps(export_data, indent=2, default=str)
                
            except Exception as e:
                export_content = json.dumps({"error": f"Export failed: {e}"}, indent=2)
        
        elif export_format == "CSV":
            # For CSV, export recent alerts and healing log
            try:
                alerts_data = st.session_state.alert_manager.export_alerts(format='csv')
                export_content = f"# ALERTS DATA\n{alerts_data}\n\n# HEALING LOG\n"
                
                healing_log = st.session_state.healer.get_healing_log(100)
                if healing_log:
                    healing_df = pd.DataFrame(healing_log)
                    export_content += healing_df.to_csv(index=False)
                
            except Exception as e:
                export_content = f"Export failed: {e}"
        
        elif export_format == "Text":
            # Generate comprehensive text report
            try:
                export_content = st.session_state.monitor.generate_system_report()
            except Exception as e:
                export_content = f"Export failed: {e}"
        
        else:  # HTML
            # Generate HTML report
            export_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{report_type} - System Monitor Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h1>{report_type}</h1>
                <p><strong>Generated:</strong> {st.session_state.report_timestamp}</p>
                <p><strong>Time Range:</strong> {start_datetime} to {end_datetime}</p>
                
                <h2>System Information</h2>
                <p>This report was generated by the Self-Healing System Monitor.</p>
                <p>For detailed data, please use JSON or CSV export formats.</p>
            </body>
            </html>
            """
        
        # Download button
        file_extension = export_format.lower()
        if file_extension == "text":
            file_extension = "txt"
        
        filename = f"system_report_{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        
        st.download_button(
            label=f"📥 Download {export_format} Report",
            data=export_content,
            file_name=filename,
            mime="text/plain" if export_format in ["Text", "CSV"] else "application/json" if export_format == "JSON" else "text/html"
        )
        
    except Exception as e:
        st.error(f"Error generating report: {e}")
        st.exception(e)

else:
    # Default state - show report options
    st.header("📋 Generate System Reports")
    st.markdown("""
    Welcome to the System Reports section. Here you can generate comprehensive reports about your system's performance, 
    health status, alerts, and self-healing activities.
    
    **Available Report Types:**
    
    - **Complete System Report**: Comprehensive overview of all system components and status
    - **Performance Summary**: Detailed performance metrics and trends
    - **Alert Analysis**: Analysis of system alerts and their patterns
    - **Healing Activity Report**: Summary of all self-healing actions taken
    - **System Health Trend**: Overall system health assessment and recommendations
    
    **Instructions:**
    1. Select your desired report type from the sidebar
    2. Choose the time range for the report
    3. Select export format (HTML, JSON, CSV, or Text)
    4. Click "Generate Report" to create your report
    5. Download the report using the export button
    """)
    
    # Quick stats overview
    st.subheader("📊 Quick Statistics")
    
    try:
        # Get basic stats for display
        alert_stats = st.session_state.alert_manager.get_alert_statistics()
        healing_log = st.session_state.healer.get_healing_log(10)
        
        quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
        
        with quick_col1:
            st.metric("Total Alerts", alert_stats.get('total_alerts', 0))
        
        with quick_col2:
            st.metric("Active Alerts", alert_stats.get('active_alerts', 0))
        
        with quick_col3:
            st.metric("Recent Healing Actions", len(healing_log))
        
        with quick_col4:
            # Calculate system uptime
            import psutil
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = int(uptime_seconds // 3600)
            st.metric("System Uptime (hours)", uptime_hours)
            
    except Exception as e:
        st.error(f"Error loading quick statistics: {e}")

# Footer
st.markdown("---")
st.markdown(f"🕒 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

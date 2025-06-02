import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
from datetime import datetime, timedelta
import psutil

# Page configuration
st.set_page_config(
    page_title="System Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 System Dashboard")
st.markdown("### Real-time System Monitoring Overview")

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

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto Refresh (3s)", value=True)
if st.sidebar.button("🔄 Manual Refresh"):
    st.rerun()

# System status overview
st.header("🎯 System Status Overview")

try:
    # Get current system data
    cpu_data = st.session_state.monitor.get_cpu_details()
    memory_data = st.session_state.monitor.get_memory_usage()
    disk_data = st.session_state.monitor.get_disk_usage()
    
    # Status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cpu_status = "🟢 Normal" if cpu_data['percent'] < 75 else "🟡 High" if cpu_data['percent'] < 90 else "🔴 Critical"
        st.metric(
            "CPU Usage", 
            f"{cpu_data['percent']:.1f}%",
            delta=f"{cpu_data['percent'] - 50:.1f}%" if cpu_data['percent'] > 50 else None
        )
        st.write(cpu_status)
    
    with col2:
        memory_status = "🟢 Normal" if memory_data['percent'] < 80 else "🟡 High" if memory_data['percent'] < 95 else "🔴 Critical"
        st.metric(
            "Memory Usage", 
            f"{memory_data['percent']:.1f}%",
            delta=f"{memory_data['percent'] - 70:.1f}%" if memory_data['percent'] > 70 else None
        )
        st.write(memory_status)
    
    with col3:
        avg_disk_usage = sum(disk['percent'] for disk in disk_data) / len(disk_data) if disk_data else 0
        disk_status = "🟢 Normal" if avg_disk_usage < 80 else "🟡 High" if avg_disk_usage < 95 else "🔴 Critical"
        st.metric(
            "Avg Disk Usage", 
            f"{avg_disk_usage:.1f}%",
            delta=f"{avg_disk_usage - 70:.1f}%" if avg_disk_usage > 70 else None
        )
        st.write(disk_status)
    
    with col4:
        active_alerts = len(st.session_state.alert_manager.get_active_alerts())
        alert_status = "🟢 No Issues" if active_alerts == 0 else f"⚠️ {active_alerts} Active"
        st.metric("Active Alerts", active_alerts)
        st.write(alert_status)

except Exception as e:
    st.error(f"Error loading system data: {e}")

# Charts section
st.header("📈 Real-time Charts")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("CPU Usage Trend")
    try:
        if hasattr(st.session_state.monitor, 'cpu_history') and st.session_state.monitor.cpu_history:
            # Create CPU trend chart
            cpu_df = pd.DataFrame(st.session_state.monitor.cpu_history)
            cpu_df['timestamp'] = pd.to_datetime(cpu_df['timestamp'])
            
            fig_cpu = px.line(
                cpu_df, 
                x='timestamp', 
                y='value',
                title='CPU Usage Over Time',
                labels={'value': 'CPU Usage (%)', 'timestamp': 'Time'}
            )
            fig_cpu.update_layout(height=300)
            fig_cpu.add_hline(y=75, line_dash="dash", line_color="orange", annotation_text="Warning (75%)")
            fig_cpu.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="Critical (90%)")
            st.plotly_chart(fig_cpu, use_container_width=True)
        else:
            st.info("Collecting CPU data... Please wait.")
    except Exception as e:
        st.error(f"Error creating CPU chart: {e}")

with chart_col2:
    st.subheader("Memory Usage Trend")
    try:
        if hasattr(st.session_state.monitor, 'memory_history') and st.session_state.monitor.memory_history:
            # Create memory trend chart
            memory_df = pd.DataFrame(st.session_state.monitor.memory_history)
            memory_df['timestamp'] = pd.to_datetime(memory_df['timestamp'])
            
            fig_memory = px.line(
                memory_df, 
                x='timestamp', 
                y='value',
                title='Memory Usage Over Time',
                labels={'value': 'Memory Usage (%)', 'timestamp': 'Time'}
            )
            fig_memory.update_layout(height=300)
            fig_memory.add_hline(y=80, line_dash="dash", line_color="orange", annotation_text="Warning (80%)")
            fig_memory.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="Critical (95%)")
            st.plotly_chart(fig_memory, use_container_width=True)
        else:
            st.info("Collecting memory data... Please wait.")
    except Exception as e:
        st.error(f"Error creating memory chart: {e}")

# System details section
st.header("💻 System Details")

detail_col1, detail_col2 = st.columns(2)

with detail_col1:
    st.subheader("CPU Information")
    try:
        cpu_info = st.session_state.monitor.get_cpu_details()
        st.write(f"**Logical Cores:** {cpu_info['count_logical']}")
        st.write(f"**Physical Cores:** {cpu_info['count_physical']}")
        if cpu_info['freq_current']:
            st.write(f"**Current Frequency:** {cpu_info['freq_current']:.0f} MHz")
            st.write(f"**Max Frequency:** {cpu_info['freq_max']:.0f} MHz")
        
        # Per-CPU usage
        if cpu_info['per_cpu']:
            st.write("**Per-Core Usage:**")
            for i, usage in enumerate(cpu_info['per_cpu']):
                st.progress(usage / 100, text=f"Core {i+1}: {usage:.1f}%")
    except Exception as e:
        st.error(f"Error loading CPU info: {e}")

with detail_col2:
    st.subheader("Memory Information")
    try:
        memory_info = st.session_state.monitor.get_memory_usage()
        st.write(f"**Total:** {memory_info['total'] / (1024**3):.2f} GB")
        st.write(f"**Used:** {memory_info['used'] / (1024**3):.2f} GB")
        st.write(f"**Available:** {memory_info['available'] / (1024**3):.2f} GB")
        st.write(f"**Free:** {memory_info['free'] / (1024**3):.2f} GB")
        
        # Memory usage progress bar
        st.progress(memory_info['percent'] / 100, text=f"Memory Usage: {memory_info['percent']:.1f}%")
        
        # Swap information if available
        if memory_info['swap_total'] > 0:
            st.write(f"**Swap Total:** {memory_info['swap_total'] / (1024**3):.2f} GB")
            st.write(f"**Swap Used:** {memory_info['swap_used'] / (1024**3):.2f} GB ({memory_info['swap_percent']:.1f}%)")
    except Exception as e:
        st.error(f"Error loading memory info: {e}")

# Disk usage section
st.subheader("💾 Disk Usage")
try:
    disk_info = st.session_state.monitor.get_disk_usage()
    
    if disk_info:
        disk_cols = st.columns(min(len(disk_info), 4))
        
        for i, disk in enumerate(disk_info):
            with disk_cols[i % 4]:
                st.write(f"**Drive {disk['device']}**")
                st.write(f"Type: {disk['fstype']}")
                st.write(f"Total: {disk['total'] / (1024**3):.1f} GB")
                st.write(f"Used: {disk['used'] / (1024**3):.1f} GB")
                st.write(f"Free: {disk['free'] / (1024**3):.1f} GB")
                
                # Color-coded progress bar
                if disk['percent'] >= 95:
                    progress_color = "🔴"
                elif disk['percent'] >= 85:
                    progress_color = "🟡"
                else:
                    progress_color = "🟢"
                
                st.progress(disk['percent'] / 100, text=f"{progress_color} {disk['percent']:.1f}%")
    else:
        st.info("No disk information available")
except Exception as e:
    st.error(f"Error loading disk info: {e}")

# Recent alerts section
st.header("🚨 Recent Alerts")
try:
    recent_alerts = st.session_state.alert_manager.get_recent_alerts(10)
    
    if recent_alerts:
        for alert in recent_alerts:
            alert_time = datetime.fromisoformat(alert['timestamp']).strftime('%H:%M:%S')
            
            if alert['severity'] == 'critical':
                st.error(f"🔴 **{alert_time}** - {alert['message']}")
            elif alert['severity'] == 'warning':
                st.warning(f"🟡 **{alert_time}** - {alert['message']}")
            else:
                st.info(f"🔵 **{alert_time}** - {alert['message']}")
    else:
        st.success("🟢 No recent alerts - system is running smoothly!")
except Exception as e:
    st.error(f"Error loading alerts: {e}")

# System actions
st.header("⚡ Quick Actions")
action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("🧹 Clean Temp Files", type="secondary"):
        with st.spinner("Cleaning temporary files..."):
            try:
                result = st.session_state.healer.clean_temp_files()
                if result['success']:
                    st.success(f"✅ Cleaned {result['files_removed']} files, freed {result['space_freed_mb']:.1f} MB")
                    st.session_state.logger.log_healing_action("clean_temp_files", True, result['message'])
                else:
                    st.error(f"❌ {result['message']}")
            except Exception as e:
                st.error(f"Error cleaning temp files: {e}")

with action_col2:
    if st.button("💾 Free Memory", type="secondary"):
        with st.spinner("Optimizing memory..."):
            try:
                result = st.session_state.healer.free_memory()
                if result['success']:
                    st.success(f"✅ Memory optimization completed")
                    st.session_state.logger.log_healing_action("free_memory", True, result['message'])
                else:
                    st.error(f"❌ {result['message']}")
            except Exception as e:
                st.error(f"Error freeing memory: {e}")

with action_col3:
    if st.button("🔄 Restart Services", type="secondary"):
        with st.spinner("Restarting services..."):
            try:
                result = st.session_state.healer.restart_unresponsive_services()
                if result['success']:
                    st.success(f"✅ Service restart completed")
                    st.session_state.logger.log_healing_action("restart_services", True, result['message'])
                else:
                    st.error(f"❌ {result['message']}")
            except Exception as e:
                st.error(f"Error restarting services: {e}")

# Auto-refresh functionality
if auto_refresh:
    time.sleep(3)
    st.rerun()

# Footer with last update time
st.markdown("---")
st.markdown(f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

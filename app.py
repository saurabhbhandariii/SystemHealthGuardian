import streamlit as st
import time
import threading
from modules.system_monitor import SystemMonitor
from modules.self_healer import SelfHealer
from modules.alerts import AlertManager
from modules.logger import SystemLogger

# Configure the page
st.set_page_config(
    page_title="Self-Healing System Monitor",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'monitor' not in st.session_state:
    st.session_state.monitor = SystemMonitor()
    st.session_state.healer = SelfHealer()
    st.session_state.alert_manager = AlertManager()
    st.session_state.logger = SystemLogger()
    st.session_state.monitoring_active = False

def start_monitoring():
    """Start continuous monitoring in background"""
    if not st.session_state.monitoring_active:
        st.session_state.monitoring_active = True
        
def stop_monitoring():
    """Stop continuous monitoring"""
    st.session_state.monitoring_active = False

# Main page content
st.title("🔧 Self-Healing System Monitor")
st.markdown("### Windows-Compatible System Monitoring & Auto-Resolution")

# Sidebar controls
with st.sidebar:
    st.header("🎛️ Control Panel")
    
    if st.button("🟢 Start Monitoring", type="primary"):
        start_monitoring()
        st.success("Monitoring started!")
    
    if st.button("🔴 Stop Monitoring"):
        stop_monitoring()
        st.warning("Monitoring stopped!")
    
    st.divider()
    
    # Monitoring status
    if st.session_state.monitoring_active:
        st.success("🟢 Monitoring Active")
    else:
        st.error("🔴 Monitoring Inactive")
    
    st.divider()
    
    # Quick system overview
    st.header("📊 Quick Stats")
    try:
        cpu_percent = st.session_state.monitor.get_cpu_usage()
        memory_percent = st.session_state.monitor.get_memory_usage()['percent']
        
        st.metric("CPU Usage", f"{cpu_percent:.1f}%", 
                 delta=f"{cpu_percent - 50:.1f}%" if cpu_percent > 50 else None)
        st.metric("Memory Usage", f"{memory_percent:.1f}%",
                 delta=f"{memory_percent - 70:.1f}%" if memory_percent > 70 else None)
    except Exception as e:
        st.error(f"Error getting system stats: {e}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🏠 Welcome to System Monitor")
    st.markdown("""
    This application provides comprehensive system monitoring and self-healing capabilities for Windows systems.
    
    **Features:**
    - 📈 Real-time CPU, Memory, and Disk monitoring
    - 🔍 Process monitoring and management
    - 🛠️ Automatic issue detection and resolution
    - 🚨 Smart alerting system
    - 📊 Detailed system reports
    - 🏥 Self-healing capabilities
    
    **Navigation:**
    Use the sidebar to navigate between different monitoring sections.
    """)
    
    # Recent alerts
    st.subheader("🚨 Recent Alerts")
    try:
        alerts = st.session_state.alert_manager.get_recent_alerts(5)
        if alerts:
            for alert in alerts:
                alert_type = alert.get('type', 'info')
                if alert_type == 'critical':
                    st.error(f"🔴 {alert['message']} - {alert['timestamp']}")
                elif alert_type == 'warning':
                    st.warning(f"🟡 {alert['message']} - {alert['timestamp']}")
                else:
                    st.info(f"🔵 {alert['message']} - {alert['timestamp']}")
        else:
            st.info("No recent alerts")
    except Exception as e:
        st.error(f"Error loading alerts: {e}")

with col2:
    st.header("⚡ Quick Actions")
    
    if st.button("🧹 Clean Temp Files", type="secondary"):
        try:
            result = st.session_state.healer.clean_temp_files()
            if result['success']:
                st.success(f"✅ Cleaned {result['files_removed']} temporary files")
            else:
                st.error(f"❌ {result['message']}")
        except Exception as e:
            st.error(f"Error cleaning temp files: {e}")
    
    if st.button("💾 Free Memory", type="secondary"):
        try:
            result = st.session_state.healer.free_memory()
            if result['success']:
                st.success(f"✅ Memory optimization completed")
            else:
                st.error(f"❌ {result['message']}")
        except Exception as e:
            st.error(f"Error freeing memory: {e}")
    
    if st.button("📊 Generate Report", type="secondary"):
        try:
            report = st.session_state.monitor.generate_system_report()
            st.success("✅ Report generated successfully!")
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"system_report_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error generating report: {e}")

# Auto-refresh when monitoring is active
if st.session_state.monitoring_active:
    time.sleep(3)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    Self-Healing System Monitor | PBL Project - Operating System | Under guidance of Susheela Ma'am
    </div>
    """, 
    unsafe_allow_html=True
)

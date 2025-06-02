import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
import threading

# Page configuration
st.set_page_config(
    page_title="Self-Healing System",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ Self-Healing System")
st.markdown("### Automated Issue Detection and Resolution")

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

# Initialize healing state
if 'healing_enabled' not in st.session_state:
    st.session_state.healing_enabled = False
if 'last_healing_check' not in st.session_state:
    st.session_state.last_healing_check = None

# Sidebar controls
with st.sidebar:
    st.header("🎛️ Healing Controls")
    
    # Main healing toggle
    if st.button("🟢 Enable Auto-Healing" if not st.session_state.healing_enabled else "🔴 Disable Auto-Healing", 
                type="primary"):
        if not st.session_state.healing_enabled:
            result = st.session_state.healer.start_continuous_healing(check_interval=180)  # 3 minutes
            if result['success']:
                st.session_state.healing_enabled = True
                st.success("✅ Auto-healing enabled!")
            else:
                st.error(f"❌ {result['message']}")
        else:
            result = st.session_state.healer.stop_continuous_healing()
            if result['success']:
                st.session_state.healing_enabled = False
                st.success("✅ Auto-healing disabled!")
            else:
                st.error(f"❌ {result['message']}")
    
    # Status indicator
    if st.session_state.healing_enabled:
        st.success("🟢 Auto-healing is ACTIVE")
    else:
        st.warning("🟡 Auto-healing is INACTIVE")
    
    st.divider()
    
    # Manual healing options
    st.subheader("🔧 Manual Actions")
    
    if st.button("🔍 Scan for Issues"):
        with st.spinner("Scanning system for issues..."):
            try:
                issues = st.session_state.monitor.detect_issues()
                st.session_state.current_issues = issues
                st.success(f"✅ Scan complete! Found {len(issues)} issues.")
            except Exception as e:
                st.error(f"❌ Scan failed: {e}")
    
    if st.button("🏥 Run Healing Actions"):
        if 'current_issues' in st.session_state and st.session_state.current_issues:
            with st.spinner("Running healing actions..."):
                try:
                    result = st.session_state.healer.auto_heal(st.session_state.current_issues)
                    if result['success']:
                        st.success(f"✅ Healing completed: {result['successful_count']}/{result['total_count']} successful")
                    else:
                        st.error(f"❌ {result['message']}")
                except Exception as e:
                    st.error(f"❌ Healing failed: {e}")
        else:
            st.warning("⚠️ No issues detected. Run a scan first.")
    
    st.divider()
    
    # Healing configuration
    st.subheader("⚙️ Configuration")
    
    cpu_threshold = st.slider("CPU Alert Threshold (%)", 50, 100, 75)
    memory_threshold = st.slider("Memory Alert Threshold (%)", 50, 100, 85)
    disk_threshold = st.slider("Disk Alert Threshold (%)", 50, 100, 85)
    
    # Update alert rules
    new_rules = {
        'cpu': {'warning_threshold': cpu_threshold, 'critical_threshold': cpu_threshold + 15},
        'memory': {'warning_threshold': memory_threshold, 'critical_threshold': memory_threshold + 10},
        'disk': {'warning_threshold': disk_threshold, 'critical_threshold': disk_threshold + 10}
    }
    st.session_state.alert_manager.update_alert_rules(new_rules)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Current system status
    st.header("🎯 System Health Status")
    
    try:
        # Get current issues
        current_issues = st.session_state.monitor.detect_issues()
        
        if current_issues:
            st.warning(f"⚠️ {len(current_issues)} issue(s) detected:")
            
            for issue in current_issues:
                if issue['type'] == 'critical':
                    st.error(f"🔴 **{issue['category'].title()}**: {issue['message']}")
                elif issue['type'] == 'warning':
                    st.warning(f"🟡 **{issue['category'].title()}**: {issue['message']}")
                else:
                    st.info(f"🔵 **{issue['category'].title()}**: {issue['message']}")
        else:
            st.success("🟢 **System Status: HEALTHY** - No issues detected!")
        
        # Store current issues for manual healing
        st.session_state.current_issues = current_issues
        
    except Exception as e:
        st.error(f"Error checking system health: {e}")
    
    # Healing capabilities overview
    st.header("🛠️ Available Healing Actions")
    
    healing_actions = [
        {
            "action": "High CPU Process Termination",
            "description": "Automatically terminates processes consuming excessive CPU resources",
            "trigger": "CPU usage > 75%",
            "safety": "Safe - excludes system processes"
        },
        {
            "action": "Memory Optimization",
            "description": "Frees up system memory using garbage collection and cache clearing",
            "trigger": "Memory usage > 85%",
            "safety": "Safe - non-destructive operations"
        },
        {
            "action": "Temporary File Cleanup",
            "description": "Removes temporary files and browser caches to free disk space",
            "trigger": "Disk usage > 85%",
            "safety": "Safe - only removes temp files"
        },
        {
            "action": "Service Restart",
            "description": "Restarts unresponsive Windows services",
            "trigger": "Service not responding",
            "safety": "Medium - may briefly interrupt services"
        },
        {
            "action": "Zombie Process Cleanup",
            "description": "Cleans up zombie and unresponsive processes",
            "trigger": "Zombie processes detected",
            "safety": "Safe - only affects dead processes"
        }
    ]
    
    for action in healing_actions:
        with st.expander(f"🔧 {action['action']}"):
            st.write(f"**Description:** {action['description']}")
            st.write(f"**Trigger Condition:** {action['trigger']}")
            
            safety_color = "🟢" if action['safety'].startswith("Safe") else "🟡"
            st.write(f"**Safety Level:** {safety_color} {action['safety']}")

with col2:
    # Healing statistics
    st.header("📊 Healing Statistics")
    
    try:
        healing_log = st.session_state.healer.get_healing_log(50)
        
        if healing_log:
            # Success rate
            successful_actions = sum(1 for entry in healing_log if entry['success'])
            total_actions = len(healing_log)
            success_rate = (successful_actions / total_actions) * 100 if total_actions > 0 else 0
            
            st.metric("Success Rate", f"{success_rate:.1f}%")
            st.metric("Total Actions", total_actions)
            st.metric("Successful Actions", successful_actions)
            st.metric("Failed Actions", total_actions - successful_actions)
            
            # Recent actions chart
            st.subheader("Recent Actions")
            
            # Get actions from last 24 hours
            now = datetime.now()
            recent_actions = []
            
            for entry in healing_log:
                try:
                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    if now - entry_time <= timedelta(hours=24):
                        recent_actions.append({
                            'time': entry_time.strftime('%H:%M'),
                            'action': entry['action'],
                            'success': entry['success']
                        })
                except:
                    continue
            
            if recent_actions:
                df_actions = pd.DataFrame(recent_actions)
                
                # Success/failure chart
                success_counts = df_actions['success'].value_counts()
                if len(success_counts) > 0:
                    fig_success = px.pie(
                        values=success_counts.values,
                        names=['Success' if x else 'Failed' for x in success_counts.index],
                        title="Action Success Rate (24h)",
                        color_discrete_map={'Success': 'green', 'Failed': 'red'}
                    )
                    fig_success.update_layout(height=250)
                    st.plotly_chart(fig_success, use_container_width=True)
            
        else:
            st.info("No healing actions recorded yet")
            
    except Exception as e:
        st.error(f"Error loading healing statistics: {e}")

# Healing log section
st.header("📋 Healing Activity Log")

try:
    healing_log = st.session_state.healer.get_healing_log(20)
    
    if healing_log:
        # Convert to DataFrame for display
        log_df = pd.DataFrame(healing_log)
        log_df['timestamp'] = pd.to_datetime(log_df['timestamp'])
        log_df = log_df.sort_values('timestamp', ascending=False)
        
        # Display recent entries
        for _, entry in log_df.head(10).iterrows():
            timestamp = entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            action = entry['action']
            message = entry['message']
            success = entry['success']
            
            if success:
                st.success(f"✅ **{timestamp}** - {action}: {message}")
            else:
                st.error(f"❌ **{timestamp}** - {action}: {message}")
        
        # Show full log option
        if st.checkbox("Show full healing log"):
            st.subheader("Complete Healing Log")
            
            display_log = log_df[['timestamp', 'action', 'message', 'success']].copy()
            display_log.columns = ['Timestamp', 'Action', 'Message', 'Success']
            display_log['Status'] = display_log['Success'].apply(lambda x: '✅ Success' if x else '❌ Failed')
            
            st.dataframe(
                display_log[['Timestamp', 'Action', 'Message', 'Status']],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No healing activities recorded yet")
        
except Exception as e:
    st.error(f"Error displaying healing log: {e}")

# Healing recommendations
st.header("💡 Optimization Recommendations")

try:
    # Get system info for recommendations
    cpu_info = st.session_state.monitor.get_cpu_details()
    memory_info = st.session_state.monitor.get_memory_usage()
    disk_info = st.session_state.monitor.get_disk_usage()
    
    recommendations = []
    
    # CPU recommendations
    if cpu_info['percent'] > 80:
        recommendations.append({
            'category': 'CPU',
            'priority': 'High',
            'recommendation': 'Consider closing unnecessary applications or upgrading CPU',
            'action': 'Terminate high CPU processes'
        })
    elif cpu_info['percent'] > 60:
        recommendations.append({
            'category': 'CPU',
            'priority': 'Medium',
            'recommendation': 'Monitor CPU usage and consider optimization',
            'action': 'Review running processes'
        })
    
    # Memory recommendations
    if memory_info['percent'] > 90:
        recommendations.append({
            'category': 'Memory',
            'priority': 'High',
            'recommendation': 'Critical memory usage - immediate action required',
            'action': 'Free memory and close applications'
        })
    elif memory_info['percent'] > 75:
        recommendations.append({
            'category': 'Memory',
            'priority': 'Medium',
            'recommendation': 'High memory usage - consider adding more RAM',
            'action': 'Memory cleanup and optimization'
        })
    
    # Disk recommendations
    for disk in disk_info:
        if disk['percent'] > 90:
            recommendations.append({
                'category': 'Disk',
                'priority': 'High',
                'recommendation': f'Critical disk space on {disk["device"]} - clean up files',
                'action': 'Disk cleanup and temp file removal'
            })
        elif disk['percent'] > 80:
            recommendations.append({
                'category': 'Disk',
                'priority': 'Medium',
                'recommendation': f'Low disk space on {disk["device"]} - monitor usage',
                'action': 'Schedule regular cleanup'
            })
    
    if recommendations:
        for rec in recommendations:
            priority_color = "🔴" if rec['priority'] == 'High' else "🟡"
            st.info(f"{priority_color} **{rec['category']}** ({rec['priority']} Priority): {rec['recommendation']}")
            st.write(f"   💡 Suggested action: {rec['action']}")
    else:
        st.success("🟢 No optimization recommendations at this time. System is performing well!")

except Exception as e:
    st.error(f"Error generating recommendations: {e}")

# Footer
st.markdown("---")
st.markdown(f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
           f"Auto-healing: {'🟢 Active' if st.session_state.healing_enabled else '🔴 Inactive'}")

# Auto-refresh if healing is enabled
if st.session_state.healing_enabled:
    time.sleep(5)
    st.rerun()

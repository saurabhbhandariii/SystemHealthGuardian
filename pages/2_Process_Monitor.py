import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psutil
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Process Monitor",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Process Monitor")
st.markdown("### Real-time Process Monitoring and Management")

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
    st.header("🎛️ Controls")
    
    auto_refresh = st.checkbox("Auto Refresh (3s)", value=True)
    
    if st.button("🔄 Refresh Now"):
        st.rerun()
    
    st.divider()
    
    # Filter options
    st.subheader("🔽 Filters")
    min_cpu = st.slider("Min CPU Usage (%)", 0.0, 100.0, 0.0, 0.1)
    min_memory = st.slider("Min Memory Usage (MB)", 0.0, 1000.0, 0.0, 10.0)
    
    process_status_filter = st.selectbox(
        "Process Status",
        ["All", "running", "sleeping", "disk-sleep", "stopped", "zombie"]
    )
    
    st.divider()
    
    # Process management
    st.subheader("⚙️ Management")
    
    if st.button("🛑 Kill High CPU Processes", type="primary"):
        with st.spinner("Terminating high CPU processes..."):
            try:
                result = st.session_state.healer.kill_high_cpu_processes(cpu_threshold=80.0)
                if result['success']:
                    st.success(f"✅ Terminated {len(result['killed_processes'])} processes")
                    for proc in result['killed_processes']:
                        st.write(f"- {proc['name']} (PID: {proc['pid']}, CPU: {proc['cpu_percent']:.1f}%)")
                else:
                    st.error(f"❌ {result['message']}")
            except Exception as e:
                st.error(f"Error: {e}")

# Main content
try:
    # Get process data
    with st.spinner("Loading process data..."):
        processes = st.session_state.monitor.get_running_processes()
    
    if not processes:
        st.warning("No process data available")
        st.stop()
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(processes)
    
    # Clean and prepare data
    df['cpu_percent'] = df['cpu_percent'].fillna(0)
    df['memory_percent'] = df['memory_percent'].fillna(0)
    df['memory_mb'] = df['memory_mb'].fillna(0)
    
    # Apply filters
    if min_cpu > 0:
        df = df[df['cpu_percent'] >= min_cpu]
    
    if min_memory > 0:
        df = df[df['memory_mb'] >= min_memory]
    
    if process_status_filter != "All":
        df = df[df['status'] == process_status_filter]
    
    # Summary statistics
    st.header("📊 Process Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Processes", len(df))
    
    with col2:
        high_cpu_count = len(df[df['cpu_percent'] > 50])
        st.metric("High CPU Processes", high_cpu_count)
    
    with col3:
        high_memory_count = len(df[df['memory_mb'] > 500])
        st.metric("High Memory Processes", high_memory_count)
    
    with col4:
        zombie_count = len(df[df['status'] == 'zombie'])
        st.metric("Zombie Processes", zombie_count)
    
    # Charts
    st.header("📈 Process Analysis")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Top Processes by CPU Usage")
        top_cpu = df.nlargest(10, 'cpu_percent')[['name', 'cpu_percent', 'pid']]
        
        if not top_cpu.empty:
            fig_cpu = px.bar(
                top_cpu, 
                x='cpu_percent', 
                y='name',
                orientation='h',
                title='Top 10 CPU Consuming Processes',
                labels={'cpu_percent': 'CPU Usage (%)', 'name': 'Process Name'},
                hover_data=['pid']
            )
            fig_cpu.update_layout(height=400)
            st.plotly_chart(fig_cpu, use_container_width=True)
        else:
            st.info("No processes meet the CPU filter criteria")
    
    with chart_col2:
        st.subheader("Top Processes by Memory Usage")
        top_memory = df.nlargest(10, 'memory_mb')[['name', 'memory_mb', 'pid']]
        
        if not top_memory.empty:
            fig_memory = px.bar(
                top_memory, 
                x='memory_mb', 
                y='name',
                orientation='h',
                title='Top 10 Memory Consuming Processes',
                labels={'memory_mb': 'Memory Usage (MB)', 'name': 'Process Name'},
                hover_data=['pid']
            )
            fig_memory.update_layout(height=400)
            st.plotly_chart(fig_memory, use_container_width=True)
        else:
            st.info("No processes meet the memory filter criteria")
    
    # Process status distribution
    st.subheader("Process Status Distribution")
    status_counts = df['status'].value_counts()
    
    if not status_counts.empty:
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Distribution of Process States"
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Detailed process table
    st.header("📋 Detailed Process List")
    
    # Display options
    display_col1, display_col2 = st.columns(2)
    
    with display_col1:
        show_system_processes = st.checkbox("Show System Processes", value=False)
        
    with display_col2:
        rows_to_show = st.selectbox("Rows to Display", [25, 50, 100, 200], index=1)
    
    # Filter system processes if requested
    if not show_system_processes:
        system_processes = [
            'System', 'Registry', 'smss.exe', 'csrss.exe', 'wininit.exe',
            'winlogon.exe', 'services.exe', 'lsass.exe', 'svchost.exe',
            'spoolsv.exe', 'dwm.exe'
        ]
        df = df[~df['name'].isin(system_processes)]
    
    # Prepare display dataframe
    display_df = df[['name', 'pid', 'cpu_percent', 'memory_mb', 'memory_percent', 
                    'status', 'create_time_formatted', 'username']].copy()
    
    display_df.columns = [
        'Process Name', 'PID', 'CPU %', 'Memory (MB)', 'Memory %', 
        'Status', 'Started', 'User'
    ]
    
    # Sort by CPU usage descending
    display_df = display_df.sort_values('CPU %', ascending=False)
    
    # Display the table
    st.dataframe(
        display_df.head(rows_to_show),
        use_container_width=True,
        hide_index=True,
        column_config={
            "CPU %": st.column_config.ProgressColumn(
                "CPU %",
                help="CPU usage percentage",
                min_value=0,
                max_value=100,
                format="%.1f%%"
            ),
            "Memory %": st.column_config.ProgressColumn(
                "Memory %",
                help="Memory usage percentage",
                min_value=0,
                max_value=100,
                format="%.1f%%"
            ),
            "Memory (MB)": st.column_config.NumberColumn(
                "Memory (MB)",
                help="Memory usage in megabytes",
                format="%.1f MB"
            )
        }
    )
    
    # Process termination section
    st.header("🛑 Process Management")
    
    st.warning("⚠️ **Warning**: Terminating processes can cause system instability. Use with caution!")
    
    termination_col1, termination_col2 = st.columns(2)
    
    with termination_col1:
        st.subheader("Terminate by PID")
        pid_to_kill = st.number_input("Enter Process ID (PID)", min_value=1, value=1, step=1)
        
        if st.button("🛑 Terminate Process", type="primary"):
            try:
                # Safety check - don't allow termination of critical system processes
                critical_pids = [0, 4]  # System processes
                if pid_to_kill in critical_pids:
                    st.error("❌ Cannot terminate critical system process!")
                else:
                    process = psutil.Process(pid_to_kill)
                    process_name = process.name()
                    
                    # Confirm termination
                    if st.button(f"⚠️ Confirm termination of {process_name} (PID: {pid_to_kill})", 
                                type="secondary"):
                        process.terminate()
                        st.success(f"✅ Process {process_name} (PID: {pid_to_kill}) terminated")
                        st.session_state.logger.log_system_event(
                            "process_termination", 
                            f"Manually terminated process {process_name} (PID: {pid_to_kill})"
                        )
                        time.sleep(1)
                        st.rerun()
                        
            except psutil.NoSuchProcess:
                st.error("❌ Process not found!")
            except psutil.AccessDenied:
                st.error("❌ Access denied! Run as administrator to terminate this process.")
            except Exception as e:
                st.error(f"❌ Error terminating process: {e}")
    
    with termination_col2:
        st.subheader("Bulk Operations")
        
        if st.button("🧹 Clean Zombie Processes", type="secondary"):
            try:
                zombie_processes = df[df['status'] == 'zombie']
                if not zombie_processes.empty:
                    cleaned_count = 0
                    for _, proc in zombie_processes.iterrows():
                        try:
                            process = psutil.Process(proc['pid'])
                            process.terminate()
                            cleaned_count += 1
                        except:
                            continue
                    
                    st.success(f"✅ Cleaned {cleaned_count} zombie processes")
                    st.session_state.logger.log_healing_action(
                        "clean_zombies", True, f"Cleaned {cleaned_count} zombie processes"
                    )
                else:
                    st.info("ℹ️ No zombie processes found")
            except Exception as e:
                st.error(f"❌ Error cleaning zombie processes: {e}")
        
        st.markdown("---")
        
        if st.button("💾 Force Memory Cleanup", type="secondary"):
            with st.spinner("Forcing memory cleanup..."):
                try:
                    result = st.session_state.healer.free_memory()
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")
                except Exception as e:
                    st.error(f"❌ Error during memory cleanup: {e}")

except Exception as e:
    st.error(f"Error loading process data: {e}")
    st.exception(e)

# Auto-refresh functionality
if auto_refresh:
    time.sleep(3)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
           f"Total system processes: {len(psutil.pids())}")

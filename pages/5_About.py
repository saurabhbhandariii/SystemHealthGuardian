import streamlit as st
from datetime import datetime
import platform
import psutil

# Page configuration
st.set_page_config(
    page_title="About",
    page_icon="ℹ️",
    layout="wide"
)

st.title("ℹ️ About Self-Healing System Monitor")

# Project header with logo/icon
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <h2>🔧 Self-Healing System Monitor</h2>
    <h4>Windows-Compatible System Monitoring & Auto-Resolution</h4>
</div>
""", unsafe_allow_html=True)

# Project overview
st.header("📋 Project Overview")

st.markdown("""
The **Self-Healing System Monitor** is a comprehensive Windows-compatible application designed to continuously monitor 
system resources and automatically resolve common performance issues. This project demonstrates advanced system 
programming concepts and real-time monitoring techniques using Python and Streamlit.

### 🎯 Key Features

- **Real-time Monitoring**: Continuous tracking of CPU, memory, disk, and network usage
- **Process Management**: Detailed process monitoring with termination capabilities
- **Self-Healing Capabilities**: Automatic detection and resolution of system issues
- **Smart Alerting**: Threshold-based alert system with multiple notification methods
- **Comprehensive Reporting**: Detailed system reports with export functionality
- **User-Friendly Interface**: Modern web-based dashboard built with Streamlit

### 🔧 Technical Implementation

- **Backend**: Python with psutil for system monitoring
- **Frontend**: Streamlit for interactive web interface
- **Visualization**: Plotly for real-time charts and graphs
- **Data Processing**: Pandas for data manipulation and analysis
- **Logging**: Comprehensive activity logging with rotation
- **Multi-threading**: Background processes for continuous monitoring
""")

# Team information
st.header("👥 Development Team")

st.markdown("""
This project was developed as part of a **Problem-Based Learning (PBL)** initiative for the **Operating System** course.
""")

# Team members in a professional layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎓 Team Members")
    
    # Team member cards
    team_members = [
        {
            "name": "SAURABH BHANDARI",
            "role": "Team Leader & Core Developer",
            "code_name": "CODE GEASS",
            "responsibilities": [
                "System architecture design",
                "Self-healing algorithms implementation", 
                "Process monitoring and management",
                "Project coordination"
            ]
        },
        {
            "name": "AKSHIT KUMAR", 
            "role": "Backend Developer",
            "responsibilities": [
                "System monitoring modules",
                "Alert management system",
                "Performance optimization",
                "Error handling and logging"
            ]
        },
        {
            "name": "BRIJESH SINGH",
            "role": "Frontend Developer", 
            "responsibilities": [
                "User interface design",
                "Data visualization",
                "Report generation system",
                "User experience optimization"
            ]
        },
        {
            "name": "ARYAN ARORA",
            "role": "Testing & Documentation",
            "responsibilities": [
                "System testing and validation",
                "Documentation and user guides",
                "Bug detection and resolution",
                "Quality assurance"
            ]
        }
    ]
    
    for i, member in enumerate(team_members, 1):
        with st.expander(f"TM{i}: {member['name']}" + (f" ({member['code_name']})" if 'code_name' in member else "")):
            st.write(f"**Role:** {member['role']}")
            st.write("**Key Responsibilities:**")
            for resp in member['responsibilities']:
                st.write(f"- {resp}")

with col2:
    st.subheader("🏫 Academic Information")
    
    st.markdown("""
    **Course:** Operating System (PBL Project)  
    **Institution:** [Your Institution Name]  
    **Semester:** [Current Semester]  
    **Academic Year:** [Current Academic Year]  
    
    **Under the Guidance of:**  
    **Prof. Susheela Ma'am**
    
    ---
    
    ### 📚 Learning Objectives
    
    This project was designed to provide hands-on experience with:
    
    - **System Programming**: Working with OS APIs and system calls
    - **Process Management**: Understanding process lifecycle and control
    - **Memory Management**: Monitoring and optimizing memory usage  
    - **File System Operations**: Managing temporary files and disk space
    - **Multi-threading**: Implementing concurrent system monitoring
    - **Real-time Systems**: Building responsive monitoring applications
    - **User Interface Design**: Creating intuitive system administration tools
    """)

# Technical specifications
st.header("⚙️ Technical Specifications")

tech_col1, tech_col2 = st.columns(2)

with tech_col1:
    st.subheader("🛠️ Technology Stack")
    
    st.markdown("""
    **Core Technologies:**
    - Python 3.8+
    - Streamlit (Web Framework)
    - psutil (System Monitoring)
    - Plotly (Data Visualization)
    - Pandas (Data Processing)
    
    **Key Libraries:**
    - `threading` - Background processing
    - `subprocess` - System command execution  
    - `logging` - Activity logging
    - `json` - Data serialization
    - `datetime` - Time-based operations
    
    **Platform Support:**
    - Windows 10/11
    - Windows Server 2016+
    - Cross-platform compatibility (Linux, macOS)
    """)

with tech_col2:
    st.subheader("📊 System Requirements")
    
    st.markdown("""
    **Minimum Requirements:**
    - Windows 10 or later
    - Python 3.8+
    - 4GB RAM
    - 100MB disk space
    - Administrator privileges (recommended)
    
    **Recommended Requirements:**
    - Windows 11
    - Python 3.10+
    - 8GB RAM
    - 500MB disk space
    - SSD storage for optimal performance
    
    **Network Requirements:**
    - No internet connection required for core functionality
    - Optional: SMTP server for email notifications
    """)

# Features and capabilities
st.header("🚀 Features & Capabilities")

feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    st.subheader("📊 Monitoring")
    st.markdown("""
    - **CPU Usage**: Real-time per-core monitoring
    - **Memory**: RAM and swap space tracking
    - **Disk Space**: Multi-drive capacity monitoring  
    - **Network**: I/O statistics and interface status
    - **Processes**: Detailed process information
    - **Services**: Windows service status monitoring
    """)

with feature_col2:
    st.subheader("🛠️ Self-Healing")
    st.markdown("""
    - **Process Management**: Automatic high-CPU process termination
    - **Memory Optimization**: Garbage collection and cache clearing
    - **Disk Cleanup**: Temporary file removal
    - **Service Recovery**: Automatic service restart
    - **Threshold Management**: Configurable alert thresholds
    - **Smart Scheduling**: Intelligent healing intervals
    """)

with feature_col3:
    st.subheader("🔔 Alerting")
    st.markdown("""
    - **Real-time Alerts**: Instant threshold notifications
    - **Multiple Channels**: Desktop, sound, email notifications
    - **Alert History**: Comprehensive alert logging
    - **Severity Levels**: Critical, warning, and info alerts
    - **Custom Thresholds**: User-configurable limits
    - **Alert Analytics**: Statistical analysis and trends
    """)

# System information display
st.header("💻 Current System Information")

try:
    # Get system information
    system_info = {
        "Operating System": platform.platform(),
        "System": platform.system(),
        "Release": platform.release(), 
        "Version": platform.version(),
        "Architecture": platform.architecture()[0],
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
        "Boot Time": datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
        "CPU Cores (Logical)": psutil.cpu_count(logical=True),
        "CPU Cores (Physical)": psutil.cpu_count(logical=False),
        "Total Memory": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
        "Available Memory": f"{psutil.virtual_memory().available / (1024**3):.2f} GB"
    }
    
    # Display in two columns
    info_col1, info_col2 = st.columns(2)
    
    items = list(system_info.items())
    mid_point = len(items) // 2
    
    with info_col1:
        for key, value in items[:mid_point]:
            st.write(f"**{key}:** {value}")
    
    with info_col2:
        for key, value in items[mid_point:]:
            st.write(f"**{key}:** {value}")

except Exception as e:
    st.error(f"Error retrieving system information: {e}")

# Project timeline and milestones
st.header("📅 Project Timeline")

st.markdown("""
### Development Phases

**Phase 1: Planning & Design** *(Week 1-2)*
- Requirements analysis and system design
- Architecture planning and technology selection
- Team role assignments and project setup

**Phase 2: Core Development** *(Week 3-6)*  
- System monitoring module implementation
- Self-healing algorithms development
- Alert system and logging framework

**Phase 3: UI Development** *(Week 7-8)*
- Streamlit interface design and implementation  
- Data visualization and reporting features
- User experience optimization

**Phase 4: Testing & Integration** *(Week 9-10)*
- System testing and bug fixes
- Performance optimization
- Documentation and final preparations

**Phase 5: Deployment & Presentation** *(Week 11-12)*
- Final testing and validation
- Project documentation completion
- Presentation preparation and delivery
""")

# Acknowledgments
st.header("🙏 Acknowledgments")

st.markdown("""
We would like to express our sincere gratitude to:

- **Prof. Susheela Ma'am** for her invaluable guidance and support throughout this project
- **[Institution Name]** for providing the platform and resources for this learning experience
- **The Open Source Community** for the excellent libraries and tools that made this project possible
- **Our Fellow Students** for their feedback, testing, and encouragement

### 📚 References and Resources

- **Python Documentation**: Official Python language documentation
- **Streamlit Documentation**: Streamlit framework guides and API reference
- **psutil Documentation**: System monitoring library documentation
- **Windows API Documentation**: Microsoft Windows development resources
- **Operating System Concepts**: Textbook by Abraham Silberschatz, Peter Galvin, and Greg Gagne

### 🔗 External Libraries

- **Streamlit**: Web application framework
- **psutil**: Cross-platform system monitoring library
- **Plotly**: Interactive visualization library
- **Pandas**: Data analysis and manipulation library
- **NumPy**: Numerical computing library
""")

# Contact and support
st.header("📞 Contact & Support")

contact_col1, contact_col2 = st.columns(2)

with contact_col1:
    st.subheader("📧 Team Contact")
    st.markdown("""
    For questions, feedback, or support regarding this project:
    
    **Project Repository**: [GitHub Link]  
    **Documentation**: [Documentation Link]  
    **Email**: [team.email@institution.edu]  
    **Project Lead**: SAURABH BHANDARI (CODE GEASS)
    """)

with contact_col2:
    st.subheader("🐛 Bug Reports & Features")
    st.markdown("""
    **Report Issues**: [GitHub Issues]  
    **Feature Requests**: [GitHub Discussions]  
    **Contributing**: [Contribution Guidelines]  
    **Code of Conduct**: [Code of Conduct]
    """)

# Version information
st.header("📝 Version Information")

version_info = {
    "Application Version": "1.0.0",
    "Release Date": datetime.now().strftime('%Y-%m-%d'),
    "Build Type": "Academic Project",
    "License": "Educational Use",
    "Last Updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

for key, value in version_info.items():
    st.write(f"**{key}:** {value}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>🎓 Self-Healing System Monitor | PBL Project - Operating System</p>
    <p>Under the guidance of <strong>Prof. Susheela Ma'am</strong></p>
    <p>Developed with ❤️ by Team [Your Team Name] | © 2024</p>
</div>
""", unsafe_allow_html=True)

# Easter egg - Development stats
if st.button("🎯 Show Development Statistics", help="Click to see development statistics"):
    st.balloons()
    
    dev_stats = {
        "Lines of Code": "~2,500+",
        "Files Created": "8+",
        "Features Implemented": "15+", 
        "Testing Hours": "50+",
        "Coffee Consumed": "∞ cups ☕",
        "Bugs Fixed": "100+",
        "Team Meetings": "25+",
        "Documentation Pages": "10+"
    }
    
    st.subheader("📊 Development Statistics")
    
    stats_col1, stats_col2 = st.columns(2)
    
    items = list(dev_stats.items())
    mid_point = len(items) // 2
    
    with stats_col1:
        for key, value in items[:mid_point]:
            st.metric(key, value)
    
    with stats_col2:
        for key, value in items[mid_point:]:
            st.metric(key, value)
    
    st.success("🎉 Thank you for exploring our project!")

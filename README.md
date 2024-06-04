# Host-Based Intrusion Detection System (HIDS)

## Overview
This project is a Host-Based Intrusion Detection System (HIDS) designed to monitor system activities, detect malicious behavior, and log security events. The system consists of multiple modules that work together to provide comprehensive monitoring and alerting capabilities, ensuring enhanced security for the host system.

## Features
- **Authentication Logging**: Monitors and logs authentication attempts, detects multiple failed login attempts, and provides alerts for suspicious activities.
- **Process and Command Monitoring**: Detects and terminates forbidden processes, monitors resource usage of whitelisted processes, and logs process activities.
- **Alerting System**: Sends real-time alerts via email and Slack for critical security events.
- **Comprehensive Logging**: Detailed logging of security events with configurable log file paths.
- **Extensible and Modular Design**: Facilitates future enhancements and maintenance.

## Technologies Used
- **Programming Language**: Python
- **Libraries**: `psutil`, `unittest`, `pytest`, `logging`, `smtplib`, `requests`
- **Tools**: Git, Pytest, Mocking

## Installation

1. **Clone the Repository**:
   git clone https://github.com/your-username/HostBasedIDS.git
   cd HostBasedIDS
2. **Create and Activate Virtual Environment**:
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. **Install Dependencies**:
pip install -r requirements.txt

## Configuration

1. **Logging Module** : Configure log file path and alerting settings in logging_module.py.
2. **Alerting** : Set up email and Slack alert configurations in logger.py and logging_module.py.

## Usasge

1. **Start The HIDS**:
python main.py

2. **Monitor Authentication Attempts**:
     - Ensure the authentication_log.py is configured to monitor relevant log files.
     - Logs authentication attempts and alerts on multiple failed attempts.
3. **Monitor Process and Commands**:
     - Monitor system processes using monitor_process_and_commands.py.
     - Detects and terminates forbidden processes and logs activities.

# Aurora Multi Tool 🛠️

A comprehensive Windows system utility suite that provides powerful tools for system maintenance, browser management, and hardware monitoring.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## 🚀 Features

- **Browser Management**
  - Clear browser cache and temporary files
  - Backup important browser data (bookmarks, history, passwords)
  - Restore browser data from backups

- **System Maintenance**
  - Automated system driver updates
  - Detailed system information reporting
  - Hardware monitoring and diagnostics

- **Utilities**
  - Generate random strings for various purposes
  - Perform disk speed tests
  - Analyze memory usage
  - Profile application performance
  - Monitor network activity
  - Perform network speed tests
  - Scan open ports on a target host

## 📋 Requirements

- Windows 10 or Windows 11
- Python 3.8 or higher
- Administrator privileges for some features

### Required Python Packages
```bash
psutil>=5.9.0
wmi>=1.5.1
```

## 🔧 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/NNKTV28/aurora-multi-tool.git
   cd aurora-multi-tool
   ```

2. **Create Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

1. **Start the Tool**
   ```bash
   python multi_tool.py
   ```

2. **Navigate the Menu**
   - Use numbers 1-14 to select different tools
   - Follow on-screen instructions for each tool
   - Press Enter to confirm selections

## 📁 Project Structure

```
aurora-multi-tool/
├── backups/
├── config/
├── logs/
├── tools/
│   ├── application_performance_profiler.py
│   ├── backup_browser.py
│   ├── clean_cache.py
│   ├── disk_speed_test.py
│   ├── generate_random_string.py
│   ├── memory_analysis.py
│   ├── network_monitor.py
│   ├── network_speed_test.py
│   ├── port_scanner.py
│   ├── restore_browser_backup.py
│   ├── settings_manager.py
│   ├── system_info.py
│   ├── update_drivers.py
├── config/
│   └── browser_backup_config.json
├── .gitignore
├── README.md
├── requirements.txt
└── multi_tool.py
```

## ⚙️ Configuration

- Configuration files are stored in `config/`
- Log files are automatically created in `logs/`
- Each tool can be configured through the Settings Manager

## 🤝 Contributing
1. Check our [Contribution community rules and code standards](https://github.com/NNKTV28/aurora-multi-tool/wiki/Contributing)
2. Fork the repository
3. Create your feature branch (`git checkout -b feature/AmazingFeature`)
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔰 Support

- Report bugs by creating an issue
- Request features through the issue tracker
- Check the [Wiki](../../wiki) for detailed documentation

## 🔄 Updates

Check the [releases page](../../releases) for latest versions and updates.

---

Made with ❤️ by [NNKTV28](https://github.com/NNKTV28)

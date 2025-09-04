# 🚀 Emergent Pentest Suite

A comprehensive penetration testing platform with integrated security tools and project management capabilities.

## ✨ Features

### 🔍 Security Tools
- **Subfinder** - Fast passive subdomain discovery
- **Amass** - In-depth attack surface mapping
- **Nmap** - Network discovery and port scanning
- **Nuclei** - Fast vulnerability scanner
- **ffuf** - Fast web fuzzer
- **Gobuster** - Directory and file brute-forcer

### 📊 Project Management
- Project creation and management
- Target tracking
- Note-taking system
- Dashboard with statistics

## 🛠️ Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Or manual setup: Python 3.8+, Node.js 16+, MongoDB

### 🐳 Docker Setup (Recommended)

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Check service status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

### 🔧 Manual Setup

#### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the backend directory:
   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=pentest_suite
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

4. **Start the backend server:**
   ```bash
   python -m uvicorn server:app --reload --host 127.0.0.1 --port 8001
   ```

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

## 🧪 Testing the Tools

### Backend Test
Run the comprehensive test script to verify all tools are working:

```bash
python backend_test.py
```

This will test:
- Health check endpoint
- Tools status endpoint
- All 6 security tools (Subfinder, Amass, Nmap, Nuclei, ffuf, Gobuster)

### Manual Testing
You can also test individual endpoints:

```bash
# Health check
curl http://localhost:8001/health

# Tools status
curl http://localhost:8001/api/tools/status

# Test a tool (e.g., Subfinder)
curl -X POST http://localhost:8001/api/tools/subfinder \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com"}'
```

## 🔧 Tool Configuration

### Real Tools vs Mock Data
The backend automatically detects if security tools are installed on the system:

- **If tools are available**: Uses real tool execution
- **If tools are not available**: Falls back to realistic mock data

### Installing Security Tools (Optional)
For real tool execution, install these tools:

```bash
# Subfinder
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Amass
go install -v github.com/owasp-amass/amass/v4/...@master

# Nmap
# Download from https://nmap.org/download.html

# Nuclei
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

# ffuf
go install github.com/ffuf/ffuf@latest

# Gobuster
go install github.com/OJ/gobuster/v3@latest
```

## 📱 Usage

### 1. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001

### 2. Create a Project
- Navigate to Projects page
- Click "Create New Project"
- Fill in project details

### 3. Add Targets
- Select your project
- Add targets (domains, IPs, URLs)
- Mark targets as in-scope

### 4. Run Security Tools
- Go to Tools page
- Enter target in the input field
- Select and run desired tools
- View results in real-time

### 5. Take Notes
- Add findings and observations
- Tag notes for easy organization
- Link notes to specific projects

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI** - Modern Python web framework
- **MongoDB** - Document database for projects and notes
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation and serialization

### Frontend (React)
- **React 18** - Modern UI framework
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn/ui** - Beautiful component library
- **Lucide React** - Icon library

### API Endpoints
```
GET  /health                    - Health check
GET  /                          - Root endpoint
GET  /api/tools/status         - Tools availability status
POST /api/tools/{tool_name}    - Execute security tool
GET  /api/projects             - List projects
POST /api/projects             - Create project
GET  /api/notes                - List notes
POST /api/notes                - Create note
```

## 🔒 Security Considerations

- All tool executions are sandboxed
- Input validation on all endpoints
- CORS configuration for development
- No sensitive data logging

## 🚨 Troubleshooting

### Backend Won't Start
- Check if port 8001 is available
- Verify MongoDB connection
- Check Python dependencies

### Tools Not Working
- Run `python backend_test.py` to diagnose
- Check if tools are installed and in PATH
- Verify tool permissions

### Frontend Can't Connect
- Ensure backend is running on port 8001
- Check CORS configuration
- Verify API_BASE_URL in frontend

## 📈 Roadmap

### Phase 1 (Current)
- ✅ Basic project management
- ✅ Note-taking system
- ✅ 6 security tools integration
- ✅ Mock data fallback

### Phase 2 (Next)
- 🔄 Result visualization
- 🔄 Workflow automation
- 🔄 Custom script support
- 🔄 Team collaboration

### Phase 3 (Future)
- 🔮 Advanced reporting
- 🔮 Integration with other tools
- 🔮 Machine learning insights
- 🔮 Cloud deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

---

**Happy Penetration Testing! 🎯**

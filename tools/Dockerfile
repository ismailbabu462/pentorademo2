# Pentest Tools Docker Image
# Contains all necessary penetration testing tools
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TOOLS_DIR=/opt/tools
ENV PATH="${TOOLS_DIR}:${PATH}"

# Update package list and install basic dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    nmap \
    dirb \
    nikto \
    sqlmap \
    hydra \
    john \
    hashcat \
    aircrack-ng \
    wireshark \
    tcpdump \
    netcat \
    telnet \
    ftp \
    ssh \
    golang-go \
    && rm -rf /var/lib/apt/lists/*

# Create tools directory
RUN mkdir -p ${TOOLS_DIR}

# Install modern pentest tools
RUN cd ${TOOLS_DIR} && \
    # Install Subfinder (compatible version)
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.6.3 && \
    # Install Amass (compatible version)
    go install -v github.com/owasp-amass/amass/v3/...@v3.23.3 && \
    # Install Nuclei (compatible version)
    go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@v2.9.15 && \
    # Install FFuF (compatible version)
    go install github.com/ffuf/ffuf@v2.1.0 && \
    # Install Gobuster (compatible version)
    go install github.com/OJ/gobuster/v3@v3.6.0

# Create wordlists directory and download common wordlists
RUN mkdir -p /usr/share/wordlists && \
    cd /usr/share/wordlists && \
    # Download SecLists
    git clone https://github.com/danielmiessler/SecLists.git && \
    # Download common directories
    wget -O common_dirs.txt https://raw.githubusercontent.com/v0re/dirsearch/master/db/directories.txt || true

# Create a simple wordlist for basic testing
RUN echo -e "admin\nbackup\nconfig\n.env\nphpinfo.php\nrobots.txt\nsitemap.xml\n.git\n.svn\nwp-admin\nwp-content\nwp-includes\napi\nv1\nv2\ndocs\nhelp\nsupport\ncontact\nabout\nlogin\nregister\ndashboard\npanel\nconsole\nshell\ntest\ndev\nstaging\nbeta\nold\narchive\ntemp\ntmp" > /usr/share/wordlists/common.txt

# Set up working directory
WORKDIR /workspace

# Create a non-root user for security
RUN useradd -m -s /bin/bash pentester && \
    chown -R pentester:pentester /workspace && \
    chown -R pentester:pentester ${TOOLS_DIR}

# Switch to non-root user
USER pentester

# Verify tool installations
RUN nmap --version && \
    nikto -Version

# Set default command
CMD ["/bin/bash"]

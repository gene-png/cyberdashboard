FROM mcr.microsoft.com/devcontainers/python:3.11

# System tools Claude is likely to need
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        curl \
        jq \
        sqlite3 \
        less \
        ripgrep \
        pandoc \
        ca-certificates \
        gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 (required for Claude Code)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI from the official repo
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code globally via npm
RUN npm install -g @anthropic-ai/claude-code

# Pre-create workspace dir with correct ownership
RUN mkdir -p /workspace && chown vscode:vscode /workspace

WORKDIR /workspace

USER vscode
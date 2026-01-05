#!/bin/bash
# Build Docker sandbox image

echo "🔨 Building secure sandbox image..."

docker build -f docker/sandbox.Dockerfile -t openpanda-sandbox:latest .

if [ $? -eq 0 ]; then
    echo "✅ Sandbox image built successfully"
    echo "📋 To enable Docker mode: export USE_DOCKER_SANDBOX=true"
else
    echo "❌ Error during build"
    exit 1
fi


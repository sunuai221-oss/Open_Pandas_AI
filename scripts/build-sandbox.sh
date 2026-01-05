#!/bin/bash
# Construction de l'image sandbox Docker

echo "🔨 Construction de l'image sandbox sécurisée..."

docker build -f docker/sandbox.Dockerfile -t openpanda-sandbox:latest .

if [ $? -eq 0 ]; then
    echo "✅ Image sandbox construite avec succès"
    echo "📋 Pour activer le mode Docker : export USE_DOCKER_SANDBOX=true"
else
    echo "❌ Erreur lors de la construction"
    exit 1
fi


#!/bin/bash
# ============================================================================
# E2E Test Runner for Open Pandas-AI (Linux/Mac)
# ============================================================================

set -e

PORT=${PORT:-8501}
HEADED=${HEADED:-false}

echo "============================================"
echo "Open Pandas-AI E2E Test Runner"
echo "============================================"

# Install Playwright browsers
echo ""
echo "[1/4] Installing Playwright browsers..."
python -m playwright install chromium

# Start the application
echo ""
echo "[2/4] Starting application..."

if command -v docker-compose &> /dev/null; then
    echo "Using Docker Compose..."
    docker-compose up -d
    APP_STARTED_WITH_DOCKER=true
else
    echo "Starting Streamlit directly..."
    streamlit run app.py --server.port=$PORT --server.headless=true &
    APP_PID=$!
    APP_STARTED_WITH_DOCKER=false
fi

# Wait for the application to be ready
echo ""
echo "[3/4] Waiting for application to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
APP_READY=false

while [ "$APP_READY" = false ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" | grep -q "200"; then
        APP_READY=true
        echo "Application is ready!"
    else
        echo "Waiting... ($RETRY_COUNT/$MAX_RETRIES)"
    fi
done

if [ "$APP_READY" = false ]; then
    echo "Application failed to start within timeout"
    if [ "$APP_STARTED_WITH_DOCKER" = true ]; then
        docker-compose down
    else
        kill $APP_PID 2>/dev/null || true
    fi
    exit 1
fi

# Run E2E tests
echo ""
echo "[4/4] Running E2E tests..."

export E2E_BASE_URL="http://localhost:$PORT"

PYTEST_ARGS="tests/e2e/ -v -m e2e"
if [ "$HEADED" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS --headed"
fi

pytest $PYTEST_ARGS
TEST_RESULT=$?

# Cleanup
echo ""
echo "Cleaning up..."

if [ "$APP_STARTED_WITH_DOCKER" = true ]; then
    docker-compose down
else
    kill $APP_PID 2>/dev/null || true
fi

echo ""
echo "============================================"
if [ $TEST_RESULT -eq 0 ]; then
    echo "E2E Tests PASSED"
else
    echo "E2E Tests FAILED"
fi
echo "============================================"

exit $TEST_RESULT

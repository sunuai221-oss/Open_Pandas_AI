FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /sandbox

# Install minimal dependencies for execution
# openpyxl is included for future Excel operations even though to_excel is blocked
RUN pip install --no-cache-dir pandas==2.1.4 openpyxl==3.1.5 xlrd==2.0.1

# Copy only necessary utilities
COPY core/utils.py /sandbox/
COPY core/sandbox_runner.py /sandbox/

# Non-privileged user for enhanced security
RUN useradd -m -u 1000 sandbox
USER sandbox

# Entry point for code execution
ENTRYPOINT ["python", "sandbox_runner.py"]


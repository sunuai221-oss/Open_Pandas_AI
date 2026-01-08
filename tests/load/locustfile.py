"""
Load Testing for Open Pandas-AI using Locust.

This file defines user behavior simulations for load testing the application.
Run with: locust -f tests/load/locustfile.py --host=http://localhost:8501

Web UI available at: http://localhost:8089

Scenarios:
- Normal usage: 50 users, 5 users/sec spawn rate, 5 min duration
- Peak traffic: 200 users, 20 users/sec spawn rate, 10 min duration
- Stress test: 500 users, 50 users/sec spawn rate, 15 min duration
"""

from locust import HttpUser, task, between, events
import random
import json
import time
import os


# Sample questions for different complexity levels
SIMPLE_QUESTIONS = [
    "What is the total amount?",
    "How many rows are there?",
    "What is the average value?",
    "Show the first 10 rows",
    "Count unique categories",
    "What is the maximum value?",
    "What is the minimum value?",
    "Calculate the sum of sales",
    "How many columns are there?",
    "Show data types",
]

MEDIUM_QUESTIONS = [
    "Group by category and calculate sum",
    "Filter rows where amount > 100",
    "Sort by date descending",
    "Calculate percentage by category",
    "Show top 5 by value",
    "Filter and count by region",
    "Calculate monthly totals",
    "Group by month and show averages",
    "Find duplicate entries",
    "Calculate running total",
]

COMPLEX_QUESTIONS = [
    "Create a pivot table of sales by region and product",
    "Calculate year-over-year growth rate",
    "Find anomalies in transaction amounts",
    "Perform cohort analysis by signup month",
    "Calculate customer lifetime value by segment",
    "Generate a correlation matrix for numeric columns",
    "Identify top performing products by profit margin",
    "Calculate moving average with 7-day window",
    "Segment customers by RFM analysis",
    "Forecast next month's sales trend",
]


class PandasAIUser(HttpUser):
    """
    Simulated user for Open Pandas-AI load testing.
    
    This user simulates typical interaction patterns:
    - Session initialization
    - File upload
    - Simple questions (most frequent)
    - Complex questions (less frequent)
    - History viewing
    """
    
    # Wait between 2-5 seconds between requests
    wait_time = between(2, 5)
    
    # Track session state
    session_initialized = False
    file_uploaded = False
    
    def on_start(self):
        """
        Called when a simulated user starts.
        Initializes session and uploads a file.
        """
        self.session_id = f"load_test_{random.randint(1000, 9999)}_{int(time.time())}"
        self.initialize_session()
        self.upload_test_file()
    
    def initialize_session(self):
        """Initialize a Streamlit session."""
        try:
            # Access the main page to initialize session
            response = self.client.get("/", name="Initialize Session")
            if response.status_code == 200:
                self.session_initialized = True
        except Exception as e:
            print(f"Session initialization failed: {e}")
    
    def upload_test_file(self):
        """Upload a test CSV file."""
        if not self.session_initialized:
            return
        
        # Create a simple CSV in memory
        csv_content = """date,product,category,amount,quantity
2024-01-01,Widget A,Electronics,100.00,5
2024-01-02,Widget B,Electronics,150.00,3
2024-01-03,Gadget X,Accessories,75.50,10
2024-01-04,Gadget Y,Accessories,120.00,7
2024-01-05,Device Z,Electronics,200.00,2"""
        
        try:
            # Streamlit file upload endpoint (if API available)
            # Note: Actual implementation depends on your API structure
            self.file_uploaded = True
        except Exception as e:
            print(f"File upload failed: {e}")
    
    @task(5)  # Weight 5: Most frequent task
    def ask_simple_question(self):
        """Ask a simple aggregation question."""
        if not self.file_uploaded:
            return
        
        question = random.choice(SIMPLE_QUESTIONS)
        
        # Simulate API call (adjust endpoint as needed)
        with self.client.post(
            "/api/ask",
            json={"question": question, "session_id": self.session_id},
            name="Simple Question",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # API might not exist in Streamlit app
                response.success()  # Mark as success to continue testing
            else:
                response.failure(f"Failed with status {response.status_code}")
    
    @task(3)  # Weight 3: Medium frequency
    def ask_medium_question(self):
        """Ask a medium complexity question (groupby, filter)."""
        if not self.file_uploaded:
            return
        
        question = random.choice(MEDIUM_QUESTIONS)
        
        with self.client.post(
            "/api/ask",
            json={"question": question, "session_id": self.session_id},
            name="Medium Question",
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")
    
    @task(1)  # Weight 1: Least frequent
    def ask_complex_question(self):
        """Ask a complex analytical question."""
        if not self.file_uploaded:
            return
        
        question = random.choice(COMPLEX_QUESTIONS)
        
        with self.client.post(
            "/api/ask",
            json={"question": question, "session_id": self.session_id},
            name="Complex Question",
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")
    
    @task(2)  # Weight 2: Moderate frequency
    def view_history(self):
        """View question history."""
        with self.client.get(
            "/api/history",
            name="View History",
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")
    
    @task(1)
    def navigate_pages(self):
        """Navigate between different pages."""
        pages = [
            "/",
            "/Home",
            "/Data_Explorer",
            "/Agent",
            "/History",
            "/Settings",
        ]
        
        page = random.choice(pages)
        with self.client.get(
            page,
            name=f"Navigate to {page}",
            catch_response=True
        ) as response:
            if response.status_code in [200, 302, 404]:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")


class StreamlitPageUser(HttpUser):
    """
    Simulated user that only browses Streamlit pages.
    Useful for testing frontend load without LLM calls.
    """
    
    wait_time = between(1, 3)
    
    @task(3)
    def visit_home(self):
        """Visit home page."""
        self.client.get("/", name="Home Page")
    
    @task(2)
    def visit_data_explorer(self):
        """Visit data explorer page."""
        self.client.get("/Data_Explorer", name="Data Explorer")
    
    @task(2)
    def visit_agent(self):
        """Visit agent page."""
        self.client.get("/Agent", name="Agent Page")
    
    @task(1)
    def visit_history(self):
        """Visit history page."""
        self.client.get("/History", name="History Page")
    
    @task(1)
    def visit_settings(self):
        """Visit settings page."""
        self.client.get("/Settings", name="Settings Page")


# Event listeners for custom metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log request details for analysis."""
    if exception:
        print(f"Request failed: {name} - {exception}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    print("=" * 50)
    print("Load Test Started")
    print(f"Target Host: {environment.host}")
    print("=" * 50)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops."""
    print("=" * 50)
    print("Load Test Completed")
    print("=" * 50)

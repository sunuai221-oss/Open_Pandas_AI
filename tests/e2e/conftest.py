"""
Pytest configuration for E2E tests with Playwright.
"""

import pytest
from playwright.sync_api import Page, Browser, BrowserContext, Playwright
import os
import time

# Base URL for the Streamlit application
BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8501")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with extended timeout."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for the application."""
    return BASE_URL


@pytest.fixture
def app_page(page: Page, base_url: str) -> Page:
    """Navigate to the application and wait for it to load."""
    page.goto(base_url)
    # Wait for Streamlit to fully load
    page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
    return page


@pytest.fixture
def fixtures_path():
    """Return path to test fixtures directory."""
    return os.path.join(os.path.dirname(__file__), "..", "fixtures")


def wait_for_streamlit_load(page: Page, timeout: int = 30000):
    """Wait for Streamlit application to fully load."""
    try:
        # Wait for main app container
        page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=timeout)
        # Wait for any spinners to disappear
        page.wait_for_selector("div[data-testid='stSpinner']", state="hidden", timeout=5000)
    except Exception:
        pass  # Spinner might not exist
    
    # Small delay for Streamlit's internal state
    time.sleep(1)


def upload_file_to_streamlit(page: Page, file_path: str, timeout: int = 10000):
    """Upload a file to Streamlit file uploader."""
    # Find file input
    file_input = page.locator("input[type='file']").first
    file_input.set_input_files(file_path)
    
    # Wait for upload to process
    time.sleep(2)


def click_streamlit_button(page: Page, button_text: str, timeout: int = 10000):
    """Click a Streamlit button by its text content."""
    button = page.get_by_role("button", name=button_text)
    button.click()


def fill_streamlit_text_input(page: Page, placeholder: str, value: str):
    """Fill a Streamlit text input by placeholder."""
    input_field = page.locator(f"input[placeholder*='{placeholder}']").first
    input_field.fill(value)


def get_streamlit_metric_value(page: Page, label: str) -> str:
    """Get the value of a Streamlit metric by its label."""
    metric = page.locator(f"div[data-testid='stMetric']:has-text('{label}')")
    value = metric.locator("div[data-testid='stMetricValue']").inner_text()
    return value

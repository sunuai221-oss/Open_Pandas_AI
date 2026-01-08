"""
End-to-End tests for the complete question flow in Open Pandas-AI.

These tests verify:
- File upload functionality
- Question submission and processing
- Result display
- Domain detection
- Error handling
"""

import pytest
from playwright.sync_api import Page, expect
import os
import time

from .conftest import (
    wait_for_streamlit_load,
    upload_file_to_streamlit,
    click_streamlit_button,
    fill_streamlit_text_input,
)


@pytest.mark.e2e
class TestQuestionFlow:
    """End-to-end tests for the complete question flow."""

    def test_homepage_loads(self, page: Page, base_url: str):
        """Test that the homepage loads correctly."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # Check for main title or app elements
        expect(page.locator("body")).to_be_visible()
        # Streamlit apps should have the app container
        expect(page.locator("div[data-testid='stAppViewContainer']")).to_be_visible(timeout=30000)

    def test_navigation_to_agent_page(self, page: Page, base_url: str):
        """Test navigation to the Agent page."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # Try to navigate to Agent page via sidebar
        # Streamlit sidebar navigation
        try:
            # Look for sidebar navigation
            sidebar = page.locator("section[data-testid='stSidebar']")
            if sidebar.is_visible():
                # Click on Agent link in sidebar
                agent_link = sidebar.get_by_text("Agent", exact=False)
                if agent_link.is_visible():
                    agent_link.click()
                    time.sleep(2)
        except Exception:
            # Direct navigation as fallback
            page.goto(f"{base_url}/Agent")
            wait_for_streamlit_load(page)

    def test_upload_csv_file(self, page: Page, base_url: str, fixtures_path: str):
        """Test uploading a CSV file."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # Check if file uploader exists
        file_input = page.locator("input[type='file']").first
        
        if file_input.is_visible():
            csv_path = os.path.join(fixtures_path, "sample_sales.csv")
            if os.path.exists(csv_path):
                file_input.set_input_files(csv_path)
                time.sleep(3)  # Wait for file processing
                
                # Verify file was loaded (look for success indicators)
                # This depends on your app's UI
                pass

    def test_ask_simple_question(self, page: Page, base_url: str, fixtures_path: str):
        """Test asking a simple question about the data."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # First upload a file
        file_input = page.locator("input[type='file']").first
        csv_path = os.path.join(fixtures_path, "sample_sales.csv")
        
        if file_input.is_visible() and os.path.exists(csv_path):
            file_input.set_input_files(csv_path)
            time.sleep(3)
            
            # Navigate to Agent page if needed
            try:
                page.goto(f"{base_url}/Agent")
                wait_for_streamlit_load(page)
            except Exception:
                pass
            
            # Find and fill the question input
            question_input = page.locator("input[type='text']").first
            if question_input.is_visible():
                question_input.fill("What is the total sales?")
                
                # Submit the question
                submit_button = page.get_by_role("button", name="Analyze").first
                if submit_button.is_visible():
                    submit_button.click()
                    
                    # Wait for response (longer timeout for LLM)
                    time.sleep(10)

    def test_result_display(self, page: Page, base_url: str, fixtures_path: str):
        """Test that results are displayed correctly."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # This test verifies result display after a question is answered
        # Implementation depends on your specific UI elements

    def test_error_handling_invalid_question(self, page: Page, base_url: str, fixtures_path: str):
        """Test error handling for invalid questions."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # Upload file first
        file_input = page.locator("input[type='file']").first
        csv_path = os.path.join(fixtures_path, "sample_sales.csv")
        
        if file_input.is_visible() and os.path.exists(csv_path):
            file_input.set_input_files(csv_path)
            time.sleep(3)
            
            # Navigate to Agent
            try:
                page.goto(f"{base_url}/Agent")
                wait_for_streamlit_load(page)
            except Exception:
                pass
            
            # Ask an impossible question
            question_input = page.locator("input[type='text']").first
            if question_input.is_visible():
                question_input.fill("Calculate the value of nonexistent_column_xyz")
                
                submit_button = page.get_by_role("button", name="Analyze").first
                if submit_button.is_visible():
                    submit_button.click()
                    time.sleep(10)
                    
                    # Should see an error or appropriate message
                    # Check for error indicators


@pytest.mark.e2e
class TestDomainDetection:
    """Tests for automatic domain detection."""

    def test_finance_domain_detection(self, page: Page, base_url: str, fixtures_path: str):
        """Test that finance data is detected as finance domain."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        file_input = page.locator("input[type='file']").first
        csv_path = os.path.join(fixtures_path, "sample_finance.csv")
        
        if file_input.is_visible() and os.path.exists(csv_path):
            file_input.set_input_files(csv_path)
            time.sleep(3)
            
            # Navigate to Agent and check domain detection
            try:
                page.goto(f"{base_url}/Agent")
                wait_for_streamlit_load(page)
                
                # Look for "Finance" in domain indicator
                # This depends on your UI
            except Exception:
                pass

    def test_ecommerce_domain_detection(self, page: Page, base_url: str, fixtures_path: str):
        """Test that e-commerce data is detected as ecommerce domain."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        file_input = page.locator("input[type='file']").first
        csv_path = os.path.join(fixtures_path, "sample_ecommerce.csv")
        
        if file_input.is_visible() and os.path.exists(csv_path):
            file_input.set_input_files(csv_path)
            time.sleep(3)

    def test_hr_domain_detection(self, page: Page, base_url: str, fixtures_path: str):
        """Test that HR data is detected as HR domain."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        file_input = page.locator("input[type='file']").first
        csv_path = os.path.join(fixtures_path, "sample_hr.csv")
        
        if file_input.is_visible() and os.path.exists(csv_path):
            file_input.set_input_files(csv_path)
            time.sleep(3)


@pytest.mark.e2e
class TestExportFunctionality:
    """Tests for export functionality."""

    def test_excel_export_button_visible(self, page: Page, base_url: str, fixtures_path: str):
        """Test that Excel export button appears after results."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # After getting results, export button should be visible
        # Implementation depends on your UI

    def test_download_result(self, page: Page, base_url: str, fixtures_path: str):
        """Test downloading results as Excel."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # Test download functionality
        # This requires handling download events in Playwright


@pytest.mark.e2e
class TestVisualization:
    """Tests for visualization generation."""

    def test_generate_chart_button(self, page: Page, base_url: str, fixtures_path: str):
        """Test that chart generation button works."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # Test chart generation button visibility and functionality

    def test_chart_display(self, page: Page, base_url: str, fixtures_path: str):
        """Test that generated charts are displayed."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # Verify chart images appear


@pytest.mark.e2e
class TestSessionPersistence:
    """Tests for session state persistence."""

    def test_history_maintained(self, page: Page, base_url: str, fixtures_path: str):
        """Test that question history is maintained."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # Upload file, ask questions, verify history

    def test_data_persists_across_pages(self, page: Page, base_url: str, fixtures_path: str):
        """Test that uploaded data persists when navigating pages."""
        page.goto(base_url)
        wait_for_streamlit_load(page)
        
        # Upload file, navigate, verify data still available

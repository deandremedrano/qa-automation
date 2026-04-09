25 tests passing in the cloud with a green badge! Your qa-automation repo is now a genuinely impressive portfolio piece.
Let's update the README to reflect the expanded test suite. Open README.md in VS Code, select all with CMD + A, delete, and paste this updated version:
markdown# QA Automation Test Suite

[![QA Automation Tests](https://github.com/deandremedrano/qa-automation/actions/workflows/test.yml/badge.svg)](https://github.com/deandremedrano/qa-automation/actions/workflows/test.yml)

A professional Selenium-based automated test suite built with Python and pytest. Tests are generated using an AI-powered test case generator and executed automatically against web applications via CI/CD pipeline.

## What This Is

A comprehensive automated regression test suite covering functional, edge case, negative, UI, and security testing scenarios for login form functionality. Built as part of a full QA automation pipeline where AI generates test cases and Selenium executes them automatically.

## Tech Stack

- Python 3.13
- Selenium WebDriver 4
- pytest
- pytest-html (test reporting)
- webdriver-manager (auto manages ChromeDriver)
- Chrome browser (headless)
- GitHub Actions CI/CD

## Test Coverage

### Functional Tests (10)
- Valid login with correct credentials
- Invalid username shows error
- Invalid password shows error
- Empty fields validation
- Logout functionality
- Page title verification
- Username field presence
- Password field presence
- Login button presence
- Login button text verification

### Edge Cases (7)
- Empty username only
- Empty password only
- Username with leading/trailing spaces
- Password case sensitivity
- Special characters in username
- Very long username (100 chars)
- Very long password (100 chars)

### Negative Tests (4)
- SQL injection via username field
- SQL injection via password field
- Numeric only username
- Numeric only password

### UI Tests (4)
- Page loads correctly
- Error message is dismissable
- Login form is present
- Secure area heading after login

### Results
- Total tests: 25
- Passed: 25
- Failed: 0
- Pass rate: 100%

## Prerequisites

- Python 3.8 or higher
- Google Chrome installed
- pip

## Setup

1. Clone this repository:

git clone https://github.com/deandremedrano/qa-automation.git
cd qa-automation

2. Install dependencies:

pip3 install selenium pytest webdriver-manager pytest-html

## Running Tests

Run all tests:

pytest test_login.py -v

Run with HTML report:

pytest test_login.py -v --html=report.html --self-contained-html

Run a specific test:

pytest test_login.py::test_valid_login -v

## CI/CD Pipeline

This repo uses GitHub Actions to automatically run all 25 tests on every push to main. The status badge above shows the current pipeline status. HTML test reports are generated and uploaded as artifacts on every run.

## How It Works

Each test automatically launches Chrome in headless mode, navigates to the target URL, performs the test actions, validates the expected result, and closes the browser. webdriver-manager handles ChromeDriver installation automatically.

## Pipeline

This automation suite is part of a larger QA pipeline:
1. AI generates test cases from feature descriptions
2. Test cases are documented in Notion
3. Selenium scripts automate the execution
4. pytest reports pass/fail results
5. GitHub Actions runs all 25 tests automatically on every push
6. HTML reports are generated and stored as artifacts

## Author

Built by Deandre Medrano
# QA Automation Test Suite

A professional Selenium-based automated test suite built with Python and pytest. Tests are generated using an AI-powered test case generator and executed automatically against web applications.

## What This Is

This is a automated regression test suite for login form functionality, built as part of a full QA automation pipeline. Test cases were generated using a custom AI tool and implemented using industry standard automation frameworks.

## Tech Stack

- Python 3.13
- Selenium WebDriver 4
- pytest
- webdriver-manager (auto manages ChromeDriver)
- Chrome browser

## Test Coverage

### Functional Tests
- TC001 — Valid login with correct credentials
- TC002 — Invalid username shows error message
- TC003 — Invalid password shows error message
- TC004 — Empty fields shows error message
- TC005 — Logout returns to login page

### Results
- Total tests: 5
- Passed: 5
- Failed: 0
- Execution time: ~15 seconds

## Prerequisites

- Python 3.8 or higher
- Google Chrome installed
- pip

## Setup

1. Clone this repository:

git clone https://github.com/9j77k8ffzw-coder/qa-automation.git
cd qa-automation

2. Install dependencies:

pip3 install selenium pytest webdriver-manager

## Running Tests

Run all tests:

pytest test_login.py -v

Run a specific test:

pytest test_login.py::test_valid_login -v

## How It Works

Each test case automatically launches Chrome, navigates to the target URL, performs the test actions, validates the expected result, and closes the browser. webdriver-manager handles ChromeDriver installation automatically so no manual setup is needed.

## Test Site

Tests run against The Internet by Dave Haeffner, a practice site built specifically for QA automation training:
https://the-internet.herokuapp.com/login

## Pipeline

This automation suite is part of a larger QA pipeline:
1. AI generates test cases from feature descriptions
2. Test cases are documented in Notion
3. Selenium scripts automate the execution
4. pytest reports pass/fail results

## Author

Built by Deandre Medrano
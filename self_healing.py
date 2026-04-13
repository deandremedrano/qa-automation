#!/usr/bin/env python3
"""
Self-Healing Test Suite Engine
Automatically diagnoses and fixes failing tests using local AI.
Author: Deandre Medrano

Usage:
  python3 self_healing.py                 # Run and heal all tests
  python3 self_healing.py --dry-run       # Diagnose without fixing
  python3 self_healing.py --test file.py  # Run specific test file
"""

import subprocess
import sys
import json
import re
import os
import requests
import datetime
import argparse
import shutil

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5-coder:latest"
VERSION = "1.0.0"

class C:
    BLUE   = "\033[94m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"
    CYAN   = "\033[96m"

def blue(s):   return f"{C.BLUE}{s}{C.RESET}"
def green(s):  return f"{C.GREEN}{s}{C.RESET}"
def yellow(s): return f"{C.YELLOW}{s}{C.RESET}"
def red(s):    return f"{C.RED}{s}{C.RESET}"
def bold(s):   return f"{C.BOLD}{s}{C.RESET}"
def dim(s):    return f"{C.DIM}{s}{C.RESET}"
def cyan(s):   return f"{C.CYAN}{s}{C.RESET}"

def print_banner():
    print(f"\n{bold(blue('  Self-Healing Test Suite'))} {dim(f'v{VERSION}')}")
    print(f"  {dim('AI-powered test diagnosis and repair — by Deandre Medrano')}")
    print(f"  {dim('Powered by Qwen2.5 Coder · Runs locally · Zero cloud · Eco-friendly')}\n")

def print_divider(title=""):
    width = 64
    if title:
        pad = (width - len(title) - 2) // 2
        print(f"\n{dim('─' * pad)} {cyan(title)} {dim('─' * pad)}\n")
    else:
        print(dim("─" * width))

def print_step(n, total, msg):
    print(f"\n{blue(f'[{n}/{total}]')} {bold(msg)}")

def print_success(msg): print(f"  {green('✓')} {msg}")
def print_fail(msg):    print(f"  {red('✗')} {msg}")
def print_warning(msg): print(f"  {yellow('⚠')} {msg}")
def print_info(msg):    print(f"  {dim('→')} {msg}")

def run_tests(test_file):
    print_info(f"Running: pytest {test_file} -v --tb=short")
    result = subprocess.run(
        ["python3", "-m", "pytest", test_file, "-v", "--tb=short", "--no-header"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(test_file)) or "."
    )
    output = result.stdout + result.stderr
    passed = []
    failed = []
    errors = []
    for line in output.split("\n"):
        if " PASSED" in line and "::" in line:
            test_name = line.split("::")[1].split(" ")[0]
            passed.append(test_name.strip())
        elif " FAILED" in line and "::" in line:
            test_name = line.split("::")[1].split(" ")[0]
            failed.append(test_name.strip())
        elif " ERROR" in line and "::" in line:
            test_name = line.split("::")[1].split(" ")[0]
            errors.append(test_name.strip())
    summary_match = re.search(r"(\d+) passed", output)
    if summary_match and not passed:
        passed = [f"test_{i}" for i in range(int(summary_match.group(1)))]
    return {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "output": output,
        "return_code": result.returncode
    }

def extract_failure_details(test_name, full_output):
    lines = full_output.split("\n")
    failure_lines = []
    capture = False
    for i, line in enumerate(lines):
        if test_name in line and "FAILED" in line:
            capture = True
            start = max(0, i - 2)
            failure_lines = lines[start:i+1]
        if capture:
            failure_lines.append(line)
            if len(failure_lines) > 30:
                break
    return "\n".join(failure_lines) if failure_lines else full_output[:2000]

def read_test_file(filepath):
    with open(filepath, "r") as f:
        return f.read()

def extract_test_function(source, test_name):
    lines = source.split("\n")
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if f"def {test_name}(" in line:
            start_idx = i
        elif start_idx is not None and i > start_idx:
            if (line.startswith("def ") or line.startswith("class ")) and line.strip():
                end_idx = i
                break
    if start_idx is None:
        return ""
    end_idx = end_idx or len(lines)
    return "\n".join(lines[start_idx:end_idx])

def call_ai(system, user):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                "stream": True
            },
            stream=True,
            timeout=180
        )
        full_content = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if data.get("message", {}).get("content"):
                        chunk = data["message"]["content"]
                        full_content += chunk
                        print(chunk, end="", flush=True)
                except:
                    pass
        print()
        return full_content
    except requests.exceptions.ConnectionError:
        print(red("\n✗ Cannot connect to Ollama. Make sure Ollama is running."))
        sys.exit(1)

def diagnose_failure(test_name, test_code, failure_output, full_source):
    system = """You are an expert Python and Selenium QA engineer.
Analyze a failing test and provide a clear diagnosis.

Format your response exactly like this:

## Diagnosis: [test name]

**Root Cause:** [One clear sentence explaining why the test failed]

**Failure Type:** [Element Not Found / Timing Issue / Assertion Error / Network Error / Selector Changed / Logic Error / Other]

**Confidence:** [High / Medium / Low]

**Technical Details:**
[2-3 sentences of technical explanation]

**Fix Required:**
[Exactly what needs to change to fix this test]"""

    user = f"""Diagnose this failing test:

TEST NAME: {test_name}

FAILING TEST CODE:
{test_code}

FAILURE OUTPUT:
{failure_output}

FULL TEST FILE CONTEXT:
{full_source[:3000]}

What is the root cause and what needs to change?"""

    return call_ai(system, user)

def heal_test(test_name, test_code, failure_output, diagnosis, full_source):
    system = """You are an expert Python Selenium QA engineer specializing in fixing broken tests.

Rewrite the failing test function to make it pass.

CRITICAL RULES:
1. Output ONLY the fixed Python function — no explanations, no markdown, no backticks
2. Keep the same test name and purpose
3. Fix the root cause identified in the diagnosis
4. Use WebDriverWait with expected_conditions for reliability
5. Keep the same imports — do not add new ones
6. The fix must be minimal — change only what is necessary
7. The function must start with def test_ and be properly indented"""

    user = f"""Fix this failing test:

TEST NAME: {test_name}

ORIGINAL FAILING CODE:
{test_code}

FAILURE OUTPUT:
{failure_output}

DIAGNOSIS:
{diagnosis}

FULL SOURCE CONTEXT:
{full_source[:2000]}

Output ONLY the fixed Python function. No explanations. No markdown. Just raw Python code starting with def {test_name}"""

    return call_ai(system, user)

def apply_fix(filepath, test_name, healed_code):
    source = read_test_file(filepath)
    healed_code = re.sub(r"```python\n?", "", healed_code)
    healed_code = re.sub(r"```\n?", "", healed_code)
    healed_code = healed_code.strip()
    if not healed_code.startswith(f"def {test_name}"):
        lines = healed_code.split("\n")
        for i, line in enumerate(lines):
            if line.startswith(f"def {test_name}"):
                healed_code = "\n".join(lines[i:])
                break
    lines = source.split("\n")
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if f"def {test_name}(" in line:
            start_idx = i
        elif start_idx is not None and i > start_idx:
            if (line.startswith("def ") or line.startswith("class ")) and line.strip():
                end_idx = i
                break
    if start_idx is None:
        return False
    end_idx = end_idx or len(lines)
    new_lines = lines[:start_idx] + healed_code.split("\n") + [""] + lines[end_idx:]
    new_source = "\n".join(new_lines)
    backup_path = filepath + ".backup"
    shutil.copy2(filepath, backup_path)
    with open(filepath, "w") as f:
        f.write(new_source)
    return True

def verify_fix(test_file, test_name):
    result = subprocess.run(
        ["python3", "-m", "pytest", f"{test_file}::{test_name}", "-v", "--tb=short", "--no-header"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def save_healing_report(report):
    reports_dir = os.path.expanduser("~/aidria-reports")
    os.makedirs(reports_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(reports_dir, f"healing_report_{timestamp}.md")
    content = f"""# Self-Healing Test Report
**Date:** {datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")}
**Engine:** AIdria Self-Healing Test Suite v{VERSION}
**Model:** {MODEL} (local)
**Test File:** {report['test_file']}

## Summary
- Total tests run: {report['total']}
- Initially passing: {report['initial_passed']}
- Initially failing: {report['initial_failed']}
- Successfully healed: {report['healed']}
- Failed to heal: {report['unhealed']}
- Final pass rate: {report['final_pass_rate']}%

## Healing Results

"""
    for r in report['results']:
        status = "HEALED" if r['healed'] else "UNHEALED"
        content += f"### {r['test']} — {status}\n\n"
        content += f"**Root Cause:** {r.get('diagnosis_summary', 'See diagnosis')}\n\n---\n\n"
    content += f"""## Environment
- OS: macOS (Apple Silicon M3)
- Python: {sys.version.split()[0]}
- AI Model: {MODEL} (running locally)
- Privacy: 100% local — no data sent to cloud

*Generated by AIdria Self-Healing Test Suite*
*Built by Deandre Medrano*
"""
    with open(filepath, "w") as f:
        f.write(content)
    return filepath

def run_healing_engine(test_file, dry_run=False, max_attempts=2):
    print_banner()
    print_divider("INITIALIZING SELF-HEALING ENGINE")

    if not os.path.exists(test_file):
        print(red(f"✗ Test file not found: {test_file}"))
        sys.exit(1)

    print_info(f"Test file: {bold(test_file)}")
    print_info(f"AI Model: {bold(MODEL)} (local)")
    print_info(f"Mode: {bold('DRY RUN — diagnosis only' if dry_run else 'HEALING MODE — will fix failures')}")

    print_divider("STEP 1 — RUNNING TEST SUITE")
    results = run_tests(test_file)

    passed_count = len(results['passed'])
    failed_count = len(results['failed'])
    error_count = len(results['errors'])
    total = passed_count + failed_count + error_count

    print(f"\n  {green(str(passed_count) + ' passed')}  {red(str(failed_count) + ' failed')}  {yellow(str(error_count) + ' errors')}  {dim('(' + str(total) + ' total)')}")

    if not results['failed'] and not results['errors']:
        print_divider()
        print(f"\n  {green('✓')} {bold('All tests passing!')} No healing needed.")
        print(dim("  Your test suite is healthy.\n"))
        return

    all_failing = results['failed'] + results['errors']
    print(f"\n  {yellow('Failing tests:')}")
    for t in all_failing:
        print(f"  {red('✗')} {t}")

    full_source = read_test_file(test_file)
    healing_results = []
    healed_count = 0

    for idx, test_name in enumerate(all_failing):
        print_divider(f"HEALING {idx + 1}/{len(all_failing)} — {test_name}")

        test_code = extract_test_function(full_source, test_name)
        if not test_code:
            print_warning(f"Could not extract function: {test_name}")
            healing_results.append({"test": test_name, "healed": False, "diagnosis_summary": "Could not extract function"})
            continue

        print_step(1, 3 if not dry_run else 2, "Diagnosing failure...")
        failure_details = extract_failure_details(test_name, results['output'])
        diagnosis = diagnose_failure(test_name, test_code, failure_details, full_source)

        diagnosis_summary = "See full report"
        for line in diagnosis.split("\n"):
            if "Root Cause:" in line:
                diagnosis_summary = line.replace("**Root Cause:**", "").strip()
                break

        if dry_run:
            healing_results.append({"test": test_name, "healed": False, "diagnosis_summary": diagnosis_summary})
            print_warning("Dry run — skipping fix")
            continue

        healed = False
        attempt = 1
        for attempt in range(1, max_attempts + 1):
            print_step(2, 3, f"Generating fix (attempt {attempt}/{max_attempts})...")
            healed_code = heal_test(test_name, test_code, failure_details, diagnosis, full_source)

            print_step(3, 3, "Applying and verifying fix...")
            if apply_fix(test_file, test_name, healed_code):
                full_source = read_test_file(test_file)
                if verify_fix(test_file, test_name):
                    healed = True
                    healed_count += 1
                    print_success(f"{bold(test_name)} — {green('HEALED SUCCESSFULLY')}")
                    break
                else:
                    print_warning(f"Fix attempt {attempt} did not pass — {'retrying...' if attempt < max_attempts else 'giving up'}")
                    backup = test_file + ".backup"
                    if os.path.exists(backup):
                        shutil.copy2(backup, test_file)
                        full_source = read_test_file(test_file)
            else:
                print_warning("Could not apply fix to file")

        if not healed:
            print_fail(f"{bold(test_name)} — {red('COULD NOT HEAL')}")
            print_info("Manual intervention required — see diagnosis above")

        healing_results.append({
            "test": test_name,
            "healed": healed,
            "diagnosis_summary": diagnosis_summary,
            "attempts": attempt
        })

    print_divider("HEALING COMPLETE")

    unhealed = len(all_failing) - healed_count
    final_pass_rate = round(((passed_count + healed_count) / total) * 100) if total > 0 else 100

    print(f"\n  {bold('Session Summary')}")
    print(f"  {'─' * 40}")
    print(f"  Tests run:           {total}")
    print(f"  Initially passing:   {passed_count}")
    print(f"  Initially failing:   {len(all_failing)}")
    print(f"  Successfully healed: {healed_count}")
    print(f"  Could not heal:      {unhealed}")
    print(f"  Final pass rate:     {final_pass_rate}%\n")

    if not dry_run and healing_results:
        report = {
            "test_file": test_file,
            "total": total,
            "initial_passed": passed_count,
            "initial_failed": len(all_failing),
            "healed": healed_count,
            "unhealed": unhealed,
            "final_pass_rate": final_pass_rate,
            "results": healing_results
        }
        report_path = save_healing_report(report)
        print_success(f"Full report saved to: {bold(report_path)}")

    if healed_count > 0:
        print(f"\n  {green('✓')} {bold(str(healed_count) + ' test(s) automatically healed by AI')}")
        print(dim("  Review the changes in your test file before committing"))
        print(dim("  A .backup file was created in case you need to revert"))

    if unhealed > 0:
        print(f"\n  {yellow('⚠')} {bold(str(unhealed) + ' test(s) require manual attention')}")
        print(dim("  See diagnosis above for root cause analysis"))

    print()

def main():
    parser = argparse.ArgumentParser(
        prog="self_healing",
        description="AIdria Self-Healing Test Suite — AI-powered test repair",
        add_help=True
    )
    parser.add_argument("--test", default="test_login.py", help="Test file to run (default: test_login.py)")
    parser.add_argument("--dry-run", action="store_true", help="Diagnose failures without fixing them")
    parser.add_argument("--attempts", type=int, default=2, help="Max healing attempts per test (default: 2)")
    args = parser.parse_args()
    run_healing_engine(args.test, args.dry_run, args.attempts)

if __name__ == "__main__":
    main()
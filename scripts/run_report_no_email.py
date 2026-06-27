"""
Script to run the ocean report without email.

Examples:

# Preview HTML in browser
uv run scripts/run_report_no_email.py --html

# Preview text in terminal
uv run scripts/run_report_no_email.py --text

# Both previews
uv run scripts/run_report_no_email.py --html --text

# Short versions work too
uv run scripts/run_report_no_email.py -H -T

# Run in test mode
uv run scripts/run_report_no_email.py --test

# Combine everything
uv run scripts/run_report_no_email.py --html --text --test
"""

import argparse
import subprocess
from pathlib import Path

import ocean_report

RUN_EMAIL = False


def preview_html():
    """Open the latest HTML email preview in the browser."""
    script_path = Path(__file__).parent.parent / "help" / "bin" / "preview-email.sh"
    try:
        subprocess.run(["bash", str(script_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running HTML preview: {e}")
    except FileNotFoundError:
        print(f"❌ Preview script not found: {script_path}")


def preview_text():
    """Display the latest text email preview in the terminal."""
    script_path = Path(__file__).parent.parent / "help" / "bin" / "preview-email-txt.sh"
    try:
        subprocess.run(["bash", str(script_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running text preview: {e}")
    except FileNotFoundError:
        print(f"❌ Preview script not found: {script_path}")


def main():
    """
    Run Ocean report without email
    """
    parser = argparse.ArgumentParser(
        description="Run ocean report without sending email"
    )
    parser.add_argument(
        "--html",
        "-H",
        action="store_true",
        help="Open HTML email preview in browser after generating report",
    )
    parser.add_argument(
        "--text",
        "-T",
        action="store_true",
        help="Display text email preview in terminal after generating report",
    )
    parser.add_argument("--test", action="store_true", help="Run in test mode")

    args = parser.parse_args()

    # Check to see if the package is installed
    ocean_report.hello()

    # Run Report
    ocean_report.run_report(run_email=RUN_EMAIL, test=args.test)

    # Auto-preview if requested
    if args.html:
        print("\n" + "=" * 80)
        preview_html()

    if args.text:
        print("\n" + "=" * 80)
        preview_text()


if __name__ == "__main__":
    main()

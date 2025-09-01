import ocean_report

RUN_EMAIL = False
TEST = False

def main():
    """
    Run Ocean report email
    """
    ocean_report.hello()
    ocean_report.main(run_email=RUN_EMAIL, test=TEST)
    return None


if __name__ == "__main__":
    main()

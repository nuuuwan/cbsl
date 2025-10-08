from scraper import GlobalReadMe


def main():
    GlobalReadMe(
        {
            "cbsl": [
                "cbsl_annual_reports",
            ]
        }
    ).build()


if __name__ == "__main__":
    main()

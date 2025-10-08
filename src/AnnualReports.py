import sys

from scraper import AbstractPDFDoc, GlobalReadMe
from utils import WWW, Log

log = Log("AnnualReports")


class AnnualReports(AbstractPDFDoc):

    @classmethod
    def get_doc_class_label(cls) -> str:
        return "cbsl_annual_reports"

    @classmethod
    def get_doc_class_description(cls) -> str:
        return " ".join(
            [
                "Annual Reports of the Central Bank of Sri Lanka (CBSL)."
                + "It has been discountinued since 2023"
                + "and replaced with swo separate reports,"
                + "namely, the Annual Economic Review"
                + "and Financial Statements"
                + "and Operations of the Central Bank."
            ]
        )

    @classmethod
    def get_doc_class_emoji(cls) -> str:
        return "📙"

    @classmethod
    def gen_docs(cls):
        url = (
            "https://www.cbsl.gov.lk"
            + "/en/publications/economic-and-financial-reports/annual-reports"
        )
        www = WWW(url)
        soup = www.soup

        h3_list = soup.find_all("h3")
        for h3 in h3_list:
            description = h3.text.strip()
            if "Annual Report" not in description:
                continue
            year = description[-4:]
            assert year.isdigit(), description

            a = h3.find("a")
            url_pdf = a["href"]
            assert url_pdf.endswith(".pdf"), url_pdf

            doc = AbstractPDFDoc(
                num=year,
                date_str=f"{year}-12-31",
                description=description,
                url_metadata=url,
                lang="en",
                url_pdf=url_pdf,
            )
            yield doc

    @classmethod
    def run_pipeline(cls, max_dt=None):
        max_dt = (
            max_dt
            or (float(sys.argv[2]) if len(sys.argv) > 2 else None)
            or cls.MAX_DT
        )
        log.debug(f"{max_dt=}s")

        cls.cleanup_all()
        cls.scrape_all_metadata(max_dt)
        cls.write_all()
        cls.scrape_all_extended_data(max_dt)
        cls.build_summary()
        cls.build_doc_class_readme()
        cls.build_and_upload_to_hugging_face()

        if not cls.is_multi_doc():
            GlobalReadMe(
                {cls.get_repo_name(): [cls.get_doc_class_label()]}
            ).build()

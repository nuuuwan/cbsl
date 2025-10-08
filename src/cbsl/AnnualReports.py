import re
import sys
from itertools import chain

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
    def clean_description(cls, description: str) -> str:
        description = re.sub(r"[^a-zA-Z0-9\s]", "", description)
        description = re.sub(r"\s+", " ", description)
        description = description.strip()
        return description.lower().replace(" ", "-")

    @classmethod
    def gen_docs_from_report_url(cls, url_report, year):
        www = WWW(url_report)
        soup = www.soup
        div_article = soup.find("div", class_="article")
        assert div_article
        a_list = div_article.find_all("a")
        for a in a_list:
            href = a.get("href", "")
            if not href.endswith(".pdf"):
                continue
            url_pdf = href
            if "https://www.cbsl.gov.lk" not in url_pdf:
                url_pdf = "https://www.cbsl.gov.lk" + url_pdf
            description = a.text.strip()
            num = url_pdf.split("/")[-1].replace(".pdf", "")
            yield cls(
                num=num,
                date_str=f"{year}-01-01",
                description=description,
                url_metadata=url_report,
                lang="en",
                url_pdf=url_pdf,
            )

    @classmethod
    def gen_report_urls_new(cls):
        url = (
            "https://www.cbsl.gov.lk"
            + "/en/publications/economic-and-financial-reports/annual-reports"
        )
        www = WWW(url)
        soup = www.soup

        table = soup.find("table")
        assert table
        for tr in table.find_all("tr"):
            for td in tr.find_all("td"):
                p = td.find("p")
                if not p:
                    continue
                a = td.find("a")
                if not a:
                    continue
                href = a["href"]
                url_report = (
                    "https://www.cbsl.gov.lk"
                    + "/en/publications/economic-and-financial-reports/"
                    + href
                )
                year = p.text.strip()[-4:]
                if not year.isdigit():
                    continue
                yield (url_report, year)

    @classmethod
    def gen_report_urls_old(cls):
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
            if not year.isdigit():
                continue
            a = h3.find("a")
            if not a:
                continue

            href = a["href"]
            url_report = (
                "https://www.cbsl.gov.lk"
                + "/en/publications/economic-and-financial-reports/"
                + href
            )
            yield (url_report, year)

    @classmethod
    def gen_docs(cls):
        for url_report, year in chain(
            cls.gen_report_urls_new(), cls.gen_report_urls_old()
        ):
            for doc in cls.gen_docs_from_report_url(url_report, year):
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

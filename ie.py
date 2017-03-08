import requests
import csv
from bs4 import BeautifulSoup
import xml.etree.cElementTree as et
import csv
from math import ceil
QUERY_HASH = {"abstract":"ab=",
              "author":"au=",
              "num_rec":"hc=",
              "fetch_start":"rs="}
IEEE_XPLORE_GATEWAY = "http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?"

def build_table_header():
    return ["Rank",
            "Title",
            "# of Authors",
            "# of Countries of Authors",
            "Number of Organizations of Authors",
            "Year",
            "Publication Type",
            "Publication Title",
            "Length of Abstract(Words)",
            "Length of Title",
            "Length of Paper"
            "CITATIONS",
            "NUM_VERSION"]


def buildtable(soup, newroot):
    table = [[] for _ in range(1000)]
    row = []
    i = 0

    for document in newroot:

        rank = int(document.rank.text)
        title_info = get_title_info(document)
        title = title_info[0]
        title_len = title_info[1]

        author_len = len(document.authors.text.split(';'))  # Gets the length of the authors

        countries = -1

        if document.affiliations is None:
            organizations = "None"
        else:
            organizations = len(document.affiliations.text.encode('utf-8').split(";"))

        if document.py is None:
            year = -1
        else:
            year = int(document.py.text)  # Published Year

        if document.pubtype is None:
            pubtype = "None"
        else:
            pubtype = str(document.pubtype.text.encode('utf-8'))  # Publication Type

        if document.pubtitle is None:
            pubtitle = "None"
        else:
            pubtitle = str(document.pubtitle.text.encode('utf-8')) # Publication title

        if document.abstract is None:
            abstract_len = -1
        else:
            abstract_len = len(document.abstract.text.encode('utf-8').split())  # Length of the abstract

        paper_length = get_paper_length(document)

        row = [rank, title, author_len, countries, organizations, year,
               pubtype, pubtitle, abstract_len, title_len, paper_length]
        table[i] = row
        i += 1

    return table


def get_title_info(document):
    if document.title is None:
        return "Missing Title", -1
    else:
        title = str(document.title.text.encode('utf-8'))  # Title
        title_len = len(title.split())  # Length of title
        return title, title_len


def get_paper_length(document):
    ill_format = "Inc. format"

    if document.spage is None or document.epage is None:
        return ill_format
    else:
        start_page = str(document.spage.text)
        end_page = str(document.epage.text)
        if start_page.isdigit() and end_page.isdigit():
            return int(end_page) - int(start_page)
        else:
            return ill_format


def build_query(fetch_start, hc):
    base_url = IEEE_XPLORE_GATEWAY
    base_url += (QUERY_HASH["abstract"])
    base_url += "software"
    base_url += "&"
    base_url += QUERY_HASH["num_rec"]
    base_url += str(hc)
    base_url += "&"
    base_url += QUERY_HASH["fetch_start"]
    base_url += str(fetch_start)
    print base_url
    return base_url


def run_queries():
    outfile = open("test.csv", 'wb')
    writer = csv.writer(outfile, delimiter=',')
    tableheader = build_table_header()
    writer.writerow(tableheader)

    cur_start = 1
    query = build_query(cur_start, 1)
    page = requests.get(query)
    soup = BeautifulSoup(page.content, 'html.parser')
    total_queries = float(soup.totalfound.text)
    total_queries = int(ceil(total_queries / 1000))

    for i in range(0, total_queries):
        query = build_query(cur_start, 1000)
        page = requests.get(query)
        soup = BeautifulSoup(page.content, 'html.parser')
        root = list(soup.children)[2]
        document = list(list(root.children)[5])  # Start of the documents in IEEE Gateway Tree

        cha = document[0]  # Need to remove u'\n'
        newroot = filter(lambda a: a != cha, root.children)  # Holds cleaned xml elements.
        newroot.pop(0)
        newroot.pop(0)  # Remove high-level data. Only contains documents

        table = buildtable(soup, newroot)  # Contains 1000 records. Need to re-query with new range.

        for row in table:
            writer.writerow(row)
        cur_start += 1000

    outfile.close()


def main():
    run_queries()


if __name__ == "__main__":
    main()

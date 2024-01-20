from collections import defaultdict
import pandas
import sys
import math

# TODO: find labels that can tear/split
# https://www.clasohlson.com/no/Selvheftende-etiketter/p/32-2618
# 70x37mm

# print settings:
# A4 with none margins and without headers and footers

template_doc = open("template_doc.html").read()
template_label = open("template_label.html").read()


class Page:
    def __init__(self, name, page, labels = None) -> None:
        self.name = name
        self.page = page
        self.labels = [] if labels is None else labels

    def add(self, label):
        self.labels.append(label)
        assert len(self.labels) <= 24

    def count(self) -> int:
        return len(self.labels)
    
    def full(self) -> bool:
        return len(self.labels) == 24
    
    def html(self):
        return template_doc.replace("BODY", "".join(self.labels))

    def write(self):
        if self.count() > 0:
            filename = f"out/{self.name}-{self.page}.html"
            print("Writing", filename)
            with open(filename, "w") as f:
                f.write(self.html())

    def next(self):
        return Page(self.name, self.page + 1)


def parse(filename: str):
    dataframe = pandas.read_csv(filename)
    records = dataframe.to_dict(orient="records")
    for r in records:
        # RaceSplitter start list, forventer følgende kolonner
        # Racer bib number,First name,Last name,Team,Skive
        # Add column Skive: =MOD(B1 - 1, 20) + 1
        # Export as: CSV (UTF-8 encoded)
        nummer = str(r["Racer bib number"])
        fornavn = r["First name"]
        etternavn = r["Last name"]
        assert isinstance(fornavn, str)
        assert isinstance(etternavn, str)
        navn = fornavn + " " + etternavn
        klubb = r["Team"]
        skive = str(r["Skive"])

        #if len(klubb) > 18:
        #    klubb = klubb[:18] + "..."

        if not navn:
            print("SKIP", r)
            continue

        # dataclass?
        yield {
            "NUMMER": nummer,
            "KLUBB": klubb,
            "NAVN": navn,
            "SKIVE": skive,
        }




def clubwise(records):
    klubber = defaultdict(list)
    for r in records:
        klubb = r["KLUBB"]
        klubber[klubb].append(r)

    if 0:
        for klubb, records in klubber.items():
            print(klubb, len(records))
        return
    for klubb, records in klubber.items():
        n = len(records)
        for r in records:
            yield r
        m = 3 - (n % 3)
        if m == 3:
            m = 0
        # print(klubb, len(records), m)
        assert (len(records) + m) % 3 == 0
        for i in range(m):
            yield {"KLUBB": klubb, "SKIVE": "", "NUMMER": "", "NAVN": ""}


def main():

    race = sys.argv[1]
    filename = sys.argv[2]

    page = Page(race, 1)

    # TODO: kutte lange navn og klubbnavn
    # TODO: shuffle clubs to avoid cuts and minimize sheets
    # e.g. fill large clubs with small ones
    # for o in parse(filename):
    for o in clubwise(parse(filename)):
            
        if page.full():
            page.write()
            page = page.next()

        html = template_label
        for k, v in o.items():
            html = html.replace(k, v)
        page.add(html)

    page.write()


if __name__ == "__main__":
    main()
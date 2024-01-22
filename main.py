from collections import defaultdict
import pandas
import sys
import math


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
    # Add column Skive: =MOD(B1 - 1, 20) + 1
    # Export as: CSV (UTF-8 encoded)

    dataframe = pandas.read_csv(filename)
    records = dataframe.to_dict(orient="records")
    for r in records:
        # print(r)

        if 0:
            # RaceSplitter start list, må legge til Skive
            nummer = str(r["Racer bib number"])
            fornavn = r["First name"]
            etternavn = r["Last name"]
            klubb = r["Team"]
            skive = str(r["Skive"])
        else:
            # Norske kolonner ala RecaSplitter
            nummer = str(r["Nummer"])
            fornavn = r["Fornavn"]
            etternavn = r["Etternavn"]
            klubb = r["Klubb"]
            skive = str(r["Skive"])

        # TODO: skive = (int(nummer) -1) % 20 + 1
    
        assert isinstance(fornavn, str)
        assert isinstance(etternavn, str)
        navn = fornavn + " " + etternavn
        print("NAME", len(navn), navn, repr(etternavn))

        # TODO: drop first names if name is long...
        maxlen = 25
        while len(navn) > maxlen and fornavn:
            fn = fornavn.split(" ")
            fornavn = " ".join(fn[:-1])
            if len(fn[-1]) > 1:
                init = fn[-1][0]
                fn[-1] = init
                fornavn += " " + init
            navn = fornavn + " " + etternavn
            print("NAMECUT", len(navn), navn)

        if not navn:
            print("SKIP", r)
            continue

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

        # fyll opp raden:
        m = 3 - (n % 3)
        if m == 3:
            m = 0
        assert (len(records) + m) % 3 == 0
        for i in range(m):
            yield {"KLUBB": klubb, "SKIVE": "...", "NUMMER": "...", "NAVN": "..."}


def main():

    race = sys.argv[1]
    filename = sys.argv[2]

    page = Page(race, 1)

    # TODO: skrive ut ubrukte startnummer for etteranmeldinger?
    # TODO: don't use end of nearly full sheets
    # TODO: shuffle clubs to avoid cuts and minimize sheets
    # e.g. fill large clubs with small ones

    # i rekkefølge av startnummer:
    # for o in parse(filename):

    # Samling av lapper fra samme klubb:
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
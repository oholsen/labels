import pandas

# https://www.clasohlson.com/no/Selvheftende-etiketter/p/32-2618

dataframe = pandas.read_csv("records.csv")
records = dataframe.to_dict(orient="records")


# print(records)

template_doc = open("template_doc.html").read()
template_label = open("template_label.html").read()
page_break = '<div class="page-break"></div>\n'

current_klubb = None

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
        if page.count() > 0:
            with open(f"out/{self.name}-{self.page}.html", "w") as f:
                f.write(self.html())

    def next(self):
        return Page(self.name, self.page + 1)


page = None
klubber = {}

for r in records:
    #print(r)
    nummer = str(r["Start nr"])
    if "Navn" in r:
        navn = str(r["Navn"])
    else:
        fornavn = str(r["Fornavn"])
        etternavn = str(r["Etternavn"])
        navn = fornavn + " " + etternavn

    klubb = str(r["Klubb"])
    skive = str(r["Skive"])
    klasse = str(r["Klasse"])
    if not klubb:
        continue

    # if klubb == "nan": continue

    if klubb != current_klubb:
        # labels.append(page_break)
        klubber[klubb] = []
        if page:
            page.write()
        page = Page(klubb, 1)
        current_klubb = klubb
        
    if page.full():
        # labels.append(page_break)
        page.write()
        page = page.next()

    # assert int(nummer) % 20 == int(skive), (nummer, skive)
    #print(nummer, skive, fornavn, etternavn, klubb)
    o = {
        "NUMMER": nummer,
        "KLUBB": klubb,
        "NAVN": navn,
        "SKIVE": skive,
    }
    html = template_label
    for k, v in o.items():
        html = html.replace(k, v)
    # html = template_label.replace("NUMMER", nummer).replace("KLUBB", klubb).replace("NAVN", navn).replace("SKIVE", skive)
    #print(html
    page.add(html)
    klubber[klubb].append(html)

    #break

#doc = template_doc.replace("BODY", "".join(labels))
#print(doc)

for k, v in klubber.items():
    print(k, len(v))

empty = ['<div class="label"></div>']
empty_line = empty * 3

def dump(klubb):
    Page(klubb, 1, klubber[klubb]).write()
    
dump("Asker")
dump("Bærum")
dump("Try")
fossum = klubber["Fossum"]
Page("Fossum", 1, fossum[:24]).write()
Page("Fossum", 2, fossum[24:48]).write()
Page("Rest", 1, [fossum[48]] + empty*2 + empty_line + klubber["Gjerdrum"] + empty*2).write()

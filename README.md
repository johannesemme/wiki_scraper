## Formål

Indhent en række wikipedia-artikler for forskellige udvalgte wikipedia-kategorier. Herefter dumpe data i S3.

Denne data kan efterfølgende bruges til bl.a. 
- at træne en kategori-model, som kan kategorisere en tekst mht. de udvalgte kategorier.
- at lave egen søgbar database
- at træne mini language model

## Indhent wikipediaartikler og deres kategorier

Wikipedias artikler er inddelt i forskellige kategorier, som kan findes her:

https://da.wikipedia.org/wiki/Wikipedia:Kategorier.

Systemet er hierarkisk opbygget i en lidt "kringlet" træ-struktur. Kategorier såsom Historie, Sundhed, Geografi m.fl. udgør topniveau-kategorier (https://da.wikipedia.org/wiki/Kategori:Topniveau_for_emner) og har hver en hel del underkategorier, der videre har en del underkategorier osv. Disse forgreninger af underkategorier kan sagtens være beslægtede - f.eks. hører Wikipedia artiklen "Arbejdsindsats" både ind under kategorierne Sundhed samt Erhvervsliv.

Kategorisystemet muliggør, at man kan indhente de Wikipedia-artikler, der hører ind under specifikke kategorier. Oplagt er det at indhente artikler, der hører ind under hver topniveau-kategori. For dette projekt (repo) er følgende tolv "hovedkategorier" udvalgt:

UDANNELSE
SAMFUND
VIDENSKAB
NATUR (KLIMA & MILJØ)
TEKNOLOGI
KULTUR (MUSIK, TEATER, KUNST)
HISTORIE
SUNDHED
GEOGRAFI
ØKONOMI
SPORT
RELIGION
POLITIK
ERHVERVSLIV

### Hvorfor ikke bruge wikipedia XLM dump, DB pedia eller Wikipedia API?

1. God øvelse at lave egen scraper
2. Det kan hurtigt blive komplekst og ressource-krævende at arbejde med XLM-dump pga. den store datastørrelse
3. Ved eget scrape kan vi sikre nyeste data

## Setup

Kør følgende kommando for at:
- lave conda miljø
- installere requirements
- installere ipykernel (for at arbejde med jupyter notebooks)
- lave data folder

```bash
make setup
```

## Indhent url'er

Navigér til wikipedia scrapy projekt-mappen (cd Wikipedia). Vælg den dybde du vil bruge. Default: 3.

```bash
python collect_wiki_urls.py --depth 3
```

I dette script indhentes først url'erme for hver af de tolv hovedkategorier. Eksempel: For Uddannelse: "https://da.wikipedia.org/wiki/Kategori:Uddannelse", gemmes url'er først for de tilhørende Wikipedia-artikler (fx er det bl.a. artikler såsom Almendannelse, Elev, og Studiekort). Efterfølgende forfølges hvert link til underkategori-siderne, hvor de tilsvarende artiklers url'er ligeledes gemmes osv. 


## Scrape wikipedia artikler

Fra scrapy-projekt mappen "wikipedia"

```bash
scrapy crawl wiki -a depth=3
```
## Rense artikel-data og upload til cloud storage (S3)

Sørg for at have aws api installeret.
+ have lavet S3 bucket...

```bash
python process_and_store.py --depth 3
```


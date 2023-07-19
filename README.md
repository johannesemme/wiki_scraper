## Formål

Indhent en række wikipedia-artikler for forskellige udvalgte wikipedia-kategorier. Herefter dumpe data i S3.

Denne data kan efterfølgende bruges til bl.a. 
- at træne en kategori-model, som kan kategorisere en tekst mht. de udvalgte kategorier.
- at lave egen søgbar minidatabase
- at træne mini language model

## Indhent wikipediaartikler og deres kategorier

Wikipedias artikler er inddelt i forskellige kategorier, som kan findes her:

https://da.wikipedia.org/wiki/Wikipedia:Kategorier.

Systemet er hierarkisk opbygget i en lidt "kringlet" træ-struktur. Kategorier såsom Historie, Sundhed, Geografi m.fl. udgør topniveau-kategorier (https://da.wikipedia.org/wiki/Kategori:Topniveau_for_emner) og har hver en hel del underkategorier, der videre har en del underkategorier osv. Disse forgreninger af underkategorier kan sagtens være beslægtede - f.eks. hører Wikipedia artiklen "Arbejdsindsats" både ind under kategorierne Sundhed samt Erhvervsliv.

Kategorisystemet muliggør, at man kan indhente de Wikipedia-artikler, der hører ind under specifikke kategorier. Oplagt er det at indhente artikler, der hører ind under hver topniveau-kategori. For dette projekt (repo) er følgende tolv "hovedkategorier" udvalgt:

1. UDANNELSE
2. SAMFUND
3. VIDENSKAB
4. NATUR (KLIMA & MILJØ)
5. TEKNOLOGI
6. KULTUR (MUSIK, TEATER, KUNST)
7. HISTORIE
8. SUNDHED
9. GEOGRAFI
10. BIOLOGI
11. ØKONOMI
12. SPORT
13. RELIGION
14. POLITIK
15. UNDERHOLDNING



### Hvorfor ikke bruge wikipedia XLM dump, DB pedia eller Wikipedia API?

1. God øvelse at lave egen scraper
2. Det kan hurtigt blive komplekst og ressource-krævende at arbejde med XLM-dump pga. den store datastørrelse
3. Ved eget scrape kan vi sikre nyeste data

## Setup

Lav conda miljø og aktivér det

```bash
make conda_env
```

```bash
conda activate wiki_scraper
```
Kør følgende kommando for at:
- Installere requirements
- Installere ipykernel (for at arbejde med jupyter notebooks)
- Oprette data folder

```bash
make setup
```

## Indhent url'er

Vælg den dybde du vil bruge. Default is 3 for all scripts.

```bash
python collect_wiki_urls.py --depth 1
```

I dette script indhentes først url'erme for hver af de tolv hovedkategorier. Eksempel: For Uddannelse: "https://da.wikipedia.org/wiki/Kategori:Uddannelse", gemmes url'er først for de tilhørende Wikipedia-artikler (fx er det bl.a. artikler såsom Almendannelse, Elev, og Studiekort). Efterfølgende forfølges hvert link til underkategori-siderne, hvor de tilsvarende artiklers url'er ligeledes gemmes osv. 


## Scrape wikipedia artikler

Fra scrapy-projekt mappen "wikipedia" kør:

```bash
scrapy crawl wiki -a depth=1
```
## Rense artikel-data (html->text)

For at "rense" html'en og kun få den ønskede tekst ud køres følgende sript:

```bash
python process.py --depth 1
```

## Upload data til s3

Til sidst uploades data til S3 bucket:

```bash
python push_to_cloud.py --input_file 'wiki_depth_1.parquet' --bucket_name hanse-scrape-data --s3_folder wikipedia-categories
```


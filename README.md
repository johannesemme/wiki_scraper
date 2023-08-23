# Formål

Indhent en række wikipedia-artikler for forskellige udvalgte wikipedia-kategorier. Herefter dumpe data i S3.

Denne data kan efterfølgende bruges til bl.a. 
- at træne en kategori-model, som kan kategorisere en tekst mht. de udvalgte kategorier.
- at lave egen søgbar minidatabase
- at træne mini language model

# Indhent wikipediaartikler og deres kategorier

Wikipedias artikler er inddelt i forskellige kategorier, som kan findes her:

https://da.wikipedia.org/wiki/Wikipedia:Kategorier.

Systemet er hierarkisk opbygget i en lidt "kringlet" træ-struktur. Kategorier såsom Historie, Sundhed, Geografi m.fl. udgør topniveau-kategorier (https://da.wikipedia.org/wiki/Kategori:Topniveau_for_emner) og har hver en hel del underkategorier, der videre har en del underkategorier osv. Disse forgreninger af underkategorier kan sagtens være beslægtede - f.eks. hører Wikipedia artiklen "Arbejdsindsats" både ind under kategorierne Sundhed samt Erhvervsliv.

Kategorisystemet muliggør, at man kan indhente de Wikipedia-artikler, der hører ind under specifikke "hovedkategorier" (fx topniveau-kaetgorier og/eller selvvalgte udgangspunkter). Oplagt er det at indhente artikler, der hører ind under hver topniveau-kategori. For dette projekt er følgende tolv "hovedkategorier" udvalgt:

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

## Hvorfor ikke bruge wikipedia XLM dump, DB pedia eller Wikipedia API?

1. God øvelse at lave egen scraper
2. Det kan hurtigt blive komplekst og ressource-krævende at arbejde med XLM-dump pga. den store datastørrelse
3. Ved eget scrape kan vi sikre nyeste data

# Setup

Lav conda miljø og aktivér det

```bash
make conda_env
```

```bash
conda activate wiki_scraper
```

Kør følgende kommando for at installere requirements og oprette data folder

```bash
make setup
```

# Scrape

For at scrape wikipedia artikler er det valgt at gøre dette i to omgange. Dette skyldes:
1. Nemmere at lave og teste "små kodedele" for sig
2. Beautifulsoup kan bruges nemt til at indhente url'er, mens scrapy kan indstilles til polite+effektivt scrape.

## Indhent url'er

Vælg den dybde du vil bruge. Default er 3 for all scripts.

```bash
python collect_wiki_urls.py --depth 1
```

I dette script indhentes først url'erme for hver af de tolv hovedkategorier. Eksempel: For Uddannelse: "https://da.wikipedia.org/wiki/Kategori:Uddannelse", gemmes url'er først for de tilhørende Wikipedia-artikler (fx er det bl.a. artikler såsom Almendannelse, Elev, og Studiekort). Efterfølgende forfølges hvert link til underkategori-siderne, hvor de tilsvarende artiklers url'er ligeledes gemmes osv.
Url'erne gemmes i JSON format.  


## Scrape wikipedia artikler

Ved brug af scrapy indhentes den html for url: 

```bash
scrapy crawl wiki -a depth=1
```

## Upload data til s3

Til sidst gemmes data i parquet for mat og uploades til S3 bucket. Sørg for at have opsat aws credentials. 

```bash
python push_to_cloud.py --depth 1 --bucket_name hanse-scrape-data --s3_folder wikipedia-categories
```
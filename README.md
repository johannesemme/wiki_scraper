## Formål

Indhent en række wikipedia-artikler for forskellige udvalgte wikipedia-kategorier og dump data i S3.

Denne data kan efterfølgende bruges til bl.a. at træne en model, som kan kategorisere en tekst mht. de udvalgte kategorier.

## Indhent wikipediaartikler og deres kategorier

Wikipedias artikler er inddelt i forskellige kategorier, som kan findes her:

https://da.wikipedia.org/wiki/Wikipedia:Kategorier.

Systemet er hierarkisk opbygget i en "kringlet" træ-struktur, hvor kategorier såsom Historie, Sundhed, Geografi m.fl. udgør topniveau-kategorier (https://da.wikipedia.org/wiki/Kategori:Topniveau_for_emner), som har en hel del underkategorier, der videre har en del underkategorier osv. Disse forgreninger af underkategorier kan sagtens være beslægtede - f.eks. hører Wikipedia artiklen "Arbejdsindsats" både ind under kategorierne Sundhed samt Erhvervsliv, som videre hører ind under Økonomi og Samfund.

Kategorisystemet muliggør, at man kan indhente de Wikipedia-artikler, der hører ind under specifikke kategorier - oplagt er at indhente artikler der hører ind under hver topniveau-kategori. For denne kode er følgende tolv "hovedkategorier" udvalgt:

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

### collect_wiki_urls.py

I dette script indhentes først url'erme for hver af de tolv hovedkategorier. Eksempel: For Uddannelse: "https://da.wikipedia.org/wiki/Kategori:Uddannelse", gemmes url'er først for de tilhørende Wikipedia-artikler (fx er det bl.a. artikler såsom Almendannelse, Elev, og Studiekort). Efterfølgende forfølges hvert link til underkategori-siderne, hvor de tilsvarende artiklers url'er ligeledes gemmes osv. 


### scraping


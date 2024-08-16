Na inštaláciu je potrebné nainštalovanie Python virtuálneho prostredia a v ňom balíčky:

pip install requests
pip install tornado
pip install polyline
pip install psycopg2
pip install peewee
pip install jinja2
pip install matplotlib

Po inštalácii všetkých potrebných balíčkov je potrebné pre správne fungovanie aplikácie vykonať nasledovné kroky:

Premenujte súbor config.temp.py na config.py.
Otvorte súbor config.py a nahraďte preddefinované texty (napr. "your\_db\_host", "your\_db\_name") skutočnými hodnotami, ktoré zodpovedajú vašim konfiguračným nastaveniam, ako sú údaje pre pripojenie k databáze, OAuth2 nastavenia pre Google a podobne.
Tieto kroky sú nevyhnutné pre správne fungovanie aplikácie a zabezpečenie prístupu k externým službám a databázam.
    V prípade testovania výkonu aplikácie je potrebné zmeniť názov súboru handlers.py na nejaký iný a súbor handlersForTests.py premenovať na handlers.py.

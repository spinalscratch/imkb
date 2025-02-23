from rdflib import Graph, Namespace

# Carica il file TTL
g = Graph()
g.parse("music_knowledge_base.ttl", format="turtle")

# Definisci i namespace
IMKB = Namespace("http://example.org/imkb/")
WD = Namespace("http://www.wikidata.org/entity/")

# Query 1: Verifica le playlist e le canzoni associate
query_playlists = """
PREFIX imkb: <http://example.org/imkb/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?playlistName ?songTitle
WHERE {
    ?playlist a imkb:Playlist ;
              imkb:hasName ?playlistName ;
              imkb:contains ?song .
    ?song imkb:hasTitle ?songTitle .
}
"""

# Query 2: Verifica gli artisti e i collegamenti a Wikidata
query_artists = """
PREFIX imkb: <http://example.org/imkb/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?artistName ?wikidataURI
WHERE {
    ?artist a imkb:Artist ;
            imkb:hasName ?artistName ;
            imkb:linkedTo ?wikidataURI .
}
"""

# Query 3: Verifica le canzoni senza collegamenti a Wikidata
query_songs_without_wikidata = """
PREFIX imkb: <http://example.org/imkb/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?songTitle ?artistName
WHERE {
    ?song a imkb:Song ;
          imkb:hasTitle ?songTitle ;
          imkb:hasArtist ?artist .
    ?artist imkb:hasName ?artistName .
    FILTER NOT EXISTS { ?artist imkb:linkedTo ?wikidataURI }
}
"""

# Esegui le query e stampa i risultati
def run_query(graph, query, description):
    print(f"\n{description}\n{'=' * len(description)}")
    results = graph.query(query)
    for row in results:
        print(row)

# Esegui le query
run_query(g, query_playlists, "Playlist e canzoni associate")
run_query(g, query_artists, "Artisti con collegamenti a Wikidata")
run_query(g, query_songs_without_wikidata, "Canzoni senza collegamenti a Wikidata")

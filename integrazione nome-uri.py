import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from fuzzywuzzy import fuzz
import time
import os  # Importante per la gestione del file


def wikidata_search(artist_name):
    """
    Cerca un artista su Wikidata e restituisce l'URI dell'entità.
    Ottimizzato per evitare timeout e gestisce il caso in cui artistLabel non è presente.
    """
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)

    def run_query(query):
        sparql.setQuery(query)
        try:
            results = sparql.query().convert()
            return results["results"]["bindings"]
        except Exception as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return []

    # --- Fase 1: Ricerca Diretta (Ottimizzata) ---
    query_direct = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?artist ?artistLabel WHERE {{
          ?artist rdfs:label "{artist_name}"@en .
          {{ ?artist wdt:P31 wd:Q5 . }}
          UNION
          {{ ?artist wdt:P31 wd:Q215380 . }}
          UNION
          {{ ?artist wdt:P31 wd:Q482994 .}}
        }}
        LIMIT 5
    """
    results_direct = run_query(query_direct)

    if results_direct:
        for result in results_direct:
            # Usa .get() per evitare KeyError
            if result.get("artistLabel") and result["artistLabel"]["value"].lower() == artist_name.lower():
                return result["artist"]["value"]
        if len(results_direct) > 0: #Controllo che la lista non sia vuota
            return results_direct[0]["artist"]["value"]


    # --- Fase 2: Fuzzy Matching (Ottimizzata) ---
    query_fuzzy = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?artist ?artistLabel WHERE {{
          ?artist rdfs:label ?artistLabel .
          ?artist wdt:P31 wd:Q5 .
          FILTER(LANG(?artistLabel) = "en")
        }}
        LIMIT 100
    """
    results_fuzzy = run_query(query_fuzzy)

    best_match = None
    best_score = 0

    for result in results_fuzzy:
        label = result.get("artistLabel", {}).get("value") # Usa .get() anche qui
        if label:  # Controlla che label non sia None
            score = fuzz.ratio(artist_name.lower(), label.lower())
            if score > best_score:
                best_score = score
                best_match = result["artist"]["value"]

    if best_score >= 80:
        return best_match
    else:
        return None



def process_playlist_file_in_batches(filepath, output_filepath, batch_size=100):
    """
    Legge il file, estrae artisti/titoli, cerca su Wikidata, gestisce batch, e salva l'output.
    """
    results = {}
    current_playlist = None
    batch = []

    # Controlla se il file di output esiste, altrimenti lo crea
    if not os.path.exists(output_filepath):
        open(output_filepath, 'w').close()  # Crea un file vuoto

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Playlist:"):
                current_playlist = line.replace("Playlist:", "").strip()
                results[current_playlist] = []  # Inizializza la lista per la playlist
            elif line.startswith("- Artist:"):
                parts = line.split(", Track:")
                artist_name = parts[0].replace("- Artist:", "").strip()
                track_name = parts[1].strip() if len(parts) > 1 else "Titolo Sconosciuto"
                batch.append((current_playlist, artist_name, track_name))

                if len(batch) >= batch_size:
                    process_batch(batch, results, output_filepath)
                    batch = []
                    time.sleep(5)

        if batch:  # Ultimo batch
            process_batch(batch, results, output_filepath)

    return results



def process_batch(batch, results, output_filepath):
    """
    Elabora un batch e scrive l'output sul file.
    """
    with open(output_filepath, 'a', encoding='utf-8') as outfile:  # 'a' per append
        for playlist, artist_name, track_name in batch:
            wikidata_uri = wikidata_search(artist_name)
            #results[playlist].append((artist_name, track_name, wikidata_uri)) #Non serve più perchè scriviamo sul file
            if wikidata_uri:
                output_line = f"Playlist: {playlist} -- {artist_name} -- {track_name} --> {wikidata_uri}\n"
            else:
                output_line = f"Playlist: {playlist} -- {artist_name} -- {track_name} --> NON TROVATO\n"
            outfile.write(output_line)
            print(output_line.strip())  # Stampa anche a schermo per il monitoraggio



# --- Esempio di utilizzo ---
file_path = "playlists.txt"
output_file_path = "result.txt"  # Specifica il file di output
playlist_data = process_playlist_file_in_batches(file_path, output_file_path, batch_size=100)

print(f"I risultati sono stati salvati in {output_file_path}")

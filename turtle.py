import re

def slugify(text):
    """Normalizza il testo per gli URI"""
    text = re.sub(r'[^\w\s-]', '', text.strip().lower())
    return re.sub(r'[-\s]+', '_', text)

# Funzione per generare URI unici
def generate_uri(entity_type, name):
    return f"imkb:{entity_type}_{slugify(name)}"

# Lista per memorizzare le triple
triples = []

# Apri il file result.txt e leggi i dati
with open('result.txt', 'r', encoding='utf-8') as file:
    data = file.readlines()

# Processamento dei dati
for line in data:
    line = line.strip()
    if not line:
        continue

    # Estrazione dati
    if " --> " in line:
        parts = line.split(" -- ")
        if len(parts) < 3:
            continue

        # Pulizia dei dati e rimozione virgolette
        playlist = parts[0].replace('Playlist: ', '').strip().replace('"', '')
        artist = parts[1].strip().replace('"', '')
        song_info = parts[2].split(" --> ")
        song = song_info[0].strip().replace('"', '')
        wikidata_uri = song_info[1].strip() if len(song_info) > 1 else None

        # Generazione URI
        playlist_uri = generate_uri("Playlist", playlist)
        artist_uri = generate_uri("Artist", artist)
        song_uri = generate_uri("Song", f"{artist}_{song}")

        # Aggiunta triple
        triples.append(f"{playlist_uri} a imkb:Playlist ;")
        triples.append(f'    imkb:hasName "{playlist}" .')

        triples.append(f"{song_uri} a imkb:Song ;")
        triples.append(f'    imkb:hasTitle "{song}" ;')
        triples.append(f'    imkb:hasArtist {artist_uri} .')

        triples.append(f"{artist_uri} a imkb:Artist ;")
        triples.append(f'    imkb:hasName "{artist}"' +
                      (f' ;\n    imkb:linkedTo <{wikidata_uri}> .' if wikidata_uri and wikidata_uri != 'NON TROVATO' else ' .'))

        triples.append(f"{playlist_uri} imkb:contains {song_uri} .")

# Salvataggio su file
with open('music_knowledge_base.ttl', 'w', encoding='utf-8') as f:
    f.write("@prefix imkb: <http://example.org/imkb/> .\n")
    f.write("@prefix wd: <http://www.wikidata.org/entity/> .\n")
    f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
    f.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
    f.write("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n")
    f.write("\n".join(triples))

print("Knowledge Base generata correttamente! File salvato come music_knowledge_base.ttl")

import json

# Open the output file in write mode with UTF-8 encoding
with open('output.txt', 'a', encoding='utf-8') as outfile:
    # Load the JSON data from the file
    with open('mpd.slice.999000-999999.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Iterate through the playlists
    for playlist in data['playlists']:
        outfile.write(f"Playlist: {playlist['name']}\n")

        # Iterate through the tracks in the playlist
        for track in playlist['tracks']:
            outfile.write(f"  - Artist: {track['artist_name']}, Track: {track['track_name']}\n")

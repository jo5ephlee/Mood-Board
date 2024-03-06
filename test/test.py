import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="e61f1cd7477d4d5ab7f71030ec3ef84e",
                                               client_secret="07ee27fc98504cde955e1da133ae69fc",
                                               redirect_uri="https://localhost:8080/",
                                               scope="user-library-read"))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])
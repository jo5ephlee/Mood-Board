from __future__ import print_function
import spotipy
import json
import time
import sys
from spotipy.oauth2 import SpotifyOAuth
# using eddys 'test' app credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="e61f1cd7477d4d5ab7f71030ec3ef84e",
                                               client_secret="07ee27fc98504cde955e1da133ae69fc",
                                               redirect_uri="https://localhost:8080/",
                                               scope="user-library-read"))

sp.trace = False

if len(sys.argv) > 1:
    artist_name = ' '.join(sys.argv[1:])
else:
    artist_name = 'weezer'

results = sp.search(q=artist_name, limit=3)
tids = []
for i, t in enumerate(results['tracks']['items']):
    print(' ', i, t['name'])
    tids.append(t['uri'])

start = time.time()
features = sp.audio_features(tids)
delta = time.time() - start
for feature in features:
    print(json.dumps(feature, indent=4))
    print()
    analysis = sp._get(feature['analysis_url'])
    print(json.dumps(analysis, indent=4))
    print()
print("features retrieved in %.2f seconds" % (delta,))
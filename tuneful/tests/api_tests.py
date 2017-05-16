import unittest
import os
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Python 2 compatibility

# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the posts API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)
        
    def test_get_empty_songs(self):
        """ Getting songs from an empty database """
        response = self.client.get("/api/songs", headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data, [])
        
    def test_get_songs(self):
        """ Getting songs from a populated database """
        file1 = models.File(name= "song1")
        file2 = models.File(name= "song2")
        
        session.add_all([file1, file2])
        session.commit()
        
        song1 = models.Song(song_file_id = file1.id)
        song2 = models.Song(song_file_id = file2.id)
        

        session.add_all([song1, song2])
        session.commit()
        
        response = self.client.get("/api/songs", headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(data), 2)
        
        song1 = data[0]
        self.assertEqual(song1["file"]["name"], "song1")

        song2 = data[1]
        self.assertEqual(song2["file"]["name"], "song2")
        
    def test_post_song(self):
        """ Posting a new song """
        file = models.File(name= "song1")
        
        session.add(file)
        session.commit()

        data = {
            "file": {
            "id": file.id
                }
        }

        response = self.client.post("/api/songs",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
                         "/api/songs")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], file.id)
        self.assertEqual(data["file"]["name"], "song1")

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)

        song = songs[0]
        self.assertEqual(song.song_file_id, file.id)
        
    def test_delete_song(self):
        file = models.File(name= "song1")
        
        session.add(file)
        session.commit()

        song = models.Song(song_file_id = file.id)
        
        session.add(song)
        session.commit()

        response = self.client.delete("/api/songs/{}".format(song.id), headers=[("Accept", "application/json")])
        
        session.delete(file)
        session.commit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        posts = session.query(models.Song).all()
        self.assertEqual(len(posts), 0)
if __name__ == "__main__":
    unittest.main()

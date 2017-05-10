import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from . import app
from .database import session
from .utils import upload_path

song_schema = {
    "type": "object",
    "properties": {
        "file": {
            "type": "object",
            "properties": {
                "id": {"type": "number"}
            },
        },
    },
    "required": ["file"]
}

@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """ Get a list of songs """
    songs = session.query(models.Song).all()

    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")
    
@app.route("/api/posts", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def posts_post():
    """ Add a new post """
    data = request.json

    # Check that the JSON supplied is valid
    # If not you return a 422 Unprocessable Entity
    try:
        validate(data, song_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    # Add the post to the database
    song = models.Song(file=data["file"],)
    session.add(song)
    session.commit()

    # Return a 201 Created, containing the post as JSON and with the
    # Location header set to the location of the post
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("get_songs")}
    return Response(data, 201, headers=headers,
                    mimetype="application/json")
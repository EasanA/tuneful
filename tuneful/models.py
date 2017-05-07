import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from .database import Base, engine

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    
    file = relationship("File", uselist=False, backref="song")
    def as_dictionary(self):
        song = {
            "id": self.id,
            "file" : {
                "id": "",
                "name" :  ""  
            }
        }
        return song
        
class File(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    
    song_id = Column(Integer, ForeignKey('song.id'))
    song = relationship("Song", backref="file")
     
    def as_dictionary(self):
        file = {
            "id": self.id,
            "name" :  self.name 
            }
        return file
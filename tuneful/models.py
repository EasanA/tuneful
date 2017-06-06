import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from .database import Base, engine, session

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    
    song_file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    
    def as_dictionary(self):
        song_file_info = session.query(File).filter_by(id=self.song_file_id).first()
        song = {
            "id": self.id,
            "file" : {
                "id" : song_file_info.id,
                "name" : song_file_info.name
            }
        }
        return song
        
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    
    song = relationship("Song", uselist=False, backref="song")
     
    def as_dictionary(self):
        file = {
            "id": self.id,
            "name" :  self.name,
            "path": url_for("uploaded_file", filename=self.name)
            }
        return file
        
Base.metadata.create_all(engine)
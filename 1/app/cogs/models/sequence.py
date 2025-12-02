from typing import List
from pydantic import BaseModel, Field

class SequenceItemNote(BaseModel):
  pitch: str = Field(..., description="Musical pitch identifier")
  octave: int = Field(..., description="Octave")

class SequenceItem(BaseModel):
  br: bool = Field(False, description="Should line break after this note")
  notes: List[SequenceItemNote] = Field(..., description="List of notes in this sequence item")

class Sequence(BaseModel):
  items: List[SequenceItem] = Field(..., description="Note sequence as an ordered list of sequence items")

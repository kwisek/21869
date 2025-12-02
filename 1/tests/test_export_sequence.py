import unittest
from app.cogs.models import Sequence, SequenceItem, SequenceItemNote
from app.cogs.export.export import _sequence_to_str

class TestSequenceToStr(unittest.TestCase):
    
  def test_single_note_no_break(self):
    seq = Sequence(items=[
      SequenceItem(notes=[SequenceItemNote(pitch="C", octave=4)], br=False)
    ])
    self.assertEqual(_sequence_to_str(seq, "STANDARD"), "C4")

  def test_two_notes_without_break(self):
    seq = Sequence(items=[
      SequenceItem(notes=[SequenceItemNote(pitch="C", octave=4)], br=True),
      SequenceItem(notes=[SequenceItemNote(pitch="C", octave=5)], br=False),
    ])
    self.assertEqual(_sequence_to_str(seq, "STANDARD"), "C4\n C5")

  def test_multi_note_group(self):
    seq = Sequence(items=[
      SequenceItem(notes=[SequenceItemNote(pitch="C", octave=4), SequenceItemNote(pitch="D", octave=4), SequenceItemNote(pitch="E", octave=4)], br=False)
    ])
    self.assertEqual(_sequence_to_str(seq, "STANDARD"), "(C4 D4 E4)")

  def test_multi_items_mixed(self):
    seq = Sequence(items=[
      SequenceItem(notes=[SequenceItemNote(pitch="C", octave=4)], br=False),
      SequenceItem(notes=[SequenceItemNote(pitch="D", octave=5), SequenceItemNote(pitch="E", octave=6)], br=True),
      SequenceItem(notes=[SequenceItemNote(pitch="G", octave=5), SequenceItemNote(pitch="A", octave=5)], br=False),
    ])
    self.assertEqual(_sequence_to_str(seq, "NUMERIC"), "1 (2° 3°°)\n (5° 6°)")

if __name__ == "__main__":
  unittest.main()
import unittest
from app.cogs.export.export import _sequence_item_note_to_str
from app.cogs.models import SequenceItemNote

class TestSequenceItemNoteToStr(unittest.TestCase):

  # letter notation
  def test_letter_notation_matching_oct_4(self):
    note = SequenceItemNote(pitch="C", octave=4)
    self.assertEqual(_sequence_item_note_to_str(note, "LETTER"), "C")

  def test_letter_notation_matching_oct_5(self):
    note = SequenceItemNote(pitch="D", octave=5)
    self.assertEqual(_sequence_item_note_to_str(note, "LETTER"), "D°")

  def test_letter_notation_matching_oct_6(self):
    note = SequenceItemNote(pitch="E", octave=6)
    self.assertEqual(_sequence_item_note_to_str(note, "LETTER"), "E°°")

  # numeric notation
  def test_numeric_notation_matching_oct_4(self):
    note = SequenceItemNote(pitch="C", octave=4)
    self.assertEqual(_sequence_item_note_to_str(note, "NUMERIC"), "1")

  def test_numeric_notation_matching_oct_5(self):
    note = SequenceItemNote(pitch="D", octave=5)
    self.assertEqual(_sequence_item_note_to_str(note, "NUMERIC"), "2°")

  def test_numeric_notation_matching_oct_6(self):
    note = SequenceItemNote(pitch="E", octave=6)
    self.assertEqual(_sequence_item_note_to_str(note, "NUMERIC"), "3°°")

  # standard notation
  def test_standard_notation_matching_oct_4(self):
    note = SequenceItemNote(pitch="C", octave=4)
    self.assertEqual(_sequence_item_note_to_str(note, "STANDARD"), "C4")

  def test_standard_notation_matching_oct_5(self):
    note = SequenceItemNote(pitch="D", octave=5)
    self.assertEqual(_sequence_item_note_to_str(note, "STANDARD"), "D5")

  def test_standard_notation_matching_oct_6(self):
    note = SequenceItemNote(pitch="E", octave=6)
    self.assertEqual(_sequence_item_note_to_str(note, "STANDARD"), "E6")

if __name__ == '__main__':
    unittest.main()
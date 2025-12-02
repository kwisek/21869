import unittest
from gen.main import _parse_tokens_from_seq, _file_name_to_expected_result
from app.cogs.models import Sequence, SequenceItem, SequenceItemNote

class TestGenSampleHandling(unittest.TestCase):

  # typical sequence
  def test_parse_tokens_from_seq(self):
    seq = Sequence(items=[
      SequenceItem(notes=[SequenceItemNote(pitch='C', octave=4)]),
      SequenceItem(notes=[SequenceItemNote(pitch='C', octave=4), SequenceItemNote(pitch='C', octave=5), SequenceItemNote(pitch='C', octave=6)]),
      SequenceItem(notes=[SequenceItemNote(pitch='D', octave=6)])
    ])
    actual = _parse_tokens_from_seq(seq)
    self.assertEqual(actual, ['C4', '(C4 C5 C6)', 'D6'])
    
  # empty sequence
  def test_parse_tokens_from_seq_empty(self):
    seq = Sequence(items = [])
    actual = _parse_tokens_from_seq(seq)
    self.assertEqual(actual, [])
    
  # sigle item sequence
  def test_parse_tokens_from_seq_one_item(self):
    seq = Sequence(items = [
      SequenceItem(notes=[SequenceItemNote(pitch='C', octave=4)])
    ])
    actual = _parse_tokens_from_seq(seq)
    self.assertEqual(actual, ['C4'])
    
  # single item chord sequence
  def test_parse_tokens_from_seq_one_item_chord(self):
    seq = Sequence(items = [
      SequenceItem(notes=[SequenceItemNote(pitch='C', octave=4), SequenceItemNote(pitch='A', octave=5)])
    ])
    actual = _parse_tokens_from_seq(seq)
    self.assertEqual(actual, ['(C4 A5)'])
  
  # file names
  def test_file_name_to_expected_result_sample_singular(self):
    file_name = "A5_087.wav"
    actual = _file_name_to_expected_result(file_name)
    self.assertEqual(actual, 'A5')
    
  def test_file_name_to_expected_result_sample_chord(self):
    file_name = "A5_B5_003.wav"
    actual = _file_name_to_expected_result(file_name)
    self.assertEqual(actual, '(A5 B5)')
    
  def test_file_name_to_expected_result_sample_silence(self):
    file_name = "SILENCE_072.wav"
    actual = _file_name_to_expected_result(file_name)
    self.assertEqual(actual, '')
    
  def test_file_name_to_expected_result_sequence(self):
    file_name = "007_G4_G5__B4__D5__B4.wav"
    actual = _file_name_to_expected_result(file_name)
    self.assertEqual(actual, '(G4 G5) B4 D5 B4')

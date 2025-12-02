from io import BytesIO
from app.cogs.models.sequence import Sequence, SequenceItemNote
from app.cogs.utils.const import NOTATION_LETTERS, NOTATION_NUMBERS
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4

def _sequence_item_note_to_str(note: SequenceItemNote, notation: str) -> str:
  key = f"{note.pitch}{note.octave}"
  return (NOTATION_LETTERS if notation == "LETTER" 
    else NOTATION_NUMBERS if notation == "NUMERIC" 
    else {}).get(key, key)

def _sequence_to_str(sequence: Sequence, notation: str) -> str:
  return " ".join(
    (_sequence_item_note_to_str(item.notes[0], notation) if len(item.notes) == 1 
    else f"({' '.join(_sequence_item_note_to_str(n, notation) for n in item.notes)})")
    + ("\n" if item.br else "")
    for item in sequence.items)

def export_to_image(sequence: Sequence, notation: str) -> BytesIO:
  text = _sequence_to_str(sequence, notation)

  try:
    font = ImageFont.truetype("arial.ttf", size=40)
  except:
    font = ImageFont.load_default()

  padding = 20
  dummy_img = Image.new("RGB", (1, 1))
  dummy_draw = ImageDraw.Draw(dummy_img)
  bbox = dummy_draw.textbbox((0, 0), text, font=font)
  text_width = bbox[2] - bbox[0]
  text_height = bbox[3] - bbox[1]
  img_width = text_width + padding
  img_height = text_height + padding
  img = Image.new("RGB", (img_width, img_height), "white")
  draw = ImageDraw.Draw(img)
  draw.text((padding // 2, padding // 2), text, fill="black", font=font)
  buf = BytesIO()
  img.save(buf, format="PNG")
  buf.seek(0)
  return buf

def export_to_pdf(sequence: Sequence, notation: str) -> BytesIO:
  text = _sequence_to_str(sequence, notation)
  font_name = "Helvetica"
  font_size = 20
  padding = 20 * mm
  line_spacing = font_size * 1.4
  page_width, page_height = A4
  max_width = page_width - 2 * padding
  words = text.split(' ')
  lines = []
  line = ""
  br = False

  for word in words:
    if pdfmetrics.stringWidth(f"{line} {word}", font_name, font_size) <= max_width and br == False:
      line = f"{line} {word.strip()}"
    else:
      lines.append(line)
      line = word
    br = word.endswith('\n')
  if line:
    lines.append(line)

  buf = BytesIO()
  c = canvas.Canvas(buf, pagesize=A4)
  c.setFont(font_name, font_size)

  y = page_height - padding
  for l in lines:
    c.drawString(padding, y, l)
    y -= line_spacing
    if y < padding:
      c.showPage()
      c.setFont(font_name, font_size)
      y = page_height - padding

  c.save()
  buf.seek(0)
  return buf
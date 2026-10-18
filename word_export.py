"""Editable Word exports using a robust single-column layout."""
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from forms import materialize
from photos import cropped
from pdf_export import settings,LABELS

def make_docx(s,a,path,kind='cv'):
 if kind not in ('cv','letter','cover'):raise ValueError('Für Word bitte Lebenslauf, Anschreiben oder Deckblatt wählen.')
 p=s['profile'];materialize(p,a);doc=Document();section=doc.sections[0];section.page_width=Cm(21);section.page_height=Cm(29.7);section.top_margin=Cm(1.8);section.bottom_margin=Cm(1.8);section.left_margin=Cm(1.8);section.right_margin=Cm(1.8)
 normal=doc.styles['Normal'];normal.font.name='DejaVu Sans';normal.font.size=Pt(a['design']['size']);normal.paragraph_format.space_after=Pt(7);normal.paragraph_format.line_spacing=1.15
 for key,size in [('Title',24),('Heading 1',12),('Heading 2',11)]:
  style=doc.styles[key];style.font.name='DejaVu Sans';style.font.size=Pt(size);style.font.color.rgb=RGBColor.from_string('000000');style.paragraph_format.space_before=Pt(12);style.paragraph_format.space_after=Pt(7)
 doc.core_properties.author=p['name'];doc.core_properties.title={'cv':'Lebenslauf','letter':'Anschreiben','cover':'Bewerbung'}[kind]+' '+p['name'];doc.core_properties.subject=a['position'];doc.core_properties.comments='';doc.core_properties.last_modified_by=p['name']
 def add(text,style=None):
  if text.strip():return doc.add_paragraph(text,style)
 def head(with_photo=False):
  if with_photo and p.get('photo') and a['design']['photo']:doc.add_picture(cropped(p),width=Cm(3.1))
  add(p['name'] or 'Dein Name','Title')
  add(' · '.join(filter(None,[p['email'],p['phone']]))+'\n'+p['address'])
 if kind=='letter':
  head();add(a['recipient'] or a['company']);add(', '.join(filter(None,[a['location'],a['date']])));add('Bewerbung als '+a['position'],'Heading 1');add(a['salutation'])
  for block in a['letter'].split('\n\n'):add(block)
  add('Mit freundlichen Grüßen\n\n'+p['name'])
 elif kind=='cover':
  add('Bewerbung','Title');add(a['position'],'Heading 1');add(a['company']);head(True)
 else:
  head(True);add(p['title'])
  for key in a['design']['order']:
   value=p.get(key,'').strip()
   if not value:continue
   add(LABELS[key],'Heading 1')
   for block in value.split('\n\n'):
    if key in ('experience','education'):
     lines=block.split('\n');par=add(lines[0]);par.runs[0].bold=True;par.paragraph_format.keep_with_next=len(lines)>1
     if len(lines)>1:add('\n'.join(lines[1:]))
    else:add(block)
 doc.save(path)

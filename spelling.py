import ctypes,ctypes.util,re
from functools import lru_cache
class Speller:
 def __init__(self):
  self.lib=ctypes.CDLL(ctypes.util.find_library('hunspell-1.7') or 'libhunspell-1.7.so.0');l=self.lib
  l.Hunspell_create.argtypes=[ctypes.c_char_p,ctypes.c_char_p];l.Hunspell_create.restype=ctypes.c_void_p
  l.Hunspell_get_dic_encoding.argtypes=[ctypes.c_void_p];l.Hunspell_get_dic_encoding.restype=ctypes.c_char_p
  l.Hunspell_spell.argtypes=[ctypes.c_void_p,ctypes.c_char_p];l.Hunspell_spell.restype=ctypes.c_int
  l.Hunspell_suggest.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p)),ctypes.c_char_p];l.Hunspell_suggest.restype=ctypes.c_int
  l.Hunspell_free_list.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p)),ctypes.c_int]
  self.handle=l.Hunspell_create(b'/usr/share/hunspell/de_DE.aff',b'/usr/share/hunspell/de_DE.dic')
  if not self.handle:raise ValueError('Deutsches Wörterbuch fehlt. Bitte hunspell-de-de installieren.')
  self.encoding=l.Hunspell_get_dic_encoding(self.handle).decode()
 @lru_cache(maxsize=6000)
 def word(self,w):
  try:b=w.encode(self.encoding)
  except UnicodeEncodeError:return None
  if self.lib.Hunspell_spell(self.handle,b):return None
  suggestions=ctypes.POINTER(ctypes.c_char_p)();n=self.lib.Hunspell_suggest(self.handle,ctypes.byref(suggestions),b)
  result=[suggestions[i].decode(self.encoding,errors='replace') for i in range(min(n,5))]
  self.lib.Hunspell_free_list(self.handle,ctypes.byref(suggestions),n);return result
 def check(self,text,ignore=()):
  ignored={w.casefold() for w in ignore};found=[];seen=set()
  text=re.sub(r'\S+@\S+|https?://\S+','',text)
  for match in re.finditer(r'[^\W\d_]+(?:[-’\'][^\W\d_]+)*',text,re.UNICODE):
   w=match.group()
   if len(w)<2 or w in seen or w.casefold() in ignored:continue
   seen.add(w);suggestions=self.word(w)
   if suggestions is not None:found.append({'word':w,'suggestions':suggestions})
   if len(found)>=18:break
  return found

#!/usr/bin/python3
import os,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
os.environ['RESTLOS_BASE_DIR']=str(BASE)
from updates import choose_launch
root=choose_launch()
os.environ['LD_LIBRARY_PATH']=str(root/'native')+(':'+os.environ['LD_LIBRARY_PATH'] if os.environ.get('LD_LIBRARY_PATH') else '')
os.execv(sys.executable,[sys.executable,str(root/'app.py'),*sys.argv[1:]])

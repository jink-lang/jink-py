import sys 
from cx_Freeze import setup, Executable
import os

build_exe_options = { "include_msvcr": True }
cwd = os.getcwd()
base=None
if sys.platform == "win32":
  base = "Console"

setup(
  name="jink",
  version="0.0.2",
  description="A strongly typed, JavaScript-like programming language.",
  options={ "build_exe": build_exe_options },
  executables=[Executable("jink.py", base=base, icon=f"{cwd}\\jink.ico")]
)

from distutils.core import setup
import py2exe

#setup(console=['process_max.py'])

setup(console=['image_processing_tool.py'],
    options = {
        "py2exe": {
            "dll_excludes": ["MSVCP90.dll"]
            }
    },
)
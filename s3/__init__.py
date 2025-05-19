# pylint: skip-file
# type: ignore

import sys
sys.path.insert(0, f'./s3/s3-web-browser')
print(sys.path)
from s3_web_browser import create_app

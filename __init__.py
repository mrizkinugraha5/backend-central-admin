import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from app_name import app
from app_name.config import PORT

# run server
if __name__ == '__main__':
	app.run(port=PORT, debug=True)

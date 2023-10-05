import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from app_name import app
from app_name import config

# setting cors
"""
	Apa itu CORS ?
	- CORS kependekan dari Cross-Origin-Resource-Sharing
	- dengan CORS memungkinkan kita untuk mengatur siapa saja (aplikasi luar) yang boleh mengakses aplikasi flask ini
	- memungkinkan juga mengatur secara spesifik routing apa saja yang boleh diakses oleh pihak ke-3 (private api service)
	panduan : https://www.youtube.com/watch?v=tPKyDM0qEB8
"""
from flask_cors import CORS
cors = CORS (
	app, 
	resources= {r"/*" : {"origins" : "*"}}
)

# log environment
print('-------------------------------------')
print(f'Menjalankan aplikasi pada port', config.PORT)
print(f'Aplikasi berjalan dengan mode', config.PRODUCT_ENVIRONMENT)
print('-------------------------------------')

# run server
if __name__ == '__main__':
	app.run(port=config.PORT, debug=True)

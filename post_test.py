import requests
url = 'http://127.0.0.1:5000/predict'
data = {
    'Area': '1200',
    'Bedrooms': '3',
    'CarParking': '1',
    'Gymnasium': '0',
    'SwimmingPool': '0',
    'Location': 'Dwarka',
    'Sector': 'Sector 6'
}
try:
    r = requests.post(url, data=data, timeout=10)
    print('HTTP', r.status_code)
    print('--- response snippet ---')
    print(r.text[:1200])
except Exception as e:
    print('Request failed:', e)

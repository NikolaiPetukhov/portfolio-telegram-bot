from django.http import response
import requests
import json
import datetime


baseUrl = r'https://www.farfetch.com/ru/plpslice/listing-api/products-facets'
params = '?view=%d&pagetype=%s&pricetype=%s&page=%d'
headers = {
    'Origin': 'https://www.farfetch.com', 
    'Referer': 'https://www.farfetch.com/shopping/m/items.aspx', 
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' \
        ' Chrome/75.0.3770.100 Safari/537.36'
    }


p = {
    "view": 180,
    "pagetype": 'Shopping',
    "pricetype": 'FullPrice',
    "page": 1,
}

def buildUrl(page=p["page"]):
    parameters = params % (
        p["view"],
        p["pagetype"],
        p["pricetype"],
        page,
    )
    return baseUrl + parameters

def get_listings(page=1):
    try:
        request = requests.get(buildUrl(page), headers=headers)
    except Exception as e:
        return {}
    response = request.json()
    return response

def get_pages():
    try:
        request = requests.get(buildUrl(1), headers=headers)
    except Exception as e:
        return {}
    data = request.json()
    response = data["listingPagination"]["totalPages"]
    return response

def print_to_file(filename, date=datetime.date.today()):
    data = get_listings()
    data["date"] = str(date)
    with open(f'{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return True

def get_item_by_url(url):
    try:
        request = requests.get(url, headers=headers)
    except:
        return {}
    response = request.json()
    return response
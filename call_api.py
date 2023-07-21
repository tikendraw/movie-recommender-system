import json    
import requests


# read a json file
with open('secret.json', 'r') as f:
    data = json.load(f)

headers = data['headers']

urls = ["https://imdb-search2.p.rapidapi.com/superman2", "https://imdb-search2.p.rapidapi.com/spiderman2", "https://imdb-search2.p.rapidapi.com/300"]


def make_url(name:str):
    x = name.lower()
    x = name.strip()
    x = x.replace(' ','%20')
    return f"https://imdb-search2.p.rapidapi.com/{x}"
    
    
def get_data(name:str, headers:dict = headers)->json:
    url = make_url(name)
    response = requests.get(url, headers=headers)
    return response.json()


if __name__=='__main__':
    
    names = ['hulk','wonder woman', 'black widow']
    
    for i in names:
        
        
        data = get_data(i, headers)
        print(data)
        print('*'*30)
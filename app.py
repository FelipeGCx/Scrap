from os import path
from bs4 import BeautifulSoup
import requests
import json


class Scrapping():
    def __init__(self):
        self.main();
        pass        
    
    def main(self):
        print("executing the scrapp...")
        url = "https://www.iban.com/country-codes"
        content = self.get_script(url)
        data = self.transform_data(content)
        self.create_file("countries.json", data)
        self.create_sql("Countries", data)
        print("scrapping finished")
        
    def transform_data(self, content):
        response = []
        tbody = content.find("tbody")
        for tr in tbody.find_all("tr"):
            country = {}
            td = tr.find_all("td")
            country["name"] = td[0].get_text()
            country["iso"] = td[2].get_text()
            af = td[1].get_text().lower()
            country["flag"] = self.get_flag(af)
            response.append(country)
        return response
        
    def get_flag(self, country):
        print("get flag from", country)
        url = f"https://flagicons.lipis.dev/flags/4x3/{country}.svg"
        # url = f"https://upload.wikimedia.org/wikipedia/commons/1/1a/Flag_of_{country}.svg"
        content = self.get_script(url)
        svg =  str(content.find("svg")).replace("\"", "'") 
        svg = svg.replace("\n","") 
        return svg
        
    
    
    def get_script(self,url):
        try:
            response = requests.get(url)
            if response.ok:
                rs = response.text
                return BeautifulSoup(rs, "lxml")
            else:
                print("some failed",response.status_code)
        except requests.exceptions.ConnectionError as exc:
                print(exc)
                return
                
    def create_sql(self, tablename, data):
        sentence = f"INSERT INTO {tablename} ({','.join(data[0].keys())}) VALUES "
        for row in data:
            values = ','.join(f'"{val}"' for val in row.values())
            sentence += f"({values}),"
        with open('countries.sql', 'w', encoding='utf8') as fh:
            fh.write(sentence)
            
    def create_file(self, filename, data):
        with open(filename, 'w', encoding='utf8') as fh:
            fh.write(json.dumps(data))
    
if __name__ == "__main__":
    app = Scrapping();
    
    

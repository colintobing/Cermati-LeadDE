import threading
import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint
import html

URL = "https://www.cermati.com/karir"

def scrape(URL):
    def clean_strong(lst):
        """
        input: list of string
        output: list of string
        """
        l_cleansed = []
        for l in lst:
            _cleansed = l.replace("\xa0", " ")
            l_cleansed.append(_cleansed)
        return l_cleansed
    
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="initials")
    results_str = str(
        results
    ).replace(
        "<script id=\"initials\" type=\"application/json\">", ""
    ).replace(
        "</script>", ""
    )
    results_json = json.loads(results_str)
    job_listing = results_json.get("smartRecruiterResult").get("all").get("content")
    
    result_list = []
    for j in job_listing:
        dept = j.get("department").get("label")
        title = j.get("name")
        for cf in j.get("customField"):
            for k,v in cf.items():
                if str(k)=="fieldId":
                    if str(v)=="COUNTRY":
                        country = cf.get("valueLabel")
        location = j.get("location").get("city") + ', ' + country
        ref_page = requests.get(j.get("ref"))
        ref_str = ref_page.text
        ref_json = json.loads(ref_str)
        sections = ref_json.get("jobAd").get("sections")
        description_ref = sections.get("jobDescription").get("text")
        description_html = html.unescape(description_ref)
        description_soup = BeautifulSoup(str(description_html))
        description_list = [x.get_text() for x in description_soup.find_all('li')]
        description = clean_strong(description_list)
        qualification_ref = sections.get("qualifications").get("text")
        qualification_html = html.unescape(qualification_ref)
        qualification_soup = BeautifulSoup(str(qualification_html))
        qualification_list = [x.get_text() for x in qualification_soup.find_all('li')]
        qualification = clean_strong(qualification_list)
        job_type = j.get("typeOfEmployment").get("label")
        postedBy = ref_json.get("creator").get("name")
        
        result = {
            "dept": dept,
            "title": title,
            "location": location,
            "description": description,
            "qualification": qualification,
            "job_type": job_type,
            "postedBy": postedBy
        }
        
        result_list.append(result)
        
    res = {}
    for item in result_list:
        result = {
            "title": item.get("title"),
            "location": item.get("location"),
            "description": item.get("description"),
            "qualification": item.get("qualification"),
            "job_type": item.get("job_type"),
            "postedBy": item.get("postedBy")
        }
        
        res.setdefault(item['dept'], []).append(result)
    
    return res

def main():
    if __name__ == "__main__":
        def run_scrape():
            with open("solution.json", "w") as outfile:
                json_object = json.dumps(scrape(URL))
                outfile.write(json_object)
        threading.Thread(target=run_scrape())

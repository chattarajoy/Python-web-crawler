import sys
import requests
from bs4 import BeautifulSoup
from urlparse import urlparse
from collections import defaultdict

# gets seed url from user
def get_seed_url():
    seed_url = raw_input("Enter link to Seed Page : ")
    # Add Protocol if not present
    if "http" not in seed_url:
        seed_url = "http://" + seed_url
    return seed_url

#returns domain name from a url
def get_domain_name(seed_url):
    parsed_url = urlparse(seed_url)
    domain_name = parsed_url.netloc
    if domain_name:
        # Remove www if present at the begining of domain name
        if domain_name.split('.')[0] == "www":
            domain_name = ".".join(domain_name.split('.')[1:])
    return domain_name

#convert every url to a standard format
def normalize_url(seed_url, seed_domain_name):
    domain_name = get_domain_name(seed_url)
    if not domain_name:
        domain_name = seed_domain_name
    normalized_url = "http://" + domain_name + urlparse(seed_url).path
    return normalized_url.strip('/')

# check if url is accessible
def validate_url_accessibility(seed_url):
    try:
        request = requests.get(seed_url)
        if request.status_code == 200:
            return 1
        else:
            return 0  # for other response codes (404, 403 etc)
    except:
        return 0      # for timeouts exception

def get_links(seed_url):
    try:
        html_page = requests.get(seed_url).text
        soup = BeautifulSoup(html_page, "html.parser")
        a_tags = soup.findAll('a')
        found_pages = []
        for link in a_tags:
            url = link.get('href')
            if url:
                normalized_url = normalize_url(url, get_domain_name(seed_url))
                found_pages.append(normalized_url)

        return found_pages
    except:
        return None

# find all accessible pages till given depth
def crawl(seed_url, max_depth, depth_dict):
    current_depth = 0
    domain_name = get_domain_name(seed_url)
    visited_pages = []
    pages_to_visit = []
    
    pages_to_visit.append((seed_url, current_depth))

    while(len(pages_to_visit) > 0):
        page_to_visit, current_depth = pages_to_visit[0]
        if page_to_visit not in visited_pages:
            if current_depth + 1 <= max_depth:
                found_pages = get_links(page_to_visit)
                if found_pages:
                    for page in found_pages:
                        if get_domain_name(page) == domain_name:
                            pages_to_visit.append((page, current_depth + 1))
            visited_pages.append(page_to_visit)
            depth_dict[str(current_depth)].append(page_to_visit)
        pages_to_visit.pop(0)

if __name__ == "__main__":

    # seed_url -> www.example.com/about
    seed_url = get_seed_url()
    # normalised seed url -> http://example.com/about
    normalized_seed_url = normalize_url(seed_url, get_domain_name(seed_url))

    print "\nPlease Wait Checking accessiblility of seed page...."

    if validate_url_accessibility(normalized_seed_url):

        print "\nGreat news! Seed URL is reachable!\n"
        max_depth = int(raw_input("Enter Max Depth : "))
        print "\nWorking.. This may take some time based on your internet connection.\nPlease be Patient!"
        # Dictionary of depth and a list of pages accessible on that depth
        depth_dict = defaultdict(list)
        # start crawling from the seed page
        crawl(normalized_seed_url, max_depth, depth_dict)
        for depth in sorted(depth_dict):
            print "\nDepth : ", depth
            print "List of accessible pages : \n"
            for page in depth_dict[depth]:
                print page
    else:
        print "\nSeed URL is unreacheable or may be invalid, can't proceed further!"

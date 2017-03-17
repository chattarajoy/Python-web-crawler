import sys
import requests
from bs4 import BeautifulSoup
from urlparse import urlparse
from collections import defaultdict

# gets seed url from user
def get_seed_url():
    # User input seed page
    seed_url = raw_input("Enter link to Seed Page : ")
    # Add Protocol if not present
    if "http" not in seed_url:
        seed_url = "http://" + seed_url
    return seed_url

#returns domain name from a url
def get_domain_name(seed_url):
    parsed_url = urlparse(seed_url)
    # get domain name from url
    domain_name = parsed_url.netloc
    if domain_name:
        # Remove www if present at the begining of domain name
        if domain_name.split('.')[0] == "www":
            domain_name = ".".join(domain_name.split('.')[1:])
    return domain_name

#convert url to a standard format
def normalize_url(seed_url, seed_domain_name):
    domain_name = get_domain_name(seed_url)
    # for links of the form :  /about.html
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

# crawk a page and find links for next level crawl
def crawl(seed_url, domain_name, current_depth, max_depth, visited_pages, depth_dict):
    if current_depth <= max_depth and validate_url_accessibility(seed_url):
        # Get the contents of the page
        html_page = requests.get(seed_url).text
        # Parse using beautiful soup
        soup = BeautifulSoup(html_page, "html.parser")
        # Get all <a> tags on page
        a_tags = soup.findAll('a')
        # list of all pages found to search in next crawl
        found_pages = []
        for link in a_tags:
            # contents in the href values has the link
            url = link.get('href')
            # convert url to a standard format
            if url: # if the href tag has some text,
                normalized_url = normalize_url(url, domain_name)
                # add unvisited pages of same website for next crawl
                if (get_domain_name(normalized_url) == domain_name) and (normalized_url not in visited_pages):
                    found_pages.append(normalized_url)
                    # mark them visited
                    visited_pages.append(normalized_url)
                    # add to resultant dictionary
                    depth_dict[str(current_depth)].append(normalized_url)
        # repeat crawl for newly found pages
        for page in found_pages:
            crawl(page, domain_name, current_depth + 1, max_depth, visited_pages, depth_dict)


if __name__ == "__main__":

    # seed_url -> www.example.com/about
    seed_url = get_seed_url()
    # domain name -> example.com
    domain_name = get_domain_name(seed_url)
    # normalised seed url -> http://example.com/about
    normalized_seed_url = normalize_url(seed_url, domain_name)

    print "\nPlease Wait Checking accessiblility of seed page...."
    # check if seed page is accessible
    if validate_url_accessibility(normalized_seed_url):

        print "\nGreat news! Seed URL is reachable!\n"
        # Max depth for the crawl
        max_depth = int(raw_input("Enter Max Depth : "))
        print "\nWorking.. This may take some time based on your internet connection.\nPlease be Patient!"
        # List of all pages visited till now
        visited_pages = [normalized_seed_url]
        # Dictionary of depth and a list of pages accessible on that depth
        depth_dict = defaultdict(list)
        depth_dict["0"] = [normalized_seed_url]
        # start crawling from the seed page, current depth is set to 1
        crawl(normalized_seed_url, domain_name, 1, max_depth, visited_pages, depth_dict)
        for depth in sorted(depth_dict):
            print "\nDepth : ", depth
            print "List of accessible pages : \n"
            for page in depth_dict[depth]:
                print page
    else:
        print "\nSeed URL is unreacheable or may be invalid, can't proceed further!"

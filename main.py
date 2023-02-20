#IMPROVEMENTS:
#Use <footer> tag as marker for last strings which are visible on web page.
#Specify not to read script.
#Use opencv and tesseract to read text from image by scroling down using Selenium scroll_by() method.
#User defined language and have a dictionary for Privacy Policy in different languages.

import json
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions;
import re 


def get_page_html_soup(url):
    """
    get_page_html_soup creates a chrome web-driver which renders url's html and return 
    all html elements of page as shown in Google Chrome Developer tools in 
    web-browser.

    :param url: Url of the target page to scrape.
    :return: bs4.BeautifulSoup object containing all html elements from url.
    """ 
    
    #Include headless argument so that driver doesn't open browser window.
    c_opts = ChromeOptions()
    c_opts.add_argument("--headless")
    chrome = Chrome(options=c_opts)
    chrome.get(url)
    html = chrome.page_source
    return BeautifulSoup(html, "html.parser")


def write_tags_to_json(tags, file):
    """
    write_tags_to_json opens a .json file in current directory and writes html elements as JSON objects.
    bs4.element.Tag.attrs dictionary is used as basis of JSON objects.
    
    :param tags: Container of bs4.element.Tag objects representing html elements.
    :param file: String for file name.
    """

    with open(file + ".json", "w") as outfile:
        for tag in tags:
            # Add additional fields to current tag's parent's Tag.attrs dictionary.
            tag.parent.attrs["html-tag-name"] = tag.parent.name

            # Add parent tag info to current tag Tag.attrs dictionary.
            tag.attrs["html-tag-string"] = tag.string
            tag.attrs["html-tag-name"] = tag.name
            tag.attrs["parent-html-tag-name"] = tag.parent.attrs

            # Convert Tag.attrs dictionary to a JSON object.
            json_obj = json.dumps(tag.attrs, indent=4)
            outfile.write(json_obj)
            outfile.write("\n")


def has_source(tag):
    """
    has_source checks whether a html element loads an external source. 
    Checks that element is not a hyperlink or link to alternative version of homepage and
    has a "src" attribute or a "href" attribute.
    
    :param tags: bs4.element.Tag object representing html element.
    """
    return ((tag.has_attr("href") and not tag.has_attr("hreflang")) or tag.has_attr("src")) and not tag.name == "a"


def get_link_id(tagString, tags):
    """
    get_link_id enumerates container of bs4.element.Tag objects and return the positional index of the 
    element that contains a given string.

    :param tags: Container of bs4.element.Tag objects representing html elements.
    :param tagString: 
    :return: Integer representing the position of tagString in tags.
    """

    for id, val in enumerate(tags):
        if(val.string == tagString):
            return id


def create_word_freq_dict(strings, endString):
    """
    create_word_freq_dict creates a frequency count of unique case-insensitive words which are
    visible in the homepage.

    :param strings: String iterator containing all strings loaded from url.
    :param endString: Last string value which is visible from home page.
    :return: Dictionary of unique strings keys up until endString and corresponding frequency values
    """

    freq = {}
    # Loop through all strings.
    for x in strings:     
        # Separate string into words.
        y = x.split()       

        # Loop through all strings.
        for z in y:  
            # Make all letters lowercase and remove punctuation.   
            z = z.lower()       
            z = re.sub(r'[^\w\s]', '', z)

            # Check whether word is a number, then don't add to freq.
            if z.isnumeric():
                continue
            
            # If word exists then increment frequency.
            # Check whether word is a number.
            if (z in freq):
                freq[z] += 1
            else:
                freq[z] = 1
        
        # Break loop if endString processed.
        if(x == endString):
            break

    return freq


def write_dict_to_json(dic, file):
    """
    write_dict_to_json converts Python dictionary into JSON objects and prints to file in current directory.

    :param strings: Python dictionary.
    :param file: String for file name.
    """

    with open(file + ".json", "w") as outfile:
        json_obj = json.dumps(dic, indent=4)
        outfile.write(json_obj)
        outfile.write("\n")


def main():
    pageURL = "https://www.cfcunderwriting.com"
    searchString = "Privacy Policy"   

    # String which marks the end of visible web-page body, all strings defined after this are not visible.                
    endString = "© 2023 CFC Underwriting Ltd"


    # Step 1
    # Read html of homepage and parse into soup using get_page_html_soup. 
    # Then parse through soup and return all tags which contain an external resource using has_source result.
    # Print filtered list of tags to json file "resources.json".
    soup = get_page_html_soup(pageURL)
    tags = soup.find_all(has_source)
    write_tags_to_json(tags, "resources")


    # Step 2
    # Use find_all("a") to return all html elements in soup which have a tag name = "a", i.e. a hyperlink.
    # Print filtered list of tags to json file "links.json".
    tags = soup.find_all("a")
    write_tags_to_json(tags, "links")


    # Step 3
    # Return id of element containing searchString = "Privacy Policy" in filtered list of tags using get_link_id.
    id = get_link_id(searchString, tags)


    # Step 4
    # Creates a new url using homepage and relative path from element found in Step 3.
    # Read html of new url into new soup using BeautifulSoup.
    url = pageURL + tags[id]["href"]
    soup = get_page_html_soup(url)

    # Select "body" tag of page to look for visible string.
    # Get string value of every html tag using stripped_strings attribute.
    tags = soup.body
    strings = tags.stripped_strings

    # Create a frequency count of each word in every string before and including the endString.
    # Print frequency count to json file using write_dict_to_json.
    freq = create_word_freq_dict(strings, endString)
    write_dict_to_json(freq, "frequency")
    print("DONE")


if __name__ == "__main__":
    main()


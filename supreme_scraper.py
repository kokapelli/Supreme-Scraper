from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as soup
debug = 0
url = "https://www.supremenewyork.com/shop"
url2 = "https://www.supremenewyork.com/shop/all"

# Site Specific
def get_page(query=""):
    client = urlopen(url + query)
    html_page = client.read() 
    client.close()

    return soup(html_page, "html.parser")

# release variable should determine whether to fetch all items or new releases
# If 1 then only return those items
# this will occur on one thread, might be slower than using many threads and skipping
def get_assortment(parsed_page, release=0):
    shop_list = parsed_page.find("ul", {"id": "shop-scroller"})
    items = []
    for i in shop_list.find_all('li'):
        items.append(i)

    return items

def get_query(item):
    return "/" + item.a['href'].split("/", 2)[2]

# Item specific
def get_item_id(query):
    return query.split("/", 2)[2]

def get_type(item):
    return "".join(item['class'])

def get_tag(item):
    if(item.span == None):
        return None
    else:
        return "".join(item.span['class'])


# Product Specific
def get_product_title(product):
    return product.find('title').text

def get_product_details(product):
    d = product.find("div", {"id": "details"})
    return d.find("p", {"itemprop": "description"}).text

def get_product_color(product):
    d = product.find("div", {"id": "details"})
    return d.find("p", {"itemprop": "model"}).text

def get_product_release_date(product):
    d = product.find("div", {"id": "details"})
    return d.h1['data-rd']

def parsed_items(items):
    item_dict = {}
    count = 0
    for i in items:
        # Aux
        print("Parsing:", count, "out of", len(items))
        count += 1

        curr_query   = get_query(i)
        curr_product = get_page(curr_query)

        curr_title   = get_product_title(curr_product)
        curr_desc    = get_product_details(curr_product)
        curr_color   = get_product_color(curr_product)
        curr_rd      = get_product_release_date(curr_product)

        curr_type    = get_type(i)
        curr_id      = get_item_id(curr_query)
        curr_tag     = get_tag(i)

        item_dict[curr_id] = [curr_title, curr_desc, curr_type, curr_color, curr_tag, curr_rd]

    return item_dict
    
# TODO
def write_items(item_dict):
    filename = "Supreme.xlsx"
    print("Writing to {filename}...")
    f = open(filename, "w")
    headers = "ID, title, desc, type, color, tag, release_date\n"

    f.write(headers)
    for key, value in item_dict.items():
        curr_row = key
        for val in value:
            if val is None:
                curr_row += ", "
            else:
                curr_row += "," + str(val.replace(",", "|").replace("\n", "|"))
                
            if val is value[-1]:
                curr_row += "\n"

        f.write(curr_row)
    
    print("Writing complete, closing file...")
    f.close()


"""
def main():
    parsed_page = get_page()
    items = get_assortment(parsed_page)

    if not debug:
        item_dict = parsed_items(items)
        write_items(item_dict)

    else:
        q   = get_query(items[0])
        p   = get_page(q)
        d   = get_product_details(p)
        c   = get_product_color(p)
        rd  = get_product_release_date(p)

        #print(d)

main()
"""
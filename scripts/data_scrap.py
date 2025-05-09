from bs4 import BeautifulSoup, NavigableString
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

def extract_product_more_details(each_product_structured_information):
    driver.get(each_product_structured_information["url"])
    time.sleep(0.1)  # Wait for the page to load
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    category = soup.find("ol").get_text(strip=True).split("/")[1]
    each_product_structured_information["category"] = category
    buttons=soup.find_all("button")
    images = []
    for button in buttons:
        if button.find("img"):
            images.append("https://shop.kimelo.com/"+button.find("img").get("src"))
    if len(images)>1:
        each_product_structured_information["other_image"]=[]
        for i in range(1,len(images)):
            each_product_structured_information["other_image"].append(images[i])
    ps=soup.find_all("p")
    for i in ps:
        if "SKU" in i.get_text(separator="\n", strip=True):
            each_product_structured_information["sku_code"] = i.get_text(separator="\n", strip=True).split("\n")[1]
        if "UPC" in i.get_text(separator="\n", strip=True):
            each_product_structured_information["upc_code"] = i.get_text(separator="\n", strip=True).split("\n")[1]
    forms=soup.find_all("form")
    for form in forms:
        if "Related" in form.get_text(separator=" ", strip=True):
            related_products=form.find_all("a")
            each_product_structured_information["related"]=[]
            for related_product in related_products:
                url="https://shop.kimelo.com/"+related_product.get("href")
                if not url in each_product_structured_information["related"]:
                    each_product_structured_information["related"].append(url)
            break
    labels=soup.find_all("label")
    for label in labels:
        label_text=label.get_text(separator=" ", strip=True)
        if "case" in label_text.lower():
            label_text_split=label_text.split(" ")
            for i in label_text_split:
                if "$" in i and (not "/" in i):
                    each_product_structured_information["case_price"]=float(i[1:])
                    break
    for label in labels:
        label_text=label.get_text(separator=" ", strip=True)
        if "each" in label_text.lower():
            label_text_split=label_text.split(" ")
            for i in label_text_split:
                if "$" in i and (not "/" in i):
                    each_product_structured_information["each_price"]=float(i[1:])
    table=soup.find("table")
    head=table.find("thead")
    head_items=head.find_all("th")
    head_items_text=[]
    for i in head_items:
        head_items_text.append(i.get_text(separator=" ", strip=True))
    tr_items=table.find('tbody').find_all("tr")
    information_key = ["quantity", "size", "weight"]
    td_items=tr_items[0].find_all("td")
    for td_i in range(len(td_items)):
        each_product_structured_information[head_items_text[td_i].lower()+"_quantity"]=int(td_items[td_i].text.split(" ")[0])
    td_items=tr_items[1].find_all("td")
    for td_i in range(len(td_items)):
        each_product_structured_information[head_items_text[td_i].lower()+"_size"]=td_items[td_i].text
    td_items=tr_items[2].find_all("td")
    for td_i in range(len(td_items)):
        each_product_structured_information[head_items_text[td_i].lower()+"_weight"]=float(td_items[td_i].text.split(" ")[0])
    return each_product_structured_information
def extract_product_details(soup):
    links = soup.find_all("a")
    product_cards = []
    for link in links:
        text = link.get_text(separator=" ", strip=True)
        has_image = link.find('img') is not None
        if (
            "cheese" in text.lower() and
            has_image
        ):
            product_cards.append(link)
    products_information = []
    for product_card in product_cards:
        each_product_structured_information = {}
        each_product_unstructured_information = []
        for tag in product_card.find_all():
            for child in tag.children:
                if isinstance(child, NavigableString) and child.strip():
                    each_product_unstructured_information.append(tag.get_text(strip=True))
                    break  # Only need one text child to qualify
        each_product_structured_information["name"] = each_product_unstructured_information[0]
        each_product_structured_information["brand"] = each_product_unstructured_information[1]
        each_product_structured_information["url"] = "https://shop.kimelo.com/"+product_card.get("href")
        each_product_structured_information["sample_image"] = "https://shop.kimelo.com/" + product_card.find('img').get("src")
        if "Back in stock soon" in each_product_unstructured_information:
            each_product_structured_information["stock"] = "empty"
            each_product_structured_information["alert"] = "Back in stock soon"
        else:
            each_product_structured_information["stock"] = "not empty"
        if "buy" in each_product_unstructured_information[-1].lower():
            each_product_structured_information["special"] = each_product_unstructured_information[-1]
        each_product_structured_information = extract_product_more_details(each_product_structured_information)
        products_information.append(each_product_structured_information)
    return products_information
try:
    driver.get("https://shop.kimelo.com/department/cheese/3365")
    time.sleep(0.1)  # Wait for the page to load
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Find all b tags and filter those containing 'page'
    b_tags = soup.find_all("b")
    page_tags = ''
    for tag in b_tags:
        if 'page' in tag.get_text():
            page_tags = tag;
            break;
    pages = int(page_tags.get_text().split(" ")[-1])
    page = 1
    all_products = []
    products = extract_product_details(soup)
    while True:
        products = extract_product_details(soup)
        all_products.extend(products)
        if page < pages:
            page = page + 1
            driver.get("https://shop.kimelo.com/department/cheese/3365?page="+str(page))
            time.sleep(1)
            soup = BeautifulSoup(driver.page_source, "html.parser")
        else:
            break

    with open('cheese.json', 'w') as f:
        json.dump(all_products, f, indent=2)
finally:
    driver.quit()
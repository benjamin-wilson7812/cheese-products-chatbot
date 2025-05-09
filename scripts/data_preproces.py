import json
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
import uuid
from app.core.config import settings, ModelType

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)

embedding_model = OpenAIEmbeddings(
    model=ModelType.embedding,
    openai_api_key=settings.OPENAI_API_KEY
)
def load_cheese_data():
    with open('cheese.json', 'r') as f:
        cheese_data = json.load(f)
    return cheese_data

def convert_to_sentence(cheese_product):
    sentence = ""
    sentence = sentence + "This cheese is " + cheese_product["name"] + " and it's brand is " + cheese_product["brand"] + ". "
    sentence = sentence + "The category of this cheese is " + cheese_product["category"] + ". "

    if "each_price" in cheese_product:
        sentence = sentence + "The price of this cheese is $" + str(cheese_product["each_price"]) + ". "
    if "case_price" in cheese_product:
        sentence = sentence + "The price of one case of this cheese is $" + str(cheese_product["case_price"]) + ". "
    if "price_per_unit" in cheese_product and "unit" in cheese_product:
        sentence = sentence + "The price of this cheese per " + cheese_product["unit"] + " is $" + str(cheese_product["price_per_unit"]) + ". "
    sentence = sentence + "The SKU code of this cheese is " + cheese_product["sku_code"] + " and the UPC code is " + cheese_product["upc_code"] + ". "

    if "each_size" in cheese_product:
        sentence = sentence + "The size of this cheese is " + cheese_product["each_size"] + ". "
    if "case_size" in cheese_product:
        sentence = sentence + "The size of one case of this cheese is " + cheese_product["case_size"] + ". "
    if "each_weight" in cheese_product:
        sentence = sentence + "The weight of this cheese is " + str(cheese_product["each_weight"]) + " " +  "LB."
    if "case_weight" in cheese_product:
        sentence = sentence + "The weight of one case of this cheese is " + str(cheese_product["case_weight"]) + " " + "LB."
    if "case_quantity" in cheese_product:
        sentence = sentence + "There are " + str(cheese_product["case_quantity"]) + " cheeses in one case."
    if "url" in cheese_product:
        sentence = sentence + "The url of this cheese is " + cheese_product["url"] + ". "
    if "sample_image" in cheese_product:
        sentence = sentence + "The sample image of this cheese is " + cheese_product["sample_image"] + ". "
    if "other_images" in cheese_product and len(cheese_product["other_images"]) > 0:
        sentence = sentence + "There are other images about this cheese," + "".join(cheese_product["other_images"])
    if "related_products" in cheese_product and len(cheese_product["related_products"]) > 0:
        sentence = sentence + "There are related products about this cheese," + "".join(cheese_product["related_products"])
    if "stock" in cheese_product:
        sentence = sentence + "The stock of this cheese is " + cheese_product["stock"] + ". "
    if "alert" in cheese_product:
        sentence = sentence + "This cheese " + cheese_product["alert"]
    if "special" in cheese_product:
        sentence = sentence + "The custom can "+ cheese_product["special"]
    return sentence

def get_vector(id, cheese_product):
    embedding_vector = embedding_model.embed_documents(convert_to_sentence(cheese_product))[0]
    vector = {
        "id": id,
        "values": embedding_vector,
        "metadata": cheese_product
    }
    return vector

if __name__ == "__main__":
    cheese_products = load_cheese_data()
    print(f"Loaded {len(cheese_products)} cheese products")

    for i in range(len(cheese_products)):
        index.upsert(vectors=[get_vector(str(uuid.uuid4()), cheese_products[i])], namespace="cheese-products")
        print(i)
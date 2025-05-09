sql_vector = """
You need to select one proper database, Pinecone VectorDB or MySQL Database to gather information that related to following query.

The query is as follows.
{query}

Here is the original conversation.
{conversation}

Here is SQL Query that is used to create table.
```
CREATE TABLE IF NOT EXISTS cheese_products (
  id INT PRIMARY KEY,
  name VARCHAR(255),
  brand VARCHAR(255),
  category VARCHAR(255),
  each_price DECIMAL(10,2),
  case_price DECIMAL(10,2),
  sku_code VARCHAR(255),
  upc_code VARCHAR(255),
  each_size VARCHAR(255),
  case_size VARCHAR(255),
  each_weight DECIMAL(10,2),
  case_weight DECIMAL(10,2),
  weight_unit VARCHAR(255),
  each_quantity INT,
  case_quantity INT,
  url VARCHAR(255),
  sample_image VARCHAR(255),
  other_images VARCHAR(255),
  related_products VARCHAR(255),
  stock VARCHAR(255),
  alert VARCHAR(255),
  special VARCHAR(255)
);
```
"""
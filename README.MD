# Cheese Products AI Assistant

A Streamlit-based chatbot application powered by OpenAI that helps users analyze and understand cheese productions data. The application combines vector similarity search and SQL querying capabilities to provide comprehensive insights about cheese productions.

## Features

- 💬 Interactive chat interface
- 🔍 Hybrid search (SQL + Vector) for lease information
- 🤖 AI-powered natural language understanding

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Databases**:
  - MySQL (Structured data storage)
  - Pinecone (Vector database for semantic search)
- **AI/ML**:
  - OpenAI GPT-4
  - LangChain
  - LangGraph

## Prerequisites

- Python 3.13+
- MySQL Server (We used [Xampp](https://www.apachefriends.org/) for this project)
- Pinecone Account
- OpenAI API Key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/benjamin-wilson7812/cheese-products-chatbot.git
cd cheese-products-chatbot
```

2. Create a virtual environment:
```bash
python -m virtualenv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables with your own API keys:
```bash
cp .env.example .env
```


## Project Structure

```README.MD
├── app/
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   └── prompt_templates/  # LLM prompt templates
│   ├── db/
│   │   ├── mysql.py          # MySQL database service
│   │   └── vectordb.py       # Pinecone vector database service
│   ├── schemas/
│   │   └── cheese_products.py# Data models
│   └── services/
│       ├── chat.py           # Chat service
│       └── graph/            # LangGraph workflow
│
│── scripts/
│     │
│     │── data_preprocess.py  # Embed data
│     │── data_scrap.py       # Scrap data
├── main.py                   # Application entry point
├── requirements.txt          # Project dependencies
├── .env                     # Environment variables
└── README.md                 # README file
```

## Usage

1. Start the application:
```bash
streamlit run main.py
```


2. Interact with the chatbot by asking questions about the cheese products. Example queries:
   - "What is the most expensive cheese?"
   - "How many types are there"
   - "Give me some sliced cheese."

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
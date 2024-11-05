# LangGraph Legal Assistant

## Overview

LangGraph Legal Assistant is an AI-powered tool designed to assist with legal queries related to Pakistani law. It utilizes advanced language models and vector store technology to retrieve and generate accurate legal information, ensuring efficient responses to user questions. The tool is designed to help legal professionals, researchers, and individuals seeking guidance on Pakistani legal matters.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributors](#contributors)
- [License](#license)

## Features

- **Document Retrieval:** Fetches relevant legal documents from a vector store based on user queries.
- **Question Routing:** Directs legal queries to either a vector store or web search depending on the type of query.
- **Answer Generation:** Produces concise, accurate answers using the retrieved documents as references.
- **Document Grading:** Evaluates and ranks the relevance of documents retrieved based on user queries.
- **Hallucination Detection:** Ensures that generated answers are grounded in the provided documents, reducing inaccuracies or false information.

## Installation

### Prerequisites

- Python 3.7 or higher
- Virtual environment (recommended) for dependency management
- `git` installed to clone the repository

### Steps

1. **Clone the repository:**

     ```bash
     git clone https://github.com/Nouman-Usman/Flask_API.git
     cd Flask_API
     ```

2. **Create and activate a virtual environment (optional but recommended):**

     ```bash
     python3 -m venv env
     source env/bin/activate  # For Linux/macOS
     # or
     .\env\Scripts\activate  # For Windows
     ```

3. **Install the required dependencies:**

     ```bash
     pip install -r requirements.txt
     ```

4. **Run initial setup (if any, such as downloading models or setting up a database):**

     _[Include any additional setup instructions here, such as downloading pre-trained models, initializing databases, or other necessary steps.]_

## Usage

After installation, you can start the application with the following command:

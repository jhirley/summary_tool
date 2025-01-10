# Summary Tool

This repository contains a Streamlit-based application that generates summaries from URLs (websites, PDFs, or YouTube videos) using LangChain and OpenAI APIs. The app also provides text-to-speech capabilities and evaluates the factual accuracy of the generated summaries using a hallucination grading mechanism.

## Features
- Summarize content from websites, PDFs, and YouTube videos.
- Generate audio files from text summaries.
- Assess summary accuracy using hallucination grading.
- Adjust creativity levels to fine-tune summaries.

---

## Clone the Repository

To get started, clone the repository from GitHub:

```bash
git clone https://github.com/jhirley/summary_tool.git
cd summary_tool
```

---

## Running the Application

### 1. Running Locally with Streamlit

#### Install Dependencies

1. Ensure you have Python 3.8+ installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### Add API Keys

Create a `.streamlit/secrets.toml` file in the root directory with the following structure:

```toml
[OPENAI_API_KEY]
OPENAI_API_KEY="your_openai_api_key"

[TOGETHER_API_KEY]
TOGETHER_API_KEY="your_together_api_key"
```

Replace `your_openai_api_key` and `your_together_api_key` with your actual API keys.

https://docs.streamlit.io/develop/concepts/connections/secrets-management

#### Run the Streamlit App

Start the application:
```bash
streamlit run app.py
```

Open the provided URL in your browser (default: `http://localhost:8501`).

---

### 2. Running with Docker

#### Prerequisites

1. Install Docker: [Get Docker](https://docs.docker.com/get-docker/)
2. Install Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

#### Docker-Compose Setup

Use the following `docker-compose.yaml` file:

```yaml
version: '3.9'
services:
  summary_tool:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - .:/app
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TOGETHER_API_KEY=${TOGETHER_API_KEY}
    command: streamlit run app.py
```

#### Add Environment Variables

Create a `.env` file in the root directory with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key
TOGETHER_API_KEY=your_together_api_key
```

#### Build and Run the Docker Container

1. Build the Docker image:
   ```bash
   docker-compose build
   ```

2. Start the application:
   ```bash
   docker-compose up
   ```

3. Access the app in your browser at `http://localhost:8501`.

---

### 3. Optional: Running Without Docker

If you prefer not to use Docker, ensure all dependencies are installed locally and run:

```bash
python app.py
```

---

## License
This project is open-source and available under the MIT license.

---

## Contribution
Feel free to fork the repository, submit issues, or create pull requests for improvements or additional features.

For questions or suggestions, contact the repository owner or submit an issue in GitHub.


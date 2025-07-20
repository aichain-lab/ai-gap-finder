# 🧠 AI Gap Finder Microservice

An LLM-powered microservice that analyzes scientific abstracts, PDFs, and research topics to identify research gaps, limitations, and suggest future research directions.

## 🚀 Features

- **Abstract Analysis**: Upload research abstracts to identify gaps and limitations
- **Topic-Based Analysis**: Analyze multiple papers on a specific topic from arXiv
- **PDF Support**: Extract text from PDF files for analysis
- **LLM Integration**: Uses OpenAI GPT-4 for intelligent gap detection
- **REST API**: Simple HTTP endpoints for easy integration
- **Hypothesis Generation**: Suggests testable research hypotheses
- **Field-Specific Analysis**: Context-aware analysis for different research domains

## 📋 Prerequisites

- Python 3.11+
- OpenAI API Key
- Docker (optional, for containerization)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-gap-finder
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## 🔧 Configuration

Edit the `.env` file with your settings:

```env
OPENAI_API_KEY=your_openai_api_key_here
LOG_LEVEL=INFO
DEBUG=true
```

You can also modify `config.yaml` for more detailed configuration.

## 🚀 Running the Service

### Development Mode
```bash
python main.py
```

### Docker
```bash
docker build -t ai-gap-finder .
docker run -p 8001:8001 --env-file .env ai-gap-finder
```

The service will be available at `http://localhost:8001`

## 📚 API Documentation

Once running, visit `http://localhost:8001/docs` for interactive API documentation.

### Key Endpoints:

- `POST /analyze` - Analyze a single abstract/text
- `POST /topic` - Analyze multiple papers on a topic
- `GET /health` - Health check

### Example Usage:

```python
import requests

# Analyze an abstract
response = requests.post(
    "http://localhost:8001/analyze",
    json={
        "title": "Deep Learning in Medical Imaging",
        "abstract": "This study explores the application of convolutional neural networks...",
        "field": "medicine"
    }
)

result = response.json()
print(result["gaps"])  # Research gaps identified
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app
```

## 🏗️ Architecture

```
ai-gap-finder/
├── app/
│   ├── api/           # FastAPI routes
│   ├── core/          # Configuration and prompts
│   ├── extract/       # PDF text extraction
│   ├── schema/        # Pydantic models
│   ├── service/       # Business logic (LLM, arXiv)
│   └── utils/         # Utilities and logging
├── tests/             # Test suite
├── config.yaml        # Configuration
├── Dockerfile         # Container definition
└── main.py           # Application entry point
```

## 🔗 Integration with Backend

This microservice is designed to integrate with the Go backend via REST API calls:

```go
// Go backend integration example
type GapAnalysisRequest struct {
    Title    string `json:"title"`
    Abstract string `json:"abstract"`
    Field    string `json:"field"`
}

func analyzeGaps(title, abstract, field string) (*GapAnalysisResponse, error) {
    url := "http://localhost:8001/analyze"
    payload := GapAnalysisRequest{
        Title:    title,
        Abstract: abstract,
        Field:    field,
    }
    
    // Make HTTP request to microservice
    // Handle response...
}
```

## 🐳 Docker Support

The service includes Docker support for easy deployment:

```bash
# Build image
docker build -t ai-gap-finder .

# Run container
docker run -p 8001:8001 \
  -e OPENAI_API_KEY=your_key \
  ai-gap-finder
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

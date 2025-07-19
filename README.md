# 🚀 Electronix AI: Advanced Sentiment Analysis Platform

**Assignment Submission for Electronic AI**

[🔗 **Repository**](https://github.com/Vansh41104/Electronix-AI-Assignment-Submission)

The assignment is a cutting-edge, full-stack sentiment analysis platform that combines the power of Transformer models with modern web technologies. Built with a sleek Next.js frontend and robust FastAPI backend, it delivers real-time sentiment predictions, custom model fine-tuning, and seamless deployment through Docker orchestration.

---

## 📺 Live Demo & Video

### 🌐 Live Demo

Try Assignment in action: [https://assignment.vanshbhatnagar.space/](https://assignment.vanshbhatnagar.space/)

### 🎥 Video Walkthrough

Watch the complete platform demonstration: **\[YouTube Video Coming Soon]**

---

## 🌟 Key Features

* 🔍 **Real-Time Sentiment Analysis**: Lightning-fast predictions powered by Hugging Face Transformers
* 🎯 **Custom Model Fine-Tuning**: Train models with your own datasets for domain-specific accuracy
* 🐳 **Dockerized Deployment**: One-command setup with Docker Compose orchestration
* 💻 **Modern UI/UX**: Responsive Next.js interface with Tailwind CSS styling
* 🌙 **Dark/Light Mode**: Seamless theme switching for enhanced user experience
* ⚡ **FastAPI Backend**: High-performance API with GraphQL support
* 🔄 **Hot Model Reloading**: Automatic weight updates in development mode, with container restart for production
* 📱 **Mobile-First Design**: Fully responsive across all devices

---

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   Transformer   │
│   Frontend      │◄──►│   Backend       │◄──►│   Model         │
│   (Port 3000)   │    │   (Port 8000)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Docker        │
                    │   Compose       │
                    └─────────────────┘
```

---

## 📁 Project Structure

```bash
Electronix-AI-Assignment-Submission/
├── 🔧 backend/                    
│   ├── app.py                    
│   ├── finetune.py               
│   ├── sentiment.py              
│   ├── data.jsonl                
│   ├── requirements.txt         
│   ├── Dockerfile                
│   └── model/                    
├── 🎨 frontend/                  
│   ├── src/app/                  
│   ├── public/                  
│   ├── globals.css               
│   ├── package.json             
│   ├── Dockerfile               
│   └── tailwind.config.js      
├── 🐳 docker-compose.yml          
└── 📖 README.md                   
```

---

## 🚀 Quick Start Guide

### 📋 Prerequisites

Ensure you have the following installed:

* 🐍 **Python 3.12+**
* 🌐 **Node.js 18+**
* 🐳 **Docker & Docker Compose**

### ⚡ One-Command Setup

```bash
# Clone the repository
git clone https://github.com/Vansh41104/Electronix-AI-Assignment-Submission.git
cd Electronix-AI-Assignment-Submission

# Launch the entire platform
docker-compose build
```

**That's it!** 🎉 Your services will be available at:

* 🖥️ Frontend: [http://localhost:3000](http://localhost:3000)
* 🔧 Backend API: [http://localhost:8000](http://localhost:8000)
* 📊 API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Development Setup

### 🔧 Backend Development

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run development server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 🎨 Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

---

## 🧠 Model Fine-Tuning

### 📊 Prepare Training Data

Create your training dataset in `backend/data.jsonl`:

```jsonl
{"text": "This product is absolutely amazing!", "label": "positive"}
{"text": "Terrible experience, would not recommend.", "label": "negative"}
{"text": "Great customer service and fast delivery.", "label": "positive"}
{"text": "The quality is disappointing for the price.", "label": "negative"}
```

### 🎯 Fine-Tune Your Model

```bash
# Basic fine-tuning
python backend/finetune.py --data backend/data.jsonl

# Advanced fine-tuning with custom parameters
python backend/finetune.py \
    --data backend/data.jsonl \
    --epochs 5 \
    --lr 2e-5 \
    --batch_size 16
```

### 🔄 Hot Model Reloading

**Development Environment:**

* Hot model reloading is automatically enabled when running the backend with `--reload` flag
* Model weights are monitored for changes and updated without server restart
* Perfect for rapid experimentation and testing

**Docker Environment:**

* For containerized deployments, the Docker container needs to be restarted to load new model weights
* Use `docker-compose restart backend` after model fine-tuning
* Alternatively, rebuild the container for permanent model updates: `docker-compose build backend`

```bash
# Development: Automatic hot reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Docker: Manual restart after model updates
docker-compose restart backend
# or
docker-compose build backend && docker-compose up -d
```

---

## 🌐 API Documentation

### REST Endpoints

#### Sentiment Prediction

```bash
POST /graphql
Content-Type: application/json

{
  "text": "Your text to analyze"
}
```

**Response:**

```json
{
  "label": "positive",
  "score": 0.9234,
  "confidence": "high"
}
```

### GraphQL Schema

```graphql
type Query {
  predictSentiment(text: String!): SentimentResult
}

type SentimentResult {
  label: String!
  score: Float!
  confidence: String!
}
```

---

## 🎨 Frontend Features

### 🌟 Core Components

* **📝 Text Input**: Large textarea with placeholder guidance
* **🎯 Predict Button**: One-click sentiment analysis
* **📊 Results Display**: Clean visualization of predictions
* **🌙 Theme Toggle**: Dark/light mode switching
* **📱 Responsive Design**: Mobile-optimized interface

### 🎭 UI/UX Highlights

* **Instant Feedback**: Real-time prediction results
* **Loading States**: Smooth animations during processing
* **Error Handling**: User-friendly error messages
* **Accessibility**: Full keyboard navigation support

---

## 🧰 Technology Stack

| **Category** | **Technologies**                                 |
| ------------ | ------------------------------------------------ |
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS   |
| **Backend**  | FastAPI, Python 3.12, GraphQL (Strawberry)       |
| **ML/AI**    | Hugging Face Transformers, PyTorch, scikit-learn |
| **DevOps**   | Docker, Docker Compose, Multi-stage builds       |
| **Data**     | JSONL format, Hot-reload file watching           |

---

## 🔧 Configuration Options

### Docker Compose Profiles

```bash
# CPU-only deployment (default)
docker-compose build

# GPU-enabled deployment
docker-compose --profile gpu up

# Development mode with hot-reload
docker-compose --profile dev up
```

---

## 🚢 Deployment Options

### Local Development (This might take some time to download the libraries and load the model)

```bash
docker-compose build

docker-compose up
```

---

## 📧 Contact & Support

* **Creator**: Vansh
* **Email**: [vanshbhatnagar445@gmail.com](mailto:vanshbhatnagar445@gmail.com)
* **GitHub**: [https://github.com/Vansh41104](https://github.com/Vansh41104)
* **LinkedIn**: [https://www.linkedin.com/in/vansh-bhatnagar-66465225b/](https://www.linkedin.com/in/vansh-bhatnagar-66465225b/)
* **Portfolio**: [https://www.vanshbhatnagar.space/](https://www.vanshbhatnagar.space/)

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by [Vansh](https://github.com/Vansh41104).

</div>

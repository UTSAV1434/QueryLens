# 📊 QueryLens — Conversational BI Dashboard

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![React](https://img.shields.io/badge/React-18.x-blue)
![Vite](https://img.shields.io/badge/Vite-4.x-purple)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.0_Flash-orange)

![QueryLens Screenshot](./frontend/src/assets/hero.png)

> **Empower your data with natural language.** Upload any CSV dataset and ask questions in plain English. Get interactive charts and insights instantly, powered by Google Gemini AI.

QueryLens is a powerful conversational Business Intelligence dashboard designed to make data analysis accessible to everyone. Forget complex SQL queries or intricate charting libraries—just upload your data, ask a question, and let AI do the rest.

---

## ✨ Features

- **Dataset Agnostic:** Upload any CSV file and start querying immediately. No predefined schemas required.
- **Natural Language Queries:** Ask questions in plain English (*"What were the sales for Q1 2023?"*).
- **Smart Chart Generation:** The LLM automatically selects the best visualization type (Bar, Line, Pie, Area, Table).
- **Interactive Visualizations:** Powered by Recharts with tooltips, legends, and animations.
- **Real-time execution:** Uses pandas in the backend to execute AI-generated queries safely and return results in real-time.

## 🏗️ Architecture

```text
User → React Chat UI → Flask API → Gemini LLM → Pandas Query → JSON → Recharts Dashboard
```

1. **User Input:** User uploads a CSV and types a natural language question.
2. **LLM Processing:** The Flask backend sends the dataframe schema and the user's question to Google Gemini.
3. **Query Generation:** Gemini generates robust `pandas` code to extract the specific insights.
4. **Execution:** The backend safely executes the `pandas` query and formats the result as JSON.
5. **Visualization:** The React frontend receives the JSON and dynamically renders the appropriate Recharts component.

## 🛠️ Tech Stack

### Frontend
- **Framework:** React + Vite
- **Charts:** Recharts

### Backend
- **Framework:** Python Flask
- **Data Processing:** Pandas
- **AI/LLM:** Google Gemini 2.0 Flash (`google-generativeai`)

---

## 🚀 Quick Start

Follow these instructions to get the project up and running locally.

### Prerequisites
- Node.js (v16+)
- Python (3.8+)
- Google Gemini API Key (Get one from Google AI Studio)

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment (Recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Start the Flask server:
```bash
python app.py
```
*The backend will typically run on http://localhost:5000*

### 2. Frontend Setup

Open a new terminal window.

```bash
# Navigate to the frontend directory
cd frontend

# Install npm packages
npm install

# Start the development server
npm run dev
```

Open **http://localhost:5173** in your browser to interact with the dashboard.

---

## 📈 Sample Queries to Try

Once you upload a dataset (e.g., a sample sales `.csv` file), try these queries:

- *"Show total revenue by region"*
- *"What is the monthly sales trend over time?"*
- *"Compare profit margins across different product categories"*
- *"What are the top 10 best-selling products by volume?"*
- *"Show me a pie chart of sales distribution by country"*

---

## 🌐 Deployment (Hackathon Ready)

### Frontend (Netlify or Vercel)
1. Push your code to GitHub.
2. Connect the repository to your chosen platform.
3. Set the build command to `npm run build` and the publish directory to `dist/`.
4. Add any required environment variables (like your backend API URL if configured).

### Backend (Render or Heroku)
1. Deploy the `backend/` directory as a Web Service.
2. Provide the `GEMINI_API_KEY` in the environment variables of your hosting platform.
3. Make sure to use `gunicorn` or a production server to run the Flask app.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

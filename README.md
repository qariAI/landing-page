# 🎙️ QariAI - AI-Powered Tajweed & Hifz Coach

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?logo=vite)](https://vitejs.dev/)

> Perfect your Quran recitation with AI-powered feedback. Get instant Tajweed analysis, track your Hifz progress, and recite with confidence.

[🌐 Live Demo](https://qariai.app) | [📧 Contact](mailto:salam@qariai.app) | [🐦 Twitter](https://twitter.com/qariai)

---

## ✨ Features

### 🎤 **Real-Time Tajweed Analysis**
- AI-powered pronunciation feedback
- Detects Makharij (articulation points)
- Analyzes Ghunnah, Madd, Qalqalah, and more
- Categorizes mistakes by severity (Major/Minor)

### 🧠 **Hifz Companion**
- Spaced repetition system for memorization
- Due revision tracking
- Memory strength analytics
- Progress retention charts

### 📊 **Progress Analytics**
- Visual dashboard with radar charts
- XP and leveling system (Beginner → Intermediate → Advanced)
- Daily streaks tracking
- Weak rule identification

### 🎯 **Personalized Drills**
- AI-generated practice exercises
- Targeted drills for weak Tajweed rules
- "Regenerate" button for unlimited practice
- Proficiency-based difficulty adjustment

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/qariai.git
cd qariai

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Add your Gemini API key to .env
# VITE_GEMINI_API_KEY=your_api_key_here

# Start development server
npm run dev
```

Visit `http://localhost:5173` 🎉

---

## 🏗️ Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Styling
- **Google Gemini 2.5** - AI analysis
- **Recharts** - Analytics visualizations
- **LocalStorage** - Data persistence

---

## 📁 Project Structure

```
qariai/
├── src/
│   ├── components/
│   │   ├── Recorder.tsx
│   │   ├── Feedback.tsx
│   │   ├── Dashboard.tsx
│   │   └── HifzMode.tsx
│   ├── services/
│   │   ├── geminiService.ts
│   │   └── progressService.ts
│   ├── types.ts
│   └── App.tsx
├── public/
├── .env.example
└── vite.config.ts
```

---

## 🔧 Environment Variables

Create a `.env` file:

```env
VITE_GEMINI_API_KEY=your_api_key_here
```

---

## 🚀 Deployment

### Deploy to Vercel

```bash
npm i -g vercel
vercel login
vercel --prod
```

Add environment variables in Vercel dashboard under "Settings" → "Environment Variables"

---

## 🗺️ Roadmap

- [x] MVP: Audio recording & AI analysis
- [x] Progress tracking & Hifz mode
- [ ] User authentication
- [ ] Backend API proxy
- [ ] Mobile apps (iOS/Android)
- [ ] Offline mode
- [ ] Multiple Qira'at support

---

## 🤝 Contributing

Contributions welcome! Please open an issue first to discuss changes.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 📞 Contact

- **Email:** [salam@qariai.app](mailto:salam@qariai.app)
- **Twitter:** [@qariai](https://twitter.com/qariai)
- **Website:** [qariai.app](https://qariai.app)

---

<div align="center">

**Built with ❤️ for the Ummah**

*May Allah accept this work and make it beneficial*

</div>

// App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home.jsx';
import About from './components/About.jsx';
import StandalonePageWithComponent from './components/StandalonePageWithComponent.jsx';
// import Chatbot from './components/Chatbot.jsx';
import { LawyerAiChatJsx } from './components/lawyer-ai-chat.jsx';

function App() {
  return (
    <Router>
      <Routes>
        {/* Define routes here */}
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/standalone" element={<StandalonePageWithComponent />} />
        <Route path="/chatbot" element={<LawyerAiChatJsx />} />
        <Route path="/lawyer/:id" element={<div>Lawyer Profile Placeholder</div>} />        
        {/* You can add more routes as needed */}
      </Routes>
    </Router>
  );
}

export default App;

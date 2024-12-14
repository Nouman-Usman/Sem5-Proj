import React, { useState, useEffect } from 'react';
import { FaBriefcase, FaUser, FaStar, FaCalendar, FaComments } from 'react-icons/fa';
import io from 'socket.io-client';
import apiService from '../services/api';

const LawyerDashboard = () => {
  const [showChat, setShowChat] = useState(false);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [chatId, setChatId] = useState(null);
  const [lawyerData, setLawyerData] = useState({});
  const [recentActivities, setRecentActivities] = useState([]);
  const socket = io('http://localhost:5000');
  const [displayName, setDisplayName] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [delta, setDelta] = useState(200);

  useEffect(() => {
    const fetchLawyerData = async () => {
      const response = await apiService.getLawyerDashboardData();
      setLawyerData(response.lawyerData);
      setRecentActivities(response.recentActivities);
    };

    fetchLawyerData();
    const intervalId = setInterval(fetchLawyerData, 5000); // Fetch data every 5 seconds

    return () => clearInterval(intervalId); // Cleanup interval on component unmount
  }, []);

  useEffect(() => {
    if (chatId) {
      socket.emit('join', { chat_id: chatId });
      socket.on('message', (msg) => {
        setMessages((prevMessages) => [...prevMessages, msg]);
      });

      return () => {
        socket.emit('leave', { chat_id: chatId });
        socket.off('message');
      };
    }
  }, [chatId]);

  useEffect(() => {
    // Get user name from localStorage
    const user = JSON.parse(localStorage.getItem('user'));
    const userName = user?.name || 'Lawyer';
    setDisplayName(userName.charAt(0)); // Start with first character
  }, []);

  useEffect(() => {
    let ticker = setInterval(() => {
      tick();
    }, delta);

    return () => clearInterval(ticker);
  }, [displayName, isDeleting]);

  const tick = () => {
    const user = JSON.parse(localStorage.getItem('user'));
    const fullName = user?.name || 'Lawyer';
    
    if (isDeleting) {
      setDisplayName(fullName.substring(0, displayName.length - 1));
      setDelta(100);
    } else {
      setDisplayName(fullName.substring(0, displayName.length + 1));
      setDelta(200);
    }

    if (!isDeleting && displayName === fullName) {
      setTimeout(() => setIsDeleting(true), 2000);
    } else if (isDeleting && displayName === '') {
      setIsDeleting(false);
    }
  };

  const startChat = async (recipientId) => {
    const response = await apiService.startChat(recipientId);
    setChatId(response.chat_id);
  };

  const sendMessage = () => {
    if (message.trim()) {
      socket.emit('message', { chat_id: chatId, message });
      setMessage('');
    }
  };

  return (
    <div className="min-h-screen bg-[#030614] p-8 pt-24 relative overflow-hidden opacity-0 animate-fadeIn">
      {/* Add purple luminous background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[#9333EA]/20 rounded-full blur-[128px] animate-fadeInSlow"></div>
        <div className="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-[#7E22CE]/20 rounded-full blur-[96px] animate-fadeInSlow delay-300"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-[#6B21A8]/20 rounded-full blur-[64px] animate-fadeInSlow delay-500"></div>
      </div>

      {/* Updated Header with animation */}
      <div className="mb-8 animate-fadeIn relative z-10 opacity-0 animate-slideInDown delay-200">
        <h1 className="text-3xl font-bold text-white">
          Welcome, {' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 typewriter">
            {displayName}
          </span>
        </h1>
        <p className="text-gray-400">Here's your dashboard overview</p>
      </div>

      {/* Chat Icon with pulse effect */}
      <div className="fixed bottom-8 right-8">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-[#9333EA] to-[#7E22CE] rounded-full blur opacity-75 group-hover:opacity-100 animate-pulse"></div>
        <button
          className="relative bg-[#9333EA] text-white p-4 rounded-full shadow-lg hover:bg-[#7E22CE] transition-all duration-300 hover:scale-110 hover:shadow-[0_0_20px_rgba(147,51,234,0.5)]"
          onClick={() => setShowChat(!showChat)}
        >
          <FaComments size={24} />
        </button>
      </div>

      {/* Chat Card with enhanced animation */}
      {showChat && (
        <div className="fixed bottom-20 right-8 bg-[#030614] rounded-lg p-4 w-80 
          animate-slideIn border border-[#9333EA]/30
          shadow-[0_0_25px_rgba(147,51,234,0.2)]
          hover:shadow-[0_0_30px_rgba(147,51,234,0.3)]
          backdrop-blur-lg relative z-10
          animate-borderGlow">
          <h2 className="text-xl font-semibold mb-4 text-white">Chat</h2>
          <div className="h-64 overflow-y-scroll mb-4">
            {messages.map((msg, index) => (
              <div key={index} className="mb-2">
                <div className="bg-gray-700 p-2 rounded text-white">{msg.message}</div>
              </div>
            ))}
          </div>
          <div className="flex">
            <input
              type="text"
              className="flex-1 border border-gray-600 rounded-l p-2 bg-[#030614] text-white"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            <button
              className="bg-[#9333EA] text-white p-2 rounded-r hover:bg-[#7E22CE] transition"
              onClick={sendMessage}
            >
              Send
            </button>
          </div>
        </div>
      )}

      {/* Stats Grid with hover effects */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8 relative z-10">
        { [
          { icon: <FaBriefcase />, title: "Total Cases", value: lawyerData.totalCases, change: "+5%", delay: "delay-300" },
          { icon: <FaUser />, title: "Active Clients", value: lawyerData.activeClients, change: "+12%", delay: "delay-400" },
          { icon: <FaStar />, title: "Rating", value: lawyerData.rating, change: "+0.2", delay: "delay-500" },
          { icon: <FaCalendar />, title: "Appointments", value: lawyerData.appointments, change: "This week", delay: "delay-600" }
        ].map((stat, index) => (
          <div key={index} className={`opacity-0 animate-slideInUp ${stat.delay}`}>
            <StatCard {...stat} />
          </div>
        ))}
      </div>

      {/* Main Content with enhanced cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative z-10">
        {/* Recent Activities */}
        <div className="lg:col-span-2 bg-gradient-to-b from-[#1A1A2E] to-[#15152d] rounded-lg p-[1px]
          border border-[#9333EA]/20 
          opacity-100 transform transition-all duration-700 ease-out
          animate-[slideInLeft_0.7s_ease-out_forwards]">
          <div className="bg-[#1A1A2E]/95 rounded-lg p-6 h-full backdrop-blur-sm
            hover:shadow-[0_0_30px_rgba(147,51,234,0.2)] transition-all duration-300">
            <h2 className="text-xl font-semibold mb-4 text-white">Recent Activities</h2>
            <div className="space-y-4">
              {recentActivities.map((activity, index) => (
                <ActivityItem 
                  key={index} 
                  activity={activity} 
                  className={`animate-[fadeIn_0.3s_ease-out_forwards] delay-${300 + (index * 100)}`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Profile Card */}
        <div className="bg-gradient-to-b from-[#1A1A2E] to-[#15152d] rounded-lg p-[1px]
          border border-[#9333EA]/20 
          opacity-100 transform transition-all duration-700 ease-out
          animate-[slideInRight_0.7s_ease-out_forwards]">
          <div className="bg-[#1A1A2E]/95 rounded-lg p-6 h-full backdrop-blur-sm
            hover:shadow-[0_0_30px_rgba(147,51,234,0.2)] transition-all duration-300">
            <h2 className="text-xl font-semibold mb-4 text-white">Profile Overview</h2>
            <div className="flex flex-col items-center">
              <div className="w-32 h-32 rounded-full bg-gray-700 mb-4 animate-[fadeIn_0.5s_ease-out_forwards] delay-300 relative">
                <img src={lawyerData.profilePicture} alt="Profile" className="w-full h-full rounded-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-r from-[#9333EA] to-[#7E22CE] opacity-0 hover:opacity-50 transition-opacity duration-300 rounded-full"></div>
              </div>
              <h3 className="text-lg font-medium text-white animate-[fadeIn_0.5s_ease-out_forwards] delay-400">{lawyerData.name}</h3>
              <p className="text-gray-400 mb-4 animate-[fadeIn_0.5s_ease-out_forwards] delay-500">{lawyerData.specialization}</p>
              <div className="w-full space-y-2">
                <ProfileDetail label="Experience" value={`${lawyerData.experience} years`} />
                <ProfileDetail label="Success Rate" value={`${lawyerData.successRate}%`} />
                <ProfileDetail label="Location" value={lawyerData.location} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add new keyframes and animations */}
      <style jsx>{`
        @keyframes slideIn {
          from { transform: translateX(100px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes glow {
          0% { box-shadow: 0 0 5px rgba(147,51,234,0.2); }
          50% { box-shadow: 0 0 20px rgba(147,51,234,0.4); }
          100% { box-shadow: 0 0 5px rgba(147,51,234,0.2); }
        }

        @keyframes borderGlow {
          0% { border-color: rgba(147,51,234,0.2); }
          50% { border-color: rgba(147,51,234,0.6); }
          100% { border-color: rgba(147,51,234,0.2); }
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes fadeInSlow {
          0% { opacity: 0; transform: scale(0.9); }
          100% { opacity: 1; transform: scale(1); }
        }

        @keyframes slideInDown {
          from { 
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slideInLeft {
          from {
            opacity: 0;
            transform: translateX(-50px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(50px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.6s ease-out forwards;
        }

        .animate-fadeInSlow {
          animation: fadeInSlow 1.2s ease-out forwards;
        }

        .animate-slideInDown {
          animation: slideInDown 0.6s ease-out forwards;
        }

        .animate-slideInUp {
          animation: slideInUp 0.6s ease-out forwards;
        }

        .animate-slideInLeft {
          animation: slideInLeft 0.6s ease-out forwards;
        }

        .animate-slideInRight {
          animation: slideInRight 0.6s ease-out forwards;
        }

        .delay-200 { animation-delay: 200ms; }
        .delay-300 { animation-delay: 300ms; }
        .delay-400 { animation-delay: 400ms; }
        .delay-500 { animation-delay: 500ms; }
        .delay-600 { animation-delay: 600ms; }
        .delay-700 { animation-delay: 700ms; }
        .delay-800 { animation-delay: 800ms; }

        .animate-borderGlow {
          animation: borderGlow 2s ease-in-out infinite;
        }

        .typewriter {
          display: inline-block;
          border-right: 4px solid #9333EA;
          animation: blink 0.75s step-end infinite;
          padding-right: 4px;
        }

        @keyframes blink {
          from, to { border-color: transparent }
          50% { border-color: #9333EA }
        }
      `}</style>
    </div>
  );
};

const StatCard = ({ icon, title, value, change }) => (
  <div className="group relative transition-all duration-300 hover:scale-105">
    <div className="absolute -inset-0.5 bg-gradient-to-r from-[#9333EA] to-[#7E22CE] rounded-lg blur opacity-30 group-hover:opacity-70 transition duration-500"></div>
    <div className="relative bg-[#1A1A2E] rounded-lg p-4 
      transform transition-all duration-300 
      hover:scale-105 hover:shadow-[0_0_30px_rgba(147,51,234,0.3)]
      border border-[#9333EA]/20
      animate-borderGlow">
      <div className="flex items-center justify-between mb-2">
        <div className="text-[#9333EA] text-2xl group-hover:scale-110 transition-transform duration-300">{icon}</div>
        <span className="text-green-500 text-sm animate-pulse">{change}</span>
      </div>
      <h3 className="text-gray-400 text-sm">{title}</h3>
      <p className="text-2xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-white to-purple-500">{value}</p>
    </div>
  </div>
);

const ActivityItem = ({ activity, className = '' }) => (
  <div className={`flex items-center p-4 bg-[#2E2E3A] rounded-lg 
    transform transition-all duration-300
    hover:bg-[#3E3E4A] hover:scale-[1.02] 
    hover:shadow-[0_0_15px_rgba(147,51,234,0.2)]
    border border-[#9333EA]/20
    ${className}`}>
    <div className="w-2 h-2 bg-gradient-to-r from-[#9333EA] to-[#7E22CE] rounded-full mr-4 animate-pulse"></div>
    <div>
      <p className="font-medium text-white">{activity.Activity}</p>
      <p className="text-sm text-gray-400">{activity.Time}</p>
    </div>
  </div>
);

const ProfileDetail = ({ label, value }) => (
  <div className="flex justify-between items-center py-2 border-b border-gray-600/50 
    hover:border-[#9333EA]/50 transition-colors duration-300">
    <span className="text-gray-400">{label}</span>
    <span className="font-medium text-white">{value}</span>
  </div>
);

export default LawyerDashboard;

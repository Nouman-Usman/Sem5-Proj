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
    <div className="min-h-screen bg-white p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-black">Welcome, {lawyerData.name}</h1>
        <p className="text-gray-600">Here's your dashboard overview</p>
      </div>

      {/* Chat Icon */}
      <div className="fixed bottom-8 right-8">
        <button
          className="bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition"
          onClick={() => setShowChat(!showChat)}
        >
          <FaComments size={24} />
        </button>
      </div>

      {/* Chat Card */}
      {showChat && (
        <div className="fixed bottom-20 right-8 bg-white rounded-lg shadow-lg p-4 w-80 animate-fadeIn">
          <h2 className="text-xl font-semibold mb-4">Chat</h2>
          <div className="h-64 overflow-y-scroll mb-4">
            {messages.map((msg, index) => (
              <div key={index} className="mb-2">
                <div className="bg-gray-200 p-2 rounded">{msg.message}</div>
              </div>
            ))}
          </div>
          <div className="flex">
            <input
              type="text"
              className="flex-1 border border-gray-300 rounded-l p-2"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            <button
              className="bg-blue-600 text-white p-2 rounded-r hover:bg-blue-700 transition"
              onClick={sendMessage}
            >
              Send
            </button>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <StatCard
          icon={<FaBriefcase />}
          title="Total Cases"
          value={lawyerData.totalCases}
          change="+5%"
        />
        <StatCard
          icon={<FaUser />}
          title="Active Clients"
          value={lawyerData.activeClients}
          change="+12%"
        />
        <StatCard
          icon={<FaStar />}
          title="Rating"
          value={lawyerData.rating}
          change="+0.2"
        />
        <StatCard
          icon={<FaCalendar />}
          title="Appointments"
          value={lawyerData.appointments}
          change="This week"
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Activities */}
        <div className="lg:col-span-2 bg-gray-100 rounded-lg shadow-md p-6 animate-fadeInLeft">
          <h2 className="text-xl font-semibold mb-4 text-black">Recent Activities</h2>
          <div className="space-y-4">
            {recentActivities.map((activity, index) => (
              <ActivityItem key={index} activity={activity} />
            ))}
          </div>
        </div>

        {/* Profile Card */}
        <div className="bg-gray-100 rounded-lg shadow-md p-6 animate-fadeInRight">
          <h2 className="text-xl font-semibold mb-4 text-black">Profile Overview</h2>
          <div className="flex flex-col items-center">
            <div className="w-32 h-32 rounded-full bg-gray-300 mb-4"></div>
            <h3 className="text-lg font-medium text-black">{lawyerData.name}</h3>
            <p className="text-gray-600 mb-4">{lawyerData.specialization}</p>
            <div className="w-full space-y-2">
              <ProfileDetail label="Experience" value={`${lawyerData.experience} years`} />
              <ProfileDetail label="Success Rate" value={`${lawyerData.successRate}%`} />
              <ProfileDetail label="Location" value={lawyerData.location} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ icon, title, value, change }) => (
  <div className="bg-gray-100 rounded-lg shadow-md p-4 hover:shadow-xl transition cursor-pointer">
    <div className="flex items-center justify-between mb-2">
      <div className="text-blue-600 text-2xl">{icon}</div>
      <span className="text-green-500 text-sm">{change}</span>
    </div>
    <h3 className="text-gray-600 text-sm">{title}</h3>
    <p className="text-2xl font-semibold text-black">{value}</p>
  </div>
);

const ActivityItem = ({ activity }) => (
  <div className="flex items-center p-4 bg-gray-200 rounded-lg hover:bg-gray-300 transition">
    <div className="w-2 h-2 bg-blue-600 rounded-full mr-4"></div>
    <div>
      <p className="font-medium text-gray-800">{activity.Activity}</p>
      <p className="text-sm text-gray-600">{activity.Time}</p>
    </div>
  </div>
);

const ProfileDetail = ({ label, value }) => (
  <div className="flex justify-between items-center py-2 border-b border-gray-300">
    <span className="text-gray-600">{label}</span>
    <span className="font-medium text-black">{value}</span>
  </div>
);

export default LawyerDashboard;

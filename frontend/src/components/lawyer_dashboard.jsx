import React, { useState, useEffect } from 'react';
import { FaBriefcase, FaUser, FaStar, FaCalendar, FaComments } from 'react-icons/fa';
import io from 'socket.io-client';

const LawyerDashboard = () => {
  const [showChat, setShowChat] = useState(false);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const socket = io('http://localhost:3000');

  useEffect(() => {
    socket.on('message', (msg) => {
      setMessages((prevMessages) => [...prevMessages, msg]);
    });

    return () => {
      socket.off('message');
    };
  }, [socket]);

  const sendMessage = () => {
    if (message.trim()) {
      socket.emit('message', message);
      setMessage('');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Welcome, Lawyer Name</h1>
        <p className="text-gray-600">Here's your dashboard overview</p>
      </div>

      {/* Chat Icon */}
      <div className="fixed bottom-8 right-8">
        <button
          className="bg-blue-600 text-white p-4 rounded-full shadow-lg"
          onClick={() => setShowChat(!showChat)}
        >
          <FaComments size={24} />
        </button>
      </div>

      {/* Chat Card */}
      {showChat && (
        <div className="fixed bottom-20 right-8 bg-white rounded-lg shadow-lg p-4 w-80">
          <h2 className="text-xl font-semibold mb-4">Chat</h2>
          <div className="h-64 overflow-y-scroll mb-4">
            {messages.map((msg, index) => (
              <div key={index} className="mb-2">
                <div className="bg-gray-200 p-2 rounded">{msg}</div>
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
              className="bg-blue-600 text-white p-2 rounded-r"
              onClick={sendMessage}
            >
              Send
            </button>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<FaBriefcase />}
          title="Total Cases"
          value="124"
          change="+5%"
        />
        <StatCard
          icon={<FaUser />}
          title="Active Clients"
          value="45"
          change="+12%"
        />
        <StatCard
          icon={<FaStar />}
          title="Rating"
          value="4.8"
          change="+0.2"
        />
        <StatCard
          icon={<FaCalendar />}
          title="Appointments"
          value="8"
          change="This week"
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Activities */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Activities</h2>
          <div className="space-y-4">
            {[1, 2, 3].map((item) => (
              <ActivityItem key={item} />
            ))}
          </div>
        </div>

        {/* Profile Card */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Profile Overview</h2>
          <div className="flex flex-col items-center">
            <div className="w-32 h-32 rounded-full bg-gray-300 mb-4"></div>
            <h3 className="text-lg font-medium">John Doe</h3>
            <p className="text-gray-600 mb-4">Criminal Law Specialist</p>
            <div className="w-full space-y-2">
              <ProfileDetail label="Experience" value="8 years" />
              <ProfileDetail label="Success Rate" value="92%" />
              <ProfileDetail label="Location" value="New York, USA" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ icon, title, value, change }) => (
  <div className="bg-white rounded-lg shadow-md p-6">
    <div className="flex items-center justify-between mb-4">
      <div className="text-blue-600 text-2xl">{icon}</div>
      <span className="text-green-500 text-sm">{change}</span>
    </div>
    <h3 className="text-gray-600 text-sm">{title}</h3>
    <p className="text-2xl font-semibold text-gray-800">{value}</p>
  </div>
);

const ActivityItem = () => (
  <div className="flex items-center p-4 bg-gray-50 rounded-lg">
    <div className="w-2 h-2 bg-blue-600 rounded-full mr-4"></div>
    <div>
      <p className="font-medium">New case assignment</p>
      <p className="text-sm text-gray-600">2 hours ago</p>
    </div>
  </div>
);

const ProfileDetail = ({ label, value }) => (
  <div className="flex justify-between items-center py-2 border-b border-gray-100">
    <span className="text-gray-600">{label}</span>
    <span className="font-medium">{value}</span>
  </div>
);

export default LawyerDashboard;

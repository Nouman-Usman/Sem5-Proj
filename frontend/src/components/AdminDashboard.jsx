import React, { useState, useEffect } from 'react';
import { FaUserTie, FaUsers, FaChartBar, FaExclamationTriangle, FaComments } from 'react-icons/fa';
import apiService from '../services/api';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalLawyers: 0,
    totalClients: 0,
    activeSubscriptions: 0,
    pendingApprovals: 0
  });
  const [lawyers, setLawyers] = useState([]);
  const [clients, setClients] = useState([]);
  const [displayName, setDisplayName] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [delta, setDelta] = useState(200);

  useEffect(() => {
    const fetchData = async () => {
      const response = await apiService.getAdminDashboardData();
      setStats(response.stats);
      setLawyers(response.lawyers);
      setClients(response.clients);
    };

    fetchData();
    const intervalId = setInterval(fetchData, 30000); // Refresh every 30 seconds

    return () => clearInterval(intervalId);
  }, []);

  // Typewriter effect (same as lawyer dashboard)
  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user'));
    const userName = user?.name || 'Admin';
    setDisplayName(userName.charAt(0));
  }, []);

  // Animation logic (same as lawyer dashboard)
  useEffect(() => {
    let ticker = setInterval(() => {
      tick();
    }, delta);

    return () => clearInterval(ticker);
  }, [displayName, isDeleting]);

  const tick = () => {
    const user = JSON.parse(localStorage.getItem('user'));
    const fullName = user?.name || 'Admin';
    
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

  const handleApproval = async (lawyerId, status) => {
    await apiService.updateLawyerStatus(lawyerId, status);
    // Refresh data after approval
    const response = await apiService.getAdminDashboardData();
    setLawyers(response.lawyers);
  };

  return (
    <div className="min-h-screen bg-[#030614] p-8 pt-24 relative overflow-hidden animate-fadeIn">
      {/* Background effects (same as lawyer dashboard) */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[#9333EA]/20 rounded-full blur-[128px] animate-fadeInSlow"></div>
        <div className="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-[#7E22CE]/20 rounded-full blur-[96px] animate-fadeInSlow delay-300"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-[#6B21A8]/20 rounded-full blur-[64px] animate-fadeInSlow delay-500"></div>
      </div>

      {/* Header */}
      <div className="mb-8 animate-fadeIn relative z-10">
        <h1 className="text-3xl font-bold text-white">
          Welcome, {' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 typewriter">
            {displayName}
          </span>
        </h1>
        <p className="text-gray-400">System Overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 relative z-10">
        {[
          { icon: <FaUserTie />, title: "Total Lawyers", value: stats.totalLawyers, delay: "delay-300" },
          { icon: <FaUsers />, title: "Total Clients", value: stats.totalClients, delay: "delay-400" },
          { icon: <FaChartBar />, title: "Active Subscriptions", value: stats.activeSubscriptions, delay: "delay-500" },
          { icon: <FaExclamationTriangle />, title: "Pending Approvals", value: stats.pendingApprovals, delay: "delay-600" }
        ].map((stat, index) => (
          <div key={index} className={`opacity-0 animate-slideInUp ${stat.delay}`}>
            <StatCard {...stat} />
          </div>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 relative z-10">
        {/* Lawyers Panel */}
        <div className="bg-gradient-to-b from-[#1A1A2E] to-[#15152d] rounded-lg p-[1px]
          border border-[#9333EA]/20 animate-[slideInLeft_0.7s_ease-out_forwards]">
          <div className="bg-[#1A1A2E]/95 rounded-lg p-6 h-full backdrop-blur-sm
            hover:shadow-[0_0_30px_rgba(147,51,234,0.2)] transition-all duration-300">
            <h2 className="text-xl font-semibold mb-4 text-white">Lawyer Management</h2>
            <div className="space-y-4">
              {lawyers.map((lawyer, index) => (
                <LawyerItem 
                  key={lawyer.id}
                  lawyer={lawyer}
                  onApprove={() => handleApproval(lawyer.id, 'approved')}
                  onReject={() => handleApproval(lawyer.id, 'rejected')}
                  className={`animate-[fadeIn_0.3s_ease-out_forwards] delay-${300 + (index * 100)}`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Clients Panel */}
        <div className="bg-gradient-to-b from-[#1A1A2E] to-[#15152d] rounded-lg p-[1px]
          border border-[#9333EA]/20 animate-[slideInRight_0.7s_ease-out_forwards]">
          <div className="bg-[#1A1A2E]/95 rounded-lg p-6 h-full backdrop-blur-sm
            hover:shadow-[0_0_30px_rgba(147,51,234,0.2)] transition-all duration-300">
            <h2 className="text-xl font-semibold mb-4 text-white">Client Activity</h2>
            <div className="space-y-4">
              {clients.map((client, index) => (
                <ClientItem 
                  key={client.id}
                  client={client}
                  className={`animate-[fadeIn_0.3s_ease-out_forwards] delay-${300 + (index * 100)}`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Reuse the same styles from lawyer dashboard */}
      <style jsx>{`
        // ... existing styles from lawyer dashboard ...
      `}</style>
    </div>
  );
};

const StatCard = ({ icon, title, value }) => (
  <div className="group relative transition-all duration-300 hover:scale-105">
    <div className="absolute -inset-0.5 bg-gradient-to-r from-[#9333EA] to-[#7E22CE] rounded-lg blur opacity-30 group-hover:opacity-70 transition duration-500"></div>
    <div className="relative bg-[#1A1A2E] rounded-lg p-4 
      transform transition-all duration-300 
      hover:scale-105 hover:shadow-[0_0_30px_rgba(147,51,234,0.3)]
      border border-[#9333EA]/20">
      <div className="text-[#9333EA] text-2xl group-hover:scale-110 transition-transform duration-300">{icon}</div>
      <h3 className="text-gray-400 text-sm mt-2">{title}</h3>
      <p className="text-2xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-white to-purple-500">{value}</p>
    </div>
  </div>
);

const LawyerItem = ({ lawyer, onApprove, onReject, className }) => (
  <div className={`flex items-center justify-between p-4 bg-[#2E2E3A] rounded-lg 
    transform transition-all duration-300
    hover:bg-[#3E3E4A] hover:scale-[1.02] 
    hover:shadow-[0_0_15px_rgba(147,51,234,0.2)]
    border border-[#9333EA]/20
    ${className}`}>
    <div>
      <p className="font-medium text-white">{lawyer.name}</p>
      <p className="text-sm text-gray-400">{lawyer.specialization}</p>
    </div>
    {lawyer.status === 'pending' && (
      <div className="flex gap-2">
        <button onClick={onApprove} className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition">
          Approve
        </button>
        <button onClick={onReject} className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition">
          Reject
        </button>
      </div>
    )}
  </div>
);

const ClientItem = ({ client, className }) => (
  <div className={`flex items-center justify-between p-4 bg-[#2E2E3A] rounded-lg 
    transform transition-all duration-300
    hover:bg-[#3E3E4A] hover:scale-[1.02] 
    hover:shadow-[0_0_15px_rgba(147,51,234,0.2)]
    border border-[#9333EA]/20
    ${className}`}>
    <div>
      <p className="font-medium text-white">{client.name}</p>
      <p className="text-sm text-gray-400">Last Active: {client.lastActive}</p>
    </div>
    <div className="text-sm text-gray-400">
      Cases: {client.totalCases}
    </div>
  </div>
);

export default AdminDashboard;
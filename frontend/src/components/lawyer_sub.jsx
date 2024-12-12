import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const LawyerSubscription = () => {
  const [isSelected, setIsSelected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [error, setError] = useState(null);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const checkSubscription = async () => {
      try {
        const subscription = await apiService.getCurrentSubscription();
        setIsSubscribed(!!subscription);
      } catch (err) {
        console.error('Error checking subscription:', err);
      }
    };
    checkSubscription();
  }, []);

  const handleSubscribe = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const startDate = new Date();
      const endDate = new Date();
      endDate.setMonth(endDate.getMonth() + 1); // Add 1 month

      await apiService.createSubscription({
        plan: 'premium',
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        amount: 1000
      });

      setShowPopup(true);
      setTimeout(() => {
        setShowPopup(false);
        navigate('/lawyer-profile');
      }, 3000);
    } catch (err) {
      setError(err.message);
      setTimeout(() => setError(null), 5000);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto relative">
      <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">Lawyer Subscription Plan</h2>
      <div className="flex justify-center">
        <div className={`w-[320px] p-6 rounded-xl shadow-lg bg-white transform transition-transform hover:-translate-y-2 
            ${isSelected ? 'ring-2 ring-purple-500' : ''}`}>
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">Premium Plan</h3>
          <div className="text-4xl font-bold text-purple-600 mb-6">Rs. 1000/month</div>
          <ul className="space-y-3 mb-8">
            {[
              'Profile Listing on Platform',
              'Client Case Matching',
              'Direct Client Communication',
              'Document Management Tools',
              'Priority Support',
              'Analytics Dashboard'
            ].map((feature, index) => (
              <li key={index} className="flex items-center text-gray-600">
                <svg className="w-5 h-5 text-purple-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
                {feature}
              </li>
            ))}
          </ul>
          <button
            onClick={handleSubscribe}
            disabled={isLoading || isSubscribed}
            className={`w-full py-3 px-4 ${
              isSubscribed ? 'bg-green-600' : 'bg-purple-600 hover:bg-purple-700'
            } text-white font-semibold rounded-lg transition-colors flex items-center justify-center`}
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
            ) : isSubscribed ? "You are Subscribed 🙌" : "Subscribe Now"}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Success Popup */}
      {showPopup && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl transform animate-bounce">
            <h3 className="text-2xl font-bold text-purple-600 mb-2">Congratulations! 🎉</h3>
            <p className="text-gray-600">Your subscription is activated</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LawyerSubscription;

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const SubscriptionPlans = () => {
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSelectPlan = async (plan) => {
    try {
      setIsLoading(true);
      setError(null);
  
      const startDate = new Date();      
      const endDate = new Date();
      endDate.setMonth(endDate.getMonth() + (plan === 'basic' ? 1 : 0)); // 1 month for basic plan

      const subscriptionData = {
        plan: plan,
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        amount: plan === 'basic' ? 50 : 5 // 500 for basic, 0 for free plan
      };

      await apiService.createSubscription(subscriptionData);
      
      setShowPopup(true);
      setTimeout(() => {
        setShowPopup(false);
        navigate('/user-home');
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
      <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">Choose Your Subscription Plan</h2>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <div className="flex flex-wrap justify-center gap-8">
        {/* Free Plan */}
        <div className={`w-[320px] p-6 rounded-xl shadow-lg bg-white transform transition-transform hover:-translate-y-2 
            ${selectedPlan === 'free' ? 'ring-2 ring-blue-500' : ''}`}>
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">Free Plan</h3>
          <div className="text-4xl font-bold text-blue-600 mb-6">Rs. 0/month</div>
          <ul className="space-y-3 mb-8">
            {['5 AI Chat Credits', 'Basic Legal Assistance', 'Limited Access to Resources'].map((feature, index) => (
              <li key={index} className="flex items-center text-gray-600">
                <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
                {feature}
              </li>
            ))}
          </ul>
          <button
            onClick={() => handleSelectPlan('free')}
            disabled={isLoading}
            className={`w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg 
              hover:bg-blue-700 transition-colors flex items-center justify-center
              ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isLoading && selectedPlan === 'free' ? (
              <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
            ) : "Select Free Plan"}
          </button>
        </div>

        {/* Basic Plan */}
        <div className={`w-[320px] p-6 rounded-xl shadow-lg bg-white transform transition-transform hover:-translate-y-2 
            ${selectedPlan === 'basic' ? 'ring-2 ring-green-500' : ''}`}>
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">Basic Plan</h3>
          <div className="text-4xl font-bold text-green-600 mb-6">Rs. 500/month</div>
          <ul className="space-y-3 mb-8">
            {[
              '50 AI Chat Credits',
              'Priority Legal Assistance',
              'Full Access to Resources',
              'Direct Lawyer Recommendations'
            ].map((feature, index) => (
              <li key={index} className="flex items-center text-gray-600">
                <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
                {feature}
              </li>
            ))}
          </ul>
          <button
            onClick={() => handleSelectPlan('basic')}
            disabled={isLoading}
            className="w-full py-3 px-4 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center"
          >
            {isLoading && selectedPlan === 'basic' ? (
              <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
            ) : "Select Basic Plan"}
          </button>
        </div>
      </div>

      {/* Success Popup */}
      {showPopup && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl transform animate-bounce">
            <h3 className="text-2xl font-bold text-blue-600 mb-2">Congratulations! 🎉</h3>
            <p className="text-gray-600">Your subscription is activated</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SubscriptionPlans;

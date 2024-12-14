import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { Sparkles, Check } from 'lucide-react';

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
      //  I want free plan to renew after every day and the credits to be reset to 5
      if (plan === 'free') {
        endDate.setDate(endDate.getDate() + 3);
      }      
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
    <div className="min-h-screen bg-[#030614] pt-24 pb-8 px-4 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[#9333EA]/20 rounded-full blur-[128px] animate-fadeInSlow"></div>
        <div className="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-[#7E22CE]/20 rounded-full blur-[96px] animate-fadeInSlow delay-300"></div>
        <div className="absolute bottom-1/4 left-1/2 w-[300px] h-[300px] bg-[#6B21A8]/20 rounded-full blur-[64px] animate-fadeInSlow delay-500"></div>
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        <h2 className="text-4xl font-bold text-center text-white mb-4">Choose Your Plan</h2>
        <p className="text-gray-400 text-center mb-12">Select the perfect plan for your legal needs</p>

        {error && (
          <div className="mb-8 p-4 bg-red-900/20 border border-red-800 text-red-400 rounded-lg backdrop-blur-sm">
            {error}
          </div>
        )}

        <div className="flex flex-wrap justify-center gap-8">
          {/* Free Plan */}
          <div className={`w-[320px] backdrop-blur-sm bg-[#1A1A2E]/95 border-2 ${
            selectedPlan === 'free' 
              ? 'border-[#9333EA]' 
              : 'border-[#9333EA]/20'
            } rounded-xl transform transition-all duration-300 hover:scale-105 
            hover:shadow-[0_0_30px_rgba(147,51,234,0.2)]`}>
            <div className="p-8">
              <div className="flex items-center gap-3 mb-4">
                <Sparkles className="h-6 w-6 text-[#9333EA]" />
                <h3 className="text-2xl font-semibold text-white">Free Plan</h3>
              </div>
              <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#9333EA] to-[#7E22CE] mb-6">
                Rs. 0
              </div>
              <ul className="space-y-4 mb-8">
                {['3 days free', 'Basic Legal Assistance', 'Limited Access to Resources', 'Free References'].map((feature, index) => (
                  <li key={index} className="flex items-center text-gray-300">
                    <Check className="h-5 w-5 text-[#9333EA] mr-3" />
                    {feature}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => handleSelectPlan('free')}
                disabled={isLoading}
                className={`w-full py-3 px-4 rounded-lg font-semibold text-white
                  ${selectedPlan === 'free'
                    ? 'bg-gradient-to-r from-[#9333EA] to-[#7E22CE]'
                    : 'bg-gradient-to-r from-[#9333EA]/80 to-[#7E22CE]/80 hover:from-[#9333EA] hover:to-[#7E22CE]'
                  } transition-all duration-300 flex items-center justify-center`}
              >
                {isLoading && selectedPlan === 'free' ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-b-transparent border-white"></div>
                ) : "Start Free Trial"}
              </button>
            </div>
          </div>

          {/* Basic Plan */}
          <div className={`w-[320px] backdrop-blur-sm bg-[#1A1A2E]/95 border-2 ${
            selectedPlan === 'basic' 
              ? 'border-[#9333EA]' 
              : 'border-[#9333EA]/20'
            } rounded-xl transform transition-all duration-300 hover:scale-105
            hover:shadow-[0_0_30px_rgba(147,51,234,0.2)]`}>
            <div className="p-8">
              <div className="flex items-center gap-3 mb-4">
                <Sparkles className="h-6 w-6 text-[#9333EA]" />
                <h3 className="text-2xl font-semibold text-white">Basic Plan</h3>
              </div>
              <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#9333EA] to-[#7E22CE] mb-6">
                Rs. 500<span className="text-lg text-gray-400">/month</span>
              </div>
              <ul className="space-y-4 mb-8">
                {[
                  '500 AI Chat Credits',
                  'Priority Legal Assistance',
                  'Full Access to Resources',
                  'Direct Lawyer Recommendations'
                ].map((feature, index) => (
                  <li key={index} className="flex items-center text-gray-300">
                    <Check className="h-5 w-5 text-[#9333EA] mr-3" />
                    {feature}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => handleSelectPlan('basic')}
                disabled={isLoading}
                className={`w-full py-3 px-4 rounded-lg font-semibold text-white
                  ${selectedPlan === 'basic'
                    ? 'bg-gradient-to-r from-[#9333EA] to-[#7E22CE]'
                    : 'bg-gradient-to-r from-[#9333EA]/80 to-[#7E22CE]/80 hover:from-[#9333EA] hover:to-[#7E22CE]'
                  } transition-all duration-300 flex items-center justify-center`}
              >
                {isLoading && selectedPlan === 'basic' ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-b-transparent border-white"></div>
                ) : "Select Basic Plan"}
              </button>
            </div>
          </div>
        </div>

        {/* Success Popup */}
        {showPopup && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
            <div className="bg-[#1A1A2E] p-8 rounded-xl border border-[#9333EA]/20 shadow-[0_0_30px_rgba(147,51,234,0.2)] transform animate-popup">
              <div className="flex items-center gap-3 mb-4">
                <Sparkles className="h-6 w-6 text-[#9333EA]" />
                <h3 className="text-2xl font-bold text-white">Congratulations! 🎉</h3>
              </div>
              <p className="text-gray-300">Your subscription has been activated successfully.</p>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes popup {
          0% { opacity: 0; transform: scale(0.9); }
          100% { opacity: 1; transform: scale(1); }
        }

        @keyframes fadeInSlow {
          0% { opacity: 0; transform: scale(0.9); }
          100% { opacity: 1; transform: scale(1); }
        }

        .animate-popup {
          animation: popup 0.3s ease-out forwards;
        }

        .animate-fadeInSlow {
          animation: fadeInSlow 1.2s ease-out forwards;
        }

        .delay-300 {
          animation-delay: 300ms;
        }

        .delay-500 {
          animation-delay: 500ms;
        }
      `}</style>
    </div>
  );
};

export default SubscriptionPlans;

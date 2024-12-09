import React, { useState } from 'react';
import { apiService } from '../services/api';
import { useNavigate } from 'react-router-dom';

const LawyerProfile = () => {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    cnic: '',
    licenseNumber: '',
    location: '',
    experience: '',
    specialization: '',
    contact: '',
    email: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Validate form data before sending
      if (!formData.cnic || formData.cnic.length !== 13 || !/^\d+$/.test(formData.cnic)) {
        throw new Error('CNIC must be 13 digits');
      }

      if (!formData.email || !formData.email.includes('@')) {
        throw new Error('Please enter a valid email address');
      }

      if (parseInt(formData.experience) < 0) {
        throw new Error('Experience must be a positive number');
      }

      const response = await apiService.createLawyerProfile(formData);
      console.log('Profile created successfully:', response);
      navigate('/dashboard');
    } catch (err) {
      console.error('Profile creation error:', err);
      setError(
        err.response?.data?.error || 
        err.message || 
        'Failed to create lawyer profile'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg mt-10">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Lawyer Profile</h2>
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        {[
          { label: 'CNIC', name: 'cnic', type: 'text' },
          { label: 'License Number', name: 'licenseNumber', type: 'text' },
          { label: 'Location', name: 'location', type: 'text' },
          { label: 'Experience (years)', name: 'experience', type: 'number' },
          { label: 'Specialization', name: 'specialization', type: 'text' },
          { label: 'Contact', name: 'contact', type: 'tel' },
          { label: 'Email', name: 'email', type: 'email' }
        ].map((field) => (
          <div key={field.name} className="flex flex-col">
            <label htmlFor={field.name} className="text-sm font-medium text-gray-700 mb-1">
              {field.label}:
            </label>
            <input
              type={field.type}
              id={field.name}
              name={field.name}
              value={formData[field.name]}
              onChange={handleChange}
              required
              className="p-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        ))}

        <button
          type="submit"
          disabled={loading}
          className={`w-full py-2 px-4 rounded-md transition-colors duration-200 
            ${loading 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-indigo-600 hover:bg-indigo-700 text-white'}`}
        >
          {loading ? 'Creating Profile...' : 'Submit'}
        </button>
      </form>
    </div>
  );
};

export default LawyerProfile;

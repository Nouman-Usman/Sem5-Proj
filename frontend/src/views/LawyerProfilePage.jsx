import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card } from "@/components/ui/card";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Star, MapPin, Mail, Phone, Award, BookOpen, Calendar, Users } from 'lucide-react';
import apiService from '@/services/api';

export default function LawyerProfilePage() {
  const { id } = useParams();
  const [lawyer, setLawyer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLawyerProfile = async () => {
      try {
        setLoading(true);
        const response = await apiService.getLawyerDeatilsbyLawyerId(id);
        if (response?.lawyer) {
          setLawyer(response.lawyer);
        }
      } catch (err) {
        setError('Failed to load lawyer profile');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchLawyerProfile();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#030614] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  if (error || !lawyer) {
    return (
      <div className="min-h-screen bg-[#030614] flex items-center justify-center">
        <div className="text-white text-center">
          <h2 className="text-xl font-semibold mb-2">Error</h2>
          <p className="text-gray-400">{error || 'Failed to load lawyer profile'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#030614] pt-20 p-6"> {/* Added pt-20 for navbar height */}
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <Card className="bg-[#1A1A2E]/90 border-[#9333EA]/20 p-8 mb-6 relative overflow-hidden">
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#9333EA]/20 rounded-full blur-[128px]"></div>
          </div>
          <div className="relative z-10 flex items-start gap-8">
            <Avatar className="h-32 w-32 ring-4 ring-[#9333EA]/50">
              <AvatarImage src={lawyer.avatar} alt={lawyer.Name} />
              <AvatarFallback className="bg-[#2E2E3A] text-3xl text-white">
                {lawyer.Name?.split(' ').map(n => n[0]).join('')}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="flex justify-between items-start">
                <div>
                  <h1 className="text-3xl font-bold text-white mb-2">{lawyer.Name}</h1>
                  <p className="text-lg text-purple-400 mb-4">{lawyer.Category}</p>
                  <div className="flex items-center gap-4 text-gray-400">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      <span>{lawyer.Location}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      <span>{lawyer.Rating}/5</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>{lawyer.Experience} Years Experience</span>
                    </div>
                  </div>
                </div>
                <Button 
                  className="bg-gradient-to-r from-[#9333EA] to-[#7E22CE] text-white px-6"
                  onClick={() => {/* Handle contact */}}
                >
                  Appoint Now
                </Button>
              </div>
            </div>
          </div>
        </Card>

        {/* Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Contact Information */}
          <Card className="bg-[#1A1A2E]/90 border-[#9333EA]/20 p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Contact Information</h2>
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-gray-300">
                <Mail className="h-5 w-5 text-purple-400" />
                <span>{lawyer.Email}</span>
              </div>
              <div className="flex items-center gap-3 text-gray-300">
                <Phone className="h-5 w-5 text-purple-400" />
                <span>{lawyer.Contact}</span>
              </div>
            </div>
          </Card>

          {/* Specializations */}
          <Card className="bg-[#1A1A2E]/90 border-[#9333EA]/20 p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Specializations</h2>
            <div className="flex flex-wrap gap-2">
              {lawyer.Category?.split(',').map((specialization, index) => (
                <span 
                  key={index}
                  className="px-3 py-1 rounded-full bg-[#9333EA]/20 text-purple-400 text-sm"
                >
                  {specialization.trim()}
                </span>
              ))}
            </div>
          </Card>

          {/* Experience Details */}
          <Card className="bg-[#1A1A2E]/90 border-[#9333EA]/20 p-6 md:col-span-2">
            <h2 className="text-xl font-semibold text-white mb-4">Experience & Expertise</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-full bg-[#9333EA]/20 flex items-center justify-center">
                  <Award className="h-6 w-6 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-white font-medium">{lawyer.Experience} Years</h3>
                  <p className="text-gray-400 text-sm">Professional Experience</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-full bg-[#9333EA]/20 flex items-center justify-center">
                  <BookOpen className="h-6 w-6 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-white font-medium">{lawyer.Rating}/5</h3>
                  <p className="text-gray-400 text-sm">Client Rating</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-full bg-[#9333EA]/20 flex items-center justify-center">
                  <Users className="h-6 w-6 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-white font-medium">100+</h3>
                  <p className="text-gray-400 text-sm">Clients Served</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

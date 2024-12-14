import React, { useState, useEffect } from "react"
import { Menu as MenuIcon, X, ChevronDown, User, LogIn, LogOut, Settings } from "lucide-react"
import { Menu } from "@headlessui/react"
import {authService} from "@/services/auth"

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 0)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navbarClasses = `w-full transition-all duration-200 ${
    scrolled ? 'bg-[#030014]/70 backdrop-blur-lg border-b border-white/10' : 'bg-transparent'
  }`

  const linkClasses = "text-white/80 hover:text-white transition-colors duration-200 px-3 py-2 rounded-md text-sm font-medium relative hover:before:content-[''] hover:before:absolute hover:before:inset-0 hover:before:bg-gradient-to-b hover:before:from-white/[0.09] hover:before:to-transparent hover:before:rounded-md"

  return (
    <nav className={navbarClasses}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <img
                className="h-8 w-auto"
                src="/placeholder.svg?height=32&width=32"
                alt="Apna Waqeel Logo" />
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <a href="/" className={linkClasses}>Home</a>
                <a href="/chatbot" className={linkClasses}>Chatbot</a>
                <a href="/lawyers" className={linkClasses}>Explore Lawyers</a>
              </div>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="ml-4 flex items-center md:ml-6">
              <Menu as="div" className="relative ml-3">
                <Menu.Button className="flex items-center text-white/80 hover:text-white transition-colors duration-200 rounded-full focus:outline-none">
                  <User className="h-6 w-6" />
                  <ChevronDown className="ml-1 h-4 w-4" />
                </Menu.Button>
                <Menu.Items
                  className="absolute right-0 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                  {/* <Menu.Item>
                    {({ active }) => (
                      <a href="/Login" className={`${active ? 'bg-white/[0.09]' : ''} flex items-center px-4 py-2 text-sm text-white/80 hover:text-white transition-colors duration-200`}>
                        <LogIn className="mr-2 h-4 w-4" />
                        Login
                      </a>
                    )}
                  </Menu.Item> */}
                  <Menu.Item>
                    {({ active }) => (
                      <a
                        href="/Signup"
                        className={`${
                          active ? "bg-gray-100" : ""
                        } flex items-center px-4 py-2 text-sm text-gray-700`}
                        onClick={authService.logout}
                        >
                        <LogOut className="mr-2 h-4 w-4" />
                        Logout
                      </a>
                    )}
                  </Menu.Item>
                  <Menu.Item>
                    {({ active }) => (
                      <a
                        href="/Account-settings"
                        className={`${
                          active ? "bg-gray-100" : ""
                        } flex items-center px-4 py-2 text-sm text-gray-700`}>
                        <Settings className="mr-2 h-4 w-4" />
                        Account Settings
                      </a>
                    )}
                  </Menu.Item>
                </Menu.Items>
              </Menu>
            </div>
          </div>
          <div className="-mr-2 flex md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-white/80 hover:text-white transition-colors duration-200 p-2 rounded-md hover:bg-white/[0.09]">
              <span className="sr-only">Open main menu</span>
              {!isOpen ? (
                <MenuIcon className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <X className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>
      {isOpen && (
        <div className="md:hidden bg-[#030014]/90 backdrop-blur-lg" id="mobile-menu">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <a href="/" className={linkClasses}>Home</a>
            <a href="/chatbot" className={linkClasses}>Chatbot</a>
            <a href="/Lawyers" className={linkClasses}>Explore Lawyers</a>
          </div>
          <div className="pt-4 pb-3 border-t border-white/10">
            <div className="flex items-center px-5">
              <div className="flex-shrink-0">
                <User className="h-10 w-10 text-gray-800" />
              </div>
              <div className="ml-3">
                <div className="text-base font-medium leading-none text-gray-800">Account</div>
              </div>
            </div>
            <div className="mt-3 px-2 space-y-1">
              {/* <a
                href="#"
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-800 hover:bg-gray-200">Login</a> */}
              <a
                href="#"
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-800 hover:bg-gray-200" onClick={authService.logout}>Logout</a>
              <a
                href="#"
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-800 hover:bg-gray-200">Account Settings</a>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
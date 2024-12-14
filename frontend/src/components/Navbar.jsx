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

  const navbarClasses = `
    w-full 
    transition-all duration-300 
    ${scrolled 
      ? 'bg-white/10 backdrop-blur-md border-b border-white/20' 
      : 'bg-transparent'
    }
    fixed top-0 z-50
    before:absolute before:w-full before:h-full before:backdrop-blur-sm
    before:rounded-[50px] before:-z-10 before:content-['']
    after:absolute after:w-full after:h-[1px] after:top-0 
    after:bg-gradient-to-r after:from-transparent after:via-white/20 after:to-transparent
    after:animate-glow
  `

  const linkClasses = `
    text-white/90 hover:text-white 
    transition-all duration-300 
    px-4 py-2 rounded-full 
    text-sm font-medium relative 
    hover:bg-white/10 
    hover:shadow-[0_0_15px_rgba(255,255,255,0.1)]
    group
  `

  return (
    <nav className={navbarClasses}>
      <div className="max-w-7xl mx-auto px-6 sm:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <div className="flex-shrink-0">
            <img
              className="h-12 w-auto" // Increase the height to 12
              src="/src/assets/Main logo.svg"
              alt="Apna Waqeel Logo" 
            />
          </div>

          {/* Centered Navigation Items */}
          <div className="hidden md:flex flex-1 justify-center">
            <div className="flex items-baseline space-x-6">
              <a href="/" className={linkClasses}>
                <span className="relative z-10">Home</span>
              </a>
              <a href="/chatbot" className={linkClasses}>
                <span className="relative z-10">Chatbot</span>
              </a>
              <a href="/lawyers" className={linkClasses}>
                <span className="relative z-10">Explore Lawyers</span>
              </a>
            </div>
          </div>

          {/* User Menu */}
          <div className="hidden md:block">
            <div className="flex items-center">
              <Menu as="div" className="relative">
                <Menu.Button className="
                  flex items-center 
                  text-white/90 hover:text-white 
                  transition-all duration-300 
                  px-4 py-2 rounded-full 
                  hover:bg-white/10
                  hover:shadow-[0_0_15px_rgba(255,255,255,0.1)]
                ">
                  <User className="h-5 w-5" />
                  <ChevronDown className="ml-1 h-4 w-4" />
                </Menu.Button>
                <Menu.Items className="
                  absolute right-0 mt-2 w-48 
                  origin-top-right rounded-2xl 
                  bg-white/10 backdrop-blur-lg 
                  py-2 px-1
                  shadow-[0_0_15px_rgba(255,255,255,0.1)]
                  border border-white/20
                ">
                  <Menu.Item>
                    {({ active }) => (
                      <a href="/Login" className={`
                        ${active ? 'bg-white/10' : ''} 
                        flex items-center px-4 py-2 
                        text-sm text-white/90 hover:text-white 
                        rounded-xl transition-all duration-300
                      `}>
                        <LogIn className="mr-2 h-4 w-4" />
                        Login
                      </a>
                    )}
                  </Menu.Item>
                  <Menu.Item>
                    {({ active }) => (
                      <a
                        href="/Signup"
                        className={`${active ? "bg-gray-100" : ""} 
                          flex items-center px-4 py-2 text-sm text-gray-700`}
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
                        className={`${active ? "bg-gray-100" : ""} 
                          flex items-center px-4 py-2 text-sm text-gray-700`}
                      >
                        <Settings className="mr-2 h-4 w-4" />
                        Account Settings
                      </a>
                    )}
                  </Menu.Item>
                </Menu.Items>
              </Menu>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="
                text-white/90 hover:text-white 
                transition-all duration-300 
                p-2 rounded-full
                hover:bg-white/10
                hover:shadow-[0_0_15px_rgba(255,255,255,0.1)]
              ">
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

      {/* Mobile menu */}
      {isOpen && (
        <div className="
          md:hidden 
          bg-white/10 backdrop-blur-lg
          border-t border-white/20
          rounded-b-[50px]
        ">
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
              <a
                href="#"
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-800 hover:bg-gray-200"
              >
                Logout
              </a>
              <a
                href="#"
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-800 hover:bg-gray-200"
              >
                Account Settings
              </a>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
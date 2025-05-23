// components/layout/Header.tsx
import React from 'react';
import Link from 'next/link';

interface HeaderProps {
  // Nessuna prop necessaria per ora
}

export default function Header({}: HeaderProps) {
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-emerald-600">Transizione 5.0</h1>
          <span className="text-sm text-gray-500">by DIRATEC SRL</span>
        </div>
        <nav className="hidden md:flex space-x-6">
          <Link href="/" className="text-gray-800 hover:text-emerald-600 font-medium">Home</Link>
          <Link href="/docs" className="text-gray-600 hover:text-emerald-600">Documenti</Link>
          <Link href="#contatti" className="text-gray-600 hover:text-emerald-600 scroll-smooth">Contatti</Link>
          <Link href="/admin" className="text-gray-600 hover:text-emerald-600">Area Riservata</Link>
        </nav>
        <div className="md:hidden">
          {/* Menu mobile */}
          <button className="p-2 rounded-md text-gray-600 hover:text-emerald-600 hover:bg-gray-100">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
// components/layout/header.tsx - Versione Corretta
import React from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function Header() {
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          {/* Logo principale Transizione 5.0 - PIÙ GRANDE */}
          <Image
            src="/logos/transizione5-logo.svg"
            alt="Transizione 5.0"
            width={61}
            height={72}
            //className="h-11 w-auto"
          />
          <div>
            <h1 className="text-2xl font-bold text-emerald-600">Transizione 5.0</h1>
            {/* SOLO TESTO - NESSUN LOGO DIRATEC */}
            <div className="text-xs text-gray-500">
              powered by DIRATEC SRL
            </div>
          </div>
        </div>
        
        {/* Menu aggiornato senza Area Riservata */}
        <nav className="hidden md:flex space-x-6">
          <Link href="/" className="text-gray-800 hover:text-emerald-600 font-medium">Home</Link>
          <Link href="/certificazioni" className="text-gray-600 hover:text-emerald-600">Certificazioni</Link>
          <Link href="/chi-siamo" className="text-gray-600 hover:text-emerald-600">Chi Siamo</Link>
          <Link href="/docs" className="text-gray-600 hover:text-emerald-600">Documenti</Link>
          <Link href="#contatti" className="text-gray-600 hover:text-emerald-600">Contatti</Link>
        </nav>
        
        <div className="md:hidden">
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
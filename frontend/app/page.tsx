// app/page.tsx
import Header from '@/components/layout/header';
import Footer from '@/components/layout/footer';
import HeroSection from '@/components/sections/hero-section';
import BenefitsTable from '@/components/sections/benefits-table';
import ChatSection from '@/components/sections/chat-section';
import ProcessSection from '@/components/sections/process-section';
import ContactSection from '@/components/sections/contact-section';

export default function HomePage() {
  return (
    <div className="bg-gray-50 min-h-screen">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <HeroSection />
        <BenefitsTable />
        <ChatSection />
        <ProcessSection />
      </main>
      <ContactSection />
      <Footer />
    </div>
  );
}
// components/Chat/TypewriterEffect.tsx - versione corretta
import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

interface TypewriterEffectProps {
  content: string;
  isComplete: boolean;
  speed?: number;
  onContentUpdate?: () => void;
}

const TypewriterEffect: React.FC<TypewriterEffectProps> = ({ 
  content, 
  isComplete,
  speed = 20,
  onContentUpdate
}) => {
  const [displayedContent, setDisplayedContent] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const contentRef = useRef(content);
  const charIndexRef = useRef(0);
  const typingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Funzione per pulire il contenuto HTML e convertirlo in markdown
  const cleanContent = (rawContent: string): string => {
    return rawContent
      // Sostituisce <br> e <br /> con newline
      .replace(/<br\s*\/?>/gi, '\n')
      // Rimuove altri tag HTML comuni mantenendo il contenuto
      .replace(/<\/?p>/gi, '\n')
      .replace(/<\/?div>/gi, '\n')
      .replace(/<\/?span[^>]*>/gi, '')
      // Pulisce newline multiple
      .replace(/\n{3,}/g, '\n\n')
      .trim();
  };

  // Avvio l'effetto quando arriva nuovo contenuto
  useEffect(() => {
    // Pulisce il contenuto prima di processarlo
    const cleanedContent = cleanContent(content);
    
    // Forza l'avvio dell'animazione quando arriva nuovo contenuto
    if (cleanedContent && cleanedContent !== contentRef.current) {
      console.log('Nuovo contenuto rilevato, avvio animazione');
      contentRef.current = cleanedContent;
      charIndexRef.current = 0;
      setDisplayedContent('');
      
      // Avvia sempre l'animazione quando c'è nuovo contenuto
      startTypingAnimation();
    }
    
    // Gestione completamento
    if (isComplete && displayedContent !== cleanedContent) {
      console.log('Streaming completato, mostro contenuto completo');
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
        typingIntervalRef.current = null;
      }
      setDisplayedContent(cleanedContent);
      setIsTyping(false);
      
      if (onContentUpdate) onContentUpdate();
    }
    
    return () => {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
      }
    };
  }, [content, isComplete]);

  const startTypingAnimation = () => {
    console.log('Avvio animazione di digitazione');
    setIsTyping(true);
    
    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
    }
    
    typingIntervalRef.current = setInterval(() => {
      if (charIndexRef.current < contentRef.current.length) {
        charIndexRef.current += 1;
        const newDisplayedContent = contentRef.current.substring(0, charIndexRef.current);
        setDisplayedContent(newDisplayedContent);
        
        if (onContentUpdate) onContentUpdate();
      } else {
        clearInterval(typingIntervalRef.current as NodeJS.Timeout);
        typingIntervalRef.current = null;
        setIsTyping(false);
      }
    }, speed);
  };

  return (
    <div className="typewriter-container">
      <ReactMarkdown
        components={{
          // Personalizza il rendering di alcuni elementi se necessario
          p: ({ children }) => <p className="mb-2">{children}</p>,
          ul: ({ children }) => <ul className="list-disc ml-4 mb-2">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal ml-4 mb-2">{children}</ol>,
          li: ({ children }) => <li className="mb-1">{children}</li>,
        }}
      >
        {displayedContent}
      </ReactMarkdown>
      
      {isTyping && (
        <span className="cursor-typing"></span>
      )}
    </div>
  );
};

export default TypewriterEffect;
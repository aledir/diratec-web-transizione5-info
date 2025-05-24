// components/chat/chat-message.tsx
import { useRef } from 'react';
import TypewriterEffect from './typewriter-effect';
import useSharedConfig from '../../hooks/use-shared-config';
import ThinkingIndicator from './thinking-indicator';
import styles from './chat.module.css'; // ✅ IMPORT CORRETTO

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  isThinking?: boolean;
}

interface ChatMessageProps {
  message: Message;
  onUpdate?: () => void;
}

export default function ChatMessage({ message, onUpdate }: ChatMessageProps) {
  const { config } = useSharedConfig();
  const messageRef = useRef<HTMLDivElement>(null);
  
  // Stili condizionali in base al mittente
  const messageStyles = message.role === 'user'
    ? 'bg-blue-50 border-blue-200 ml-auto'
    : 'bg-gray-50 border-gray-200 mr-auto';
  
  // Nome da visualizzare per l'assistente, con fallback
  const assistantName = config?.assistant?.displayName || "Quinto";
  
  return (
    <div 
      ref={messageRef} 
      className={`max-w-[85%] rounded-lg border p-3 ${messageStyles} relative`}
    >
      {/* Mostra l'etichetta solo per i messaggi dell'utente */}
      {message.role === 'user' && (
        <div className="text-xs text-gray-500 mb-1">
          Tu
        </div>
      )}
      
      <div className="prose prose-sm max-w-none markdown-content">
        {message.role === 'assistant' && message.isThinking ? (
          // Per i messaggi "thinking" mostriamo il ThinkingIndicator
          <div className={styles.thinkingWrapper}>
            <ThinkingIndicator />
          </div>
        ) : message.role === 'assistant' ? (
          // Per i messaggi normali dell'assistente, mostriamo solo il contenuto
          // Il nome e l'avatar sono già gestiti nel ThinkingIndicator quando necessario
          <TypewriterEffect 
            content={message.content}
            isComplete={!message.isStreaming}
            speed={20}
            onContentUpdate={onUpdate}
          />
        ) : (
          // Per i messaggi dell'utente, contenuto semplice
          <div>{message.content}</div>
        )}
      </div>
    </div>
  );
}
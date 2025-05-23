// frontend/components/Chat/ChatInput.tsx
import React, { useState } from 'react';
import styles from './chat.module.css';

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  disabled = false,
  placeholder = "Scrivi un messaggio..."
}) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.inputForm}>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder={placeholder}
        className={styles.inputField}
        disabled={disabled}
      />
      <button 
        type="submit" 
        className={styles.sendButton}
        disabled={disabled || !message.trim()}
      >
        Invia
      </button>
    </form>
  );
};

export default ChatInput;
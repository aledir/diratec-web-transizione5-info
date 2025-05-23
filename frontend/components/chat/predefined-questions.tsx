// frontend/components/Chat/PredefinedQuestions.tsx
import React, { useState } from 'react';
import styles from './chat.module.css';

interface PredefinedQuestionsProps {
  questions: string[];
  onSelectQuestion: (question: string) => void;
}

const PredefinedQuestions: React.FC<PredefinedQuestionsProps> = ({ questions, onSelectQuestion }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  if (!questions || questions.length === 0) {
    return null;
  }

  return (
    <div className={styles.predefinedQuestions}>
      <div className={styles.predefinedQuestionsHeader} onClick={toggleExpanded}>
        <h3>Domande suggerite</h3>
        <span className={styles.toggleIcon}>
          {isExpanded ? '▲' : '▼'}
        </span>
      </div>
      
      {isExpanded && (
        <div className={styles.questionsList}>
          {questions.map((question, index) => (
            <button
              key={index}
              className={styles.questionButton}
              onClick={() => onSelectQuestion(question)}
            >
              {question}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default PredefinedQuestions;
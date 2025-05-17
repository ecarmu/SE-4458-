import React from 'react';
import './MessageBubble.css';

export default function MessageBubble({ message }) {
  const isUser = message.sender === 'user';
  return (
    <div className={`bubble ${isUser ? 'user' : 'bot'}`} style={{ whiteSpace: 'pre-wrap' }} >
      {message.text}
    </div>
  );
}

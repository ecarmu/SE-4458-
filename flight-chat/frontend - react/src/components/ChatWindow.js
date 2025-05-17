import React, { useState, useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import InputBox from './InputBox';
import './ChatWindow.css';
import io from 'socket.io-client';


export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const [socket, setSocket] = useState(null);

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    const sock = io(process.env.REACT_APP_SOCKET_URL);
    sock.on("connect", () => console.log("🟢 Socket connected:", sock.id));
    sock.on("disconnect", (reason) => console.warn("🟠 Socket disconnected:", reason));
    sock.on("connect_error", (err) => {
    console.error("🔴 Connect error:", err);
    setLoading(false);
    setMessages(prev => [
          ...prev,
          { sender: 'bot', text: '⚠️ Could not connect to agent.' }
        ]);
      });
    
    // sock.on("bot_message", handleReply);
    
    setSocket(sock);

    // You no longer need a persistent 'bot_message' listener here,
    // since you'll use socket.once in sendMessage.

    return () => {
      sock.disconnect();
    };
  }, []);
  

  const sendMessage = async (text) => {
    // Add user message
    setMessages(prev => [...prev, { sender: 'user', text }]);
    setLoading(true);

    socket.emit('user_message', { text });

    
    // Start a 5s timer to report an error if no bot_message comes back
    const timeoutId = setTimeout(() => {
      setLoading(false);
      setMessages(prev => [...prev, { sender: 'bot', text: 'Error: no response from agent.' }]);
    }, 5000);

    // When the bot reply fires, clear that timeout:
    socket.once('bot_message', ({ reply }) => {
      clearTimeout(timeoutId);
      setMessages(prev => [...prev, { sender: 'bot', text: reply }]);
      setLoading(false);
    });

  };

  return (
    <div className="chat-window">
      <div className="messages">
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
        {loading && <MessageBubble message={{ sender: 'bot', text: '...' }} />}
        <div ref={bottomRef} />
      </div>
      <InputBox onSend={sendMessage} disabled={loading} />
    </div>
  );
}

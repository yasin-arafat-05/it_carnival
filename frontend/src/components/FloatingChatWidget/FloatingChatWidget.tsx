import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { apiFetch, getAuthToken } from '../../config/api';
import './FloatingChatWidget.css';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
}

const FAQ_RESPONSES: Record<string, string> = {
  limits:
    '• Single Transaction Limit: BDT 20,000.00 max per transfer.\n• Daily Transfer Limit: BDT 50,000.00 per user per day.\n• Confirmation: All transfers require a 5-second press-and-hold confirmation for safety.',
  disputes:
    'False Transaction Reversal Process:\n1. Click your outgoing transfer under Transaction History ➔ "Report False Transaction".\n2. The receiver accepts or rejects the reversal request.\n3. Admin verifies and executes the atomic refund from receiver to sender.',
  request:
    'Money Requests:\n1. Go to "Money requests" ➔ enter the payer username or email.\n2. The payer receives a notification and can accept or decline the request.',
  ledger:
    'Double-Entry Ledger:\nEvery transaction generates real-time DEBIT and CREDIT audit records. View full audit logs under Transaction History ➔ Double-Entry Ledger Audit.',
};

export function FloatingChatWidget() {
  const location = useLocation();
  const token = getAuthToken();
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  if (isAuthPage || !token) {
    return null;
  }
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init_1',
      sender: 'assistant',
      text: 'Hello! I am your Digital Wallet AI Assistant. Ask me anything about transfer limits (BDT 20,000 single / 50,000 daily), false transaction reversals, or money requests!',
    },
  ]);

  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim();
    if (!query || loading) return;

    const userMsg: ChatMessage = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text: query,
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    // Smart Local Match or API Call
    let botReply = '';
    const qLower = query.toLowerCase();

    if (qLower.includes('limit') || qLower.includes('send') || qLower.includes('max')) {
      botReply = FAQ_RESPONSES.limits;
    } else if (qLower.includes('dispute') || qLower.includes('false') || qLower.includes('reversal') || qLower.includes('refund')) {
      botReply = FAQ_RESPONSES.disputes;
    } else if (qLower.includes('request') || qLower.includes('ask')) {
      botReply = FAQ_RESPONSES.request;
    } else if (qLower.includes('ledger') || qLower.includes('audit')) {
      botReply = FAQ_RESPONSES.ledger;
    } else {
      try {
        const response = await apiFetch<{ reply?: string; message?: string }>('/chat', {
          method: 'POST',
          body: JSON.stringify({ message: query, workflow_type: 'demo' }),
        });
        botReply = response.reply || response.message || 'I am here to assist with all Digital Wallet features!';
      } catch {
        botReply =
          'I am your Digital Wallet Assistant. You can ask about our BDT 20,000 single limit, BDT 50,000 daily limit, 5-second press-and-hold safety, and false transaction reversals!';
      }
    }

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: `bot_${Date.now()}`,
          sender: 'assistant',
          text: botReply,
        },
      ]);
      setLoading(false);
    }, 400);
  };

  return (
    <>
      {!isOpen && (
        <button
          className="chat-widget-fab"
          onClick={() => setIsOpen(true)}
          aria-label="Open AI Support Assistant Chat"
        >
          <span className="chat-widget-fab__icon">💬</span>
          <span>AI Support</span>
        </button>
      )}

      {isOpen && (
        <div className="chat-widget-window">
          <header className="chat-widget-header">
            <div className="chat-widget-header__title">
              <span className="online-status-dot" />
              <span>Wallet AI Support</span>
            </div>
            <button
              className="chat-widget-header__close"
              onClick={() => setIsOpen(false)}
              aria-label="Close Chat"
            >
              ✕
            </button>
          </header>

          <div className="chat-widget-body" ref={bodyRef}>
            <div className="chat-chips">
              <button className="chat-chip" onClick={() => handleSend('What are the transfer limits?')}>
                💡 Transfer limits?
              </button>
              <button className="chat-chip" onClick={() => handleSend('How do false transaction reversals work?')}>
                🔄 False Tx Reversals?
              </button>
              <button className="chat-chip" onClick={() => handleSend('How to request money from a user?')}>
                📩 Request Money?
              </button>
              <button className="chat-chip" onClick={() => handleSend('Tell me about double-entry ledger audit.')}>
                🛡️ Ledger Audit?
              </button>
            </div>

            {messages.map((msg) => (
              <div key={msg.id} className={`chat-msg chat-msg--${msg.sender}`}>
                <div className="chat-msg-bubble">{msg.text}</div>
              </div>
            ))}

            {loading && (
              <div className="chat-msg chat-msg--assistant">
                <div className="chat-msg-bubble" style={{ color: 'var(--color-text-secondary)' }}>
                  Typing answer...
                </div>
              </div>
            )}
          </div>

          <form
            className="chat-widget-footer"
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
          >
            <input
              type="text"
              className="chat-widget-input"
              placeholder="Ask a question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button type="submit" className="chat-widget-send" disabled={!input.trim() || loading}>
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}

import { useCallback, useState } from 'react';

import { sendQuery } from '../api/client';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const sendMessage = useCallback(async (question) => {
    const trimmed = question.trim();
    if (!trimmed) {
      return [];
    }

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: trimmed,
    };

    setMessages((current) => [...current, userMessage]);
    setLoading(true);
    setError('');

    try {
      const history = [...messages, userMessage].map((message) => ({
        role: message.role,
        content: message.content,
      }));
      const response = await sendQuery(trimmed, history);
      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        sql: response.sql,
        results: response.results,
        nodesReferenced: response.nodes_referenced ?? [],
        variant: 'default',
      };
      setMessages((current) => [...current, assistantMessage]);
      return assistantMessage.nodesReferenced;
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Query failed.';
      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: String(detail),
        sql: '',
        results: [],
        nodesReferenced: [],
        variant: err.response?.status === 400 ? 'guardrail' : 'error',
      };
      setMessages((current) => [...current, assistantMessage]);
      setError(String(detail));
      return [];
    } finally {
      setLoading(false);
    }
  }, [messages]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError('');
  }, []);

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearChat,
  };
}

import React, { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'system', content: 'Enterprise AI Autopilot Console. Describe a business task, and I will autonomously plan and execute it.', timestamp: new Date() },
  ]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;

    const userMsg: Message = { role: 'user', content: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsProcessing(true);

    try {
      const wfResult = await api.createWorkflow(
        `Task: ${input.slice(0, 50)}${input.length > 50 ? '...' : ''}`,
        input,
        ['ai-console']
      );

      if (wfResult.status === 'success') {
        const workflowId = wfResult.data.id;
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `✅ **Workflow Created**\n\nI've created an autonomous workflow to handle your request.\n\n**Workflow ID:** \`${workflowId}\`\n**Name:** ${wfResult.data.name}\n\nNow executing the plan...`,
          timestamp: new Date(),
        }]);

        const runResult = await api.runWorkflowSync(workflowId);
        if (runResult.status === 'success') {
          const output = runResult.data?.output?.summary || runResult.data?.output || 'Workflow completed successfully.';
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: `✅ **Workflow Completed**\n\n${output}\n\n---\n**Tokens Used:** ${runResult.data?.total_tokens || 'N/A'}`,
            timestamp: new Date(),
          }]);
        }
      }
    } catch (err: any) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ **Error**: ${err.message || 'Failed to process request'}`,
        timestamp: new Date(),
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-sm font-medium text-gray-300">AI Console</h2>
        <p className="text-xs text-gray-500 mt-1">Describe a business task, and the autopilot will handle it</p>
      </div>

      <div className="h-96 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
              msg.role === 'user'
                ? 'bg-blue-600/20 border border-blue-500/30 text-blue-200'
                : msg.role === 'system'
                ? 'bg-gray-800 text-gray-400 italic'
                : 'bg-gray-800/50 border border-gray-700 text-gray-200'
            }`}>
              <div className="whitespace-pre-wrap">{msg.content}</div>
              <div className="text-xs text-gray-500 mt-1">
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-2 text-sm text-gray-400">
              <span className="animate-pulse">Processing...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-800">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Describe a task to automate... (e.g., 'Send an email to the team about Q4 results')"
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
            disabled={isProcessing}
          />
          <button
            type="submit"
            disabled={isProcessing || !input.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-lg text-sm font-medium"
          >
            {isProcessing ? '...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
}

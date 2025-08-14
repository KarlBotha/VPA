/*
VPA Enhanced Chat Widget with Quality & UX Improvements

This module provides an enhanced chat widget with advanced UX features including:
- Real-time quality feedback
- Suggestion chips for follow-up queries
- Contextual help and tips
- Improved accessibility features
- Response quality indicators
- User satisfaction tracking
- Personalization capabilities

Author: VPA Development Team
Date: December 19, 2024
Milestone: Quality & UX Enhancements
*/

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  MessageSquare, 
  ThumbsUp, 
  ThumbsDown, 
  Star, 
  RefreshCw,
  Settings,
  HelpCircle,
  Volume2,
  VolumeX,
  Eye,
  EyeOff,
  Zap,
  Clock,
  TrendingUp,
  User,
  Bot,
  Sparkles,
  Heart,
  AlertCircle,
  CheckCircle,
  XCircle,
  MoreHorizontal,
  Send,
  Mic,
  MicOff,
  Copy,
  Download,
  Share2,
  Bookmark,
  Flag,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  Filter,
  Search,
  Calendar,
  BarChart3,
  Activity,
  Target,
  Award,
  Lightbulb,
  MessageCircle,
  Phone,
  Video,
  FileText,
  Image,
  Paperclip,
  Smile,
  Maximize2,
  Minimize2,
  X
} from 'lucide-react';

// Enhanced Message Interface
interface EnhancedMessage {
  id: string;
  content: string;
  timestamp: Date;
  isUser: boolean;
  qualityMetrics?: QualityMetrics;
  enhancements?: ResponseEnhancements;
  feedback?: UserFeedback;
  provider?: string;
  model?: string;
  responseTime?: number;
  tokens?: number;
  cost?: number;
  contextUsed?: boolean;
  ragContext?: string[];
  suggestions?: SuggestionChip[];
  accessibility?: AccessibilityFeatures;
}

interface QualityMetrics {
  relevanceScore: number;
  accuracyScore: number;
  completenessScore: number;
  clarityScore: number;
  helpfulnessScore: number;
  overallQuality: 'excellent' | 'good' | 'average' | 'poor' | 'unacceptable';
  responseTime: number;
  tokenEfficiency: number;
  contextUtilization: number;
}

interface ResponseEnhancements {
  suggestionChips: SuggestionChip[];
  contextualHelp: ContextualHelp[];
  formattingImprovements: FormattingImprovement[];
  accessibilityFeatures: AccessibilityFeatures;
}

interface SuggestionChip {
  text: string;
  action: 'query' | 'rephrase' | 'example' | 'clarify';
  priority: 'high' | 'medium' | 'low';
  icon?: string;
}

interface ContextualHelp {
  type: 'tip' | 'warning' | 'info' | 'success';
  title: string;
  content: string;
}

interface FormattingImprovement {
  type: 'code' | 'list' | 'highlight' | 'table';
  suggestion: string;
  applied: boolean;
}

interface AccessibilityFeatures {
  altText: string;
  readingTime: number;
  complexityLevel: 'low' | 'medium' | 'high';
  screenReaderFriendly: boolean;
  contrastRatio: number;
  fontSize: string;
}

interface UserFeedback {
  rating?: number;
  thumbsUp?: boolean;
  detailedFeedback?: string;
  improvementSuggestions?: string[];
  timestamp: Date;
}

interface ChatSettings {
  theme: 'light' | 'dark' | 'auto';
  fontSize: 'small' | 'medium' | 'large';
  enableAnimations: boolean;
  enableSounds: boolean;
  enableNotifications: boolean;
  enableAccessibility: boolean;
  showQualityMetrics: boolean;
  showResponseTime: boolean;
  showTokenUsage: boolean;
  showCostTracking: boolean;
  autoSuggestions: boolean;
  contextualHelp: boolean;
  voiceEnabled: boolean;
  language: string;
  personality: 'professional' | 'friendly' | 'casual' | 'technical';
}

interface UserPreferences {
  userId: string;
  settings: ChatSettings;
  favoriteQueries: string[];
  conversationHistory: EnhancedMessage[];
  qualityPreferences: {
    preferredProviders: string[];
    responseStyle: string;
    detailLevel: 'brief' | 'detailed' | 'comprehensive';
  };
}

// Enhanced Chat Widget Component
const VPAEnhancedChatWidget: React.FC = () => {
  // State Management
  const [messages, setMessages] = useState<EnhancedMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [settings, setSettings] = useState<ChatSettings>({
    theme: 'auto',
    fontSize: 'medium',
    enableAnimations: true,
    enableSounds: true,
    enableNotifications: true,
    enableAccessibility: true,
    showQualityMetrics: true,
    showResponseTime: true,
    showTokenUsage: false,
    showCostTracking: false,
    autoSuggestions: true,
    contextualHelp: true,
    voiceEnabled: false,
    language: 'en',
    personality: 'friendly'
  });
  const [userPreferences, setUserPreferences] = useState<UserPreferences | null>(null);
  const [currentSuggestions, setCurrentSuggestions] = useState<SuggestionChip[]>([]);
  const [qualityTrends, setQualityTrends] = useState<any[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [sessionAnalytics, setSessionAnalytics] = useState<any>(null);
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const speechRecognitionRef = useRef<any>(null);
  
  // Scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);
  
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);
  
  // Initialize speech recognition
  useEffect(() => {
    if (settings.voiceEnabled && 'webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = settings.language;
      
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(transcript);
        setIsListening(false);
      };
      
      recognition.onerror = () => {
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      speechRecognitionRef.current = recognition;
    }
  }, [settings.voiceEnabled, settings.language]);
  
  // Enhanced message sending with quality analysis
  const sendMessage = async (messageContent: string, isFollowUp: boolean = false) => {
    if (!messageContent.trim()) return;
    
    // Add user message
    const userMessage: EnhancedMessage = {
      id: generateId(),
      content: messageContent,
      timestamp: new Date(),
      isUser: true
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setCurrentSuggestions([]);
    
    try {
      // Enhanced API call with quality analysis
      const response = await fetch('/api/vpa/enhanced-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_query: messageContent,
          user_id: userPreferences?.userId || 'anonymous',
          session_id: generateSessionId(),
          use_rag: true,
          enable_quality_analysis: settings.showQualityMetrics,
          enable_enhancements: true,
          user_preferences: userPreferences,
          context: messages.slice(-5) // Last 5 messages for context
        })
      });
      
      const data = await response.json();
      
      // Create enhanced assistant message
      const assistantMessage: EnhancedMessage = {
        id: generateId(),
        content: data.content,
        timestamp: new Date(),
        isUser: false,
        qualityMetrics: data.quality_metrics,
        enhancements: data.enhancements,
        provider: data.provider_used,
        model: data.model_used,
        responseTime: data.response_time,
        tokens: data.token_count,
        cost: data.cost_estimate,
        contextUsed: data.context_used,
        ragContext: data.rag_context,
        suggestions: data.enhancements?.suggestion_chips || [],
        accessibility: data.enhancements?.accessibility_features
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update suggestions
      if (data.enhancements?.suggestion_chips) {
        setCurrentSuggestions(data.enhancements.suggestion_chips);
      }
      
      // Update analytics
      updateSessionAnalytics(assistantMessage);
      
      // Auto-play response if enabled
      if (settings.enableSounds && settings.voiceEnabled) {
        speakText(data.content);
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage: EnhancedMessage = {
        id: generateId(),
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        isUser: false
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle suggestion chip click
  const handleSuggestionClick = (suggestion: SuggestionChip) => {
    if (suggestion.action === 'query') {
      sendMessage(suggestion.text, true);
    } else if (suggestion.action === 'rephrase') {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && !lastMessage.isUser) {
        requestRephrase(lastMessage.id);
      }
    } else if (suggestion.action === 'example') {
      sendMessage(`Can you give me a practical example of ${suggestion.text}?`, true);
    } else if (suggestion.action === 'clarify') {
      sendMessage(`Can you clarify what you mean by ${suggestion.text}?`, true);
    }
  };
  
  // Submit feedback
  const submitFeedback = async (messageId: string, feedback: UserFeedback) => {
    try {
      await fetch('/api/vpa/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message_id: messageId,
          user_id: userPreferences?.userId || 'anonymous',
          feedback: feedback
        })
      });
      
      // Update message with feedback
      setMessages(prev => prev.map(msg => 
        msg.id === messageId 
          ? { ...msg, feedback: feedback }
          : msg
      ));
      
      // Show feedback confirmation
      showNotification('Thank you for your feedback!', 'success');
      
    } catch (error) {
      console.error('Error submitting feedback:', error);
      showNotification('Failed to submit feedback. Please try again.', 'error');
    }
  };
  
  // Voice recognition
  const startListening = () => {
    if (speechRecognitionRef.current && !isListening) {
      setIsListening(true);
      speechRecognitionRef.current.start();
    }
  };
  
  const stopListening = () => {
    if (speechRecognitionRef.current && isListening) {
      speechRecognitionRef.current.stop();
      setIsListening(false);
    }
  };
  
  // Text-to-speech
  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      window.speechSynthesis.speak(utterance);
    }
  };
  
  // Update session analytics
  const updateSessionAnalytics = (message: EnhancedMessage) => {
    setSessionAnalytics(prev => ({
      ...prev,
      messageCount: (prev?.messageCount || 0) + 1,
      totalResponseTime: (prev?.totalResponseTime || 0) + (message.responseTime || 0),
      averageQuality: calculateAverageQuality(messages.concat(message)),
      totalTokens: (prev?.totalTokens || 0) + (message.tokens || 0),
      totalCost: (prev?.totalCost || 0) + (message.cost || 0)
    }));
  };
  
  // Calculate average quality
  const calculateAverageQuality = (messages: EnhancedMessage[]): number => {
    const qualityMessages = messages.filter(msg => msg.qualityMetrics);
    if (qualityMessages.length === 0) return 0;
    
    const totalQuality = qualityMessages.reduce((sum, msg) => {
      const metrics = msg.qualityMetrics!;
      return sum + ((metrics.relevanceScore + metrics.accuracyScore + 
                     metrics.completenessScore + metrics.clarityScore + 
                     metrics.helpfulnessScore) / 5);
    }, 0);
    
    return totalQuality / qualityMessages.length;
  };
  
  // Utility functions
  const generateId = (): string => {
    return Math.random().toString(36).substr(2, 9);
  };
  
  const generateSessionId = (): string => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };
  
  const showNotification = (message: string, type: 'success' | 'error' | 'info') => {
    // Implementation for showing notifications
    console.log(`${type}: ${message}`);
  };
  
  const requestRephrase = async (messageId: string) => {
    const message = messages.find(m => m.id === messageId);
    if (message) {
      sendMessage(`Can you rephrase this response: "${message.content}"`, true);
    }
  };
  
  // Render quality indicator
  const renderQualityIndicator = (quality: string) => {
    const getQualityColor = (quality: string) => {
      switch (quality) {
        case 'excellent': return 'text-green-600';
        case 'good': return 'text-blue-600';
        case 'average': return 'text-yellow-600';
        case 'poor': return 'text-orange-600';
        case 'unacceptable': return 'text-red-600';
        default: return 'text-gray-600';
      }
    };
    
    const getQualityIcon = (quality: string) => {
      switch (quality) {
        case 'excellent': return <Award className="w-4 h-4" />;
        case 'good': return <CheckCircle className="w-4 h-4" />;
        case 'average': return <AlertCircle className="w-4 h-4" />;
        case 'poor': return <XCircle className="w-4 h-4" />;
        case 'unacceptable': return <XCircle className="w-4 h-4" />;
        default: return <HelpCircle className="w-4 h-4" />;
      }
    };
    
    return (
      <div className={`flex items-center space-x-1 ${getQualityColor(quality)}`}>
        {getQualityIcon(quality)}
        <span className="text-xs font-medium capitalize">{quality}</span>
      </div>
    );
  };
  
  // Render suggestion chips
  const renderSuggestionChips = () => {
    if (!currentSuggestions.length || !settings.autoSuggestions) return null;
    
    return (
      <div className="p-3 border-t bg-gray-50">
        <div className="flex flex-wrap gap-2">
          {currentSuggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors"
            >
              {suggestion.text}
            </button>
          ))}
        </div>
      </div>
    );
  };
  
  // Render accessibility features
  const renderAccessibilityFeatures = (features: AccessibilityFeatures) => {
    return (
      <div className="text-xs text-gray-500 mt-1">
        <div className="flex items-center space-x-2">
          <Clock className="w-3 h-3" />
          <span>{features.readingTime} min read</span>
          <span>•</span>
          <span className="capitalize">{features.complexityLevel} complexity</span>
        </div>
      </div>
    );
  };
  
  // Render quality metrics
  const renderQualityMetrics = (metrics: QualityMetrics) => {
    if (!settings.showQualityMetrics) return null;
    
    return (
      <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
        <div className="grid grid-cols-2 gap-2">
          <div>Relevance: {(metrics.relevanceScore * 100).toFixed(0)}%</div>
          <div>Accuracy: {(metrics.accuracyScore * 100).toFixed(0)}%</div>
          <div>Completeness: {(metrics.completenessScore * 100).toFixed(0)}%</div>
          <div>Clarity: {(metrics.clarityScore * 100).toFixed(0)}%</div>
        </div>
        {settings.showResponseTime && (
          <div className="mt-1 text-gray-600">
            Response time: {metrics.responseTime.toFixed(2)}s
          </div>
        )}
      </div>
    );
  };
  
  // Render message
  const renderMessage = (message: EnhancedMessage) => {
    return (
      <div
        key={message.id}
        className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} mb-4`}
      >
        <div
          className={`max-w-[80%] p-3 rounded-lg ${
            message.isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          <div className="flex items-start space-x-2">
            {!message.isUser && (
              <Bot className="w-5 h-5 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <div className="prose prose-sm max-w-none">
                {message.content}
              </div>
              
              {/* Quality indicators */}
              {!message.isUser && message.qualityMetrics && (
                <div className="mt-2 flex items-center justify-between">
                  {renderQualityIndicator(message.qualityMetrics.overallQuality)}
                  
                  {settings.showResponseTime && message.responseTime && (
                    <div className="flex items-center space-x-1 text-xs text-gray-500">
                      <Clock className="w-3 h-3" />
                      <span>{message.responseTime.toFixed(2)}s</span>
                    </div>
                  )}
                </div>
              )}
              
              {/* Accessibility features */}
              {!message.isUser && message.accessibility && settings.enableAccessibility && (
                renderAccessibilityFeatures(message.accessibility)
              )}
              
              {/* Quality metrics */}
              {!message.isUser && message.qualityMetrics && (
                renderQualityMetrics(message.qualityMetrics)
              )}
              
              {/* Feedback buttons */}
              {!message.isUser && !message.feedback && (
                <div className="mt-2 flex items-center space-x-2">
                  <button
                    onClick={() => submitFeedback(message.id, { thumbsUp: true, timestamp: new Date() })}
                    className="p-1 hover:bg-gray-200 rounded"
                  >
                    <ThumbsUp className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => submitFeedback(message.id, { thumbsUp: false, timestamp: new Date() })}
                    className="p-1 hover:bg-gray-200 rounded"
                  >
                    <ThumbsDown className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => speakText(message.content)}
                    className="p-1 hover:bg-gray-200 rounded"
                  >
                    <Volume2 className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  // Main render
  return (
    <div
      className={`fixed bottom-6 right-6 w-96 bg-white rounded-lg shadow-xl border transition-all duration-300 ${
        isExpanded ? 'h-[600px]' : 'h-16'
      }`}
    >
      {/* Header */}
      <div 
        className="flex items-center justify-between p-4 border-b cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-medium">VPA Assistant</h3>
            <p className="text-xs text-gray-500">Enhanced with AI Quality</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {sessionAnalytics && (
            <div className="text-xs text-gray-500">
              Quality: {(sessionAnalytics.averageQuality * 100).toFixed(0)}%
            </div>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowSettings(!showSettings);
            }}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <Settings className="w-4 h-4" />
          </button>
          {isExpanded ? (
            <Minimize2 className="w-4 h-4" />
          ) : (
            <Maximize2 className="w-4 h-4" />
          )}
        </div>
      </div>
      
      {isExpanded && (
        <>
          {/* Messages */}
          <div
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4 h-[400px]"
          >
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>Hi! I'm your enhanced VPA assistant.</p>
                <p className="text-sm mt-1">Ask me anything and I'll provide quality-optimized responses!</p>
              </div>
            ) : (
              messages.map(renderMessage)
            )}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 p-3 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <span className="text-sm text-gray-600">Generating quality response...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Suggestion chips */}
          {renderSuggestionChips()}
          
          {/* Input */}
          <div className="p-4 border-t">
            <div className="flex items-center space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage(inputValue);
                  }
                }}
                placeholder="Ask me anything..."
                className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              
              {settings.voiceEnabled && (
                <button
                  onClick={isListening ? stopListening : startListening}
                  className={`p-2 rounded-md ${
                    isListening ? 'bg-red-500 text-white' : 'bg-gray-100 hover:bg-gray-200'
                  }`}
                >
                  {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </button>
              )}
              
              <button
                onClick={() => sendMessage(inputValue)}
                disabled={!inputValue.trim() || isLoading}
                className="p-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </>
      )}
      
      {/* Settings Panel */}
      {showSettings && (
        <div className="absolute top-0 left-0 w-full h-full bg-white rounded-lg p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium">Settings</h3>
            <button
              onClick={() => setShowSettings(false)}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Theme</label>
              <select
                value={settings.theme}
                onChange={(e) => setSettings(prev => ({ ...prev, theme: e.target.value as any }))}
                className="w-full p-2 border rounded-md"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="auto">Auto</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Font Size</label>
              <select
                value={settings.fontSize}
                onChange={(e) => setSettings(prev => ({ ...prev, fontSize: e.target.value as any }))}
                className="w-full p-2 border rounded-md"
              >
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={settings.showQualityMetrics}
                  onChange={(e) => setSettings(prev => ({ ...prev, showQualityMetrics: e.target.checked }))}
                />
                <span className="text-sm">Show quality metrics</span>
              </label>
              
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={settings.showResponseTime}
                  onChange={(e) => setSettings(prev => ({ ...prev, showResponseTime: e.target.checked }))}
                />
                <span className="text-sm">Show response time</span>
              </label>
              
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={settings.autoSuggestions}
                  onChange={(e) => setSettings(prev => ({ ...prev, autoSuggestions: e.target.checked }))}
                />
                <span className="text-sm">Auto suggestions</span>
              </label>
              
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={settings.contextualHelp}
                  onChange={(e) => setSettings(prev => ({ ...prev, contextualHelp: e.target.checked }))}
                />
                <span className="text-sm">Contextual help</span>
              </label>
              
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={settings.voiceEnabled}
                  onChange={(e) => setSettings(prev => ({ ...prev, voiceEnabled: e.target.checked }))}
                />
                <span className="text-sm">Voice features</span>
              </label>
              
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={settings.enableAccessibility}
                  onChange={(e) => setSettings(prev => ({ ...prev, enableAccessibility: e.target.checked }))}
                />
                <span className="text-sm">Accessibility features</span>
              </label>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VPAEnhancedChatWidget;

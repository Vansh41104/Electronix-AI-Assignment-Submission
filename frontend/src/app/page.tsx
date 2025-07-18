'use client';
import { useState, useEffect, useCallback } from 'react';

interface SentimentResult {
  label: string;
  score: number;
}

export default function Home() {
  const [text, setText] = useState<string>('');
  const [result, setResult] = useState<SentimentResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState<boolean>(true);
  const [typingTimeout, setTypingTimeout] = useState<NodeJS.Timeout | null>(null);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  
  useEffect(() => {
    return () => {
      if (typingTimeout) {
        clearTimeout(typingTimeout);
      }
      if (abortController) {
        abortController.abort();
      }
    };
  }, [typingTimeout, abortController]);

  const performPrediction = useCallback(async (inputText: string) => {
    if (!inputText.trim()) {
      setResult(null);
      setLoading(false);
      return;
    }

    if (abortController) {
      abortController.abort();
    }

    const controller = new AbortController();
    setAbortController(controller);
    setLoading(true);
    setError(null);

    const graphqlQuery = {
      query: `
        query Predict($text: String!) {
          predict(text: $text) {
            label
            score
          }
        }
      `,
      variables: { text: inputText.trim() },
    };

    try {
      const response = await fetch('http://localhost:8000/graphql', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(graphqlQuery),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const payload = await response.json();

      if (payload.errors && payload.errors.length > 0) {
        console.error('GraphQL errors', payload.errors);
        throw new Error(payload.errors[0].message);
      }

      const data: SentimentResult = payload.data.predict;
      setResult(data);
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') {
        return;
      }
      
      setError('Failed to get prediction. Please try again.');
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
      setAbortController(null);
    }
  }, [abortController]);

  const handlePredict = () => {
    if (!text.trim()) {
      setError('Please enter some text');
      return;
    }
    performPrediction(text);
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setText(newText);

    if (typingTimeout) {
      clearTimeout(typingTimeout);
    }

    if (abortController) {
      abortController.abort();
    }

    if (newText.trim().length <= 5) {
      setResult(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    const timeout = setTimeout(() => {
      performPrediction(newText);
    }, 800);

    setTypingTimeout(timeout);
  };

  const getSentimentColor = (label: string): string => {
    return label === 'positive' ? '#34d399' : '#f87171';
  };

  const getSentimentGradient = (label: string): string => {
    return label === 'positive' ? 'from-emerald-500 to-green-600' : 'from-red-500 to-rose-600';
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const bgClass = darkMode 
    ? "min-h-screen bg-gradient-to-br from-gray-900 via-gray-950 to-black text-white"
    : "min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-white text-gray-900";

  const cardClass = darkMode
    ? "bg-gray-900/70 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-gray-700"
    : "bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-gray-200";

  const inputClass = darkMode
    ? "w-full bg-gray-800/70 text-gray-100 placeholder-gray-400 p-4 rounded-2xl border border-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/70 focus:border-indigo-500/70 transition-all duration-300 resize-none shadow-sm"
    : "w-full bg-gray-50 text-gray-900 placeholder-gray-500 p-4 rounded-2xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/70 focus:border-indigo-500/70 transition-all duration-300 resize-none shadow-sm";

  const resultClass = darkMode
    ? "bg-gray-800/80 border border-gray-700 rounded-2xl p-6 space-y-4 shadow-lg"
    : "bg-gray-50 border border-gray-200 rounded-2xl p-6 space-y-4 shadow-lg";

  return (
    <div className={`${bgClass} flex items-center justify-center p-4 transition-all duration-500`}>
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-20 left-20 w-32 h-32 ${darkMode ? 'bg-gradient-to-r from-purple-700/20 to-indigo-700/20' : 'bg-gradient-to-r from-purple-300/30 to-indigo-300/30'} rounded-full blur-xl transition-all duration-500`}></div>
        <div className={`absolute bottom-20 right-20 w-40 h-40 ${darkMode ? 'bg-gradient-to-r from-emerald-700/20 to-cyan-700/20' : 'bg-gradient-to-r from-emerald-300/30 to-cyan-300/30'} rounded-full blur-xl transition-all duration-500`}></div>
        <div className={`absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-24 h-24 ${darkMode ? 'bg-gradient-to-r from-purple-600/10 to-pink-600/10' : 'bg-gradient-to-r from-purple-200/20 to-pink-200/20'} rounded-full blur-lg transition-all duration-500`}></div>
      </div>

      <div className="relative z-10 w-full max-w-lg">
        <div className="text-center mb-8">
          <div className="flex justify-between items-center mb-4">
            <div className="flex space-x-2">
              <button
                onClick={toggleDarkMode}
                className={`p-2 rounded-xl transition-all duration-300 ${darkMode ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
                title="Toggle dark mode"
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
            </div>
          </div>

          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent mb-3">
            Sentiment Analysis
          </h1>
          <p className={`${darkMode ? 'text-gray-300' : 'text-gray-600'} text-lg`}>
            Discover the emotional tone of your text
          </p>
        </div>

        <div className={`${cardClass} relative overflow-hidden transition-all duration-500`}>
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-cyan-500/10 rounded-3xl"></div>
          <div className={`absolute inset-[1px] ${darkMode ? 'bg-gray-900/80' : 'bg-white/90'} backdrop-blur-xl rounded-3xl transition-all duration-500`}></div>

          <div className="relative z-10 space-y-6">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <label className={`block ${darkMode ? 'text-gray-300' : 'text-gray-700'} text-sm font-semibold`}>
                  Enter your text
                </label>
                <div className="flex items-center space-x-2">
                  {loading && (
                    <div className="w-3 h-3 border border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
                  )}
                  <span className={`text-xs ${darkMode ? 'text-indigo-400' : 'text-indigo-600'} font-medium`}>
                    Auto-analysis enabled
                  </span>
                </div>
              </div>
              <textarea
                value={text}
                onChange={handleTextChange}
                placeholder="Type something to analyze... (analysis starts after 5+ characters)"
                rows={4}
                className={inputClass}
              />
            </div>

            <button
              onClick={handlePredict}
              disabled={loading || !text.trim()}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold py-4 rounded-2xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98]"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Analyzing...</span>
                </div>
              ) : (
                'Analyze Now'
              )}
            </button>

            {error && (
              <div className="bg-red-800/60 border border-red-500 text-red-100 p-4 rounded-2xl text-sm font-medium shadow-sm">
                {error}
              </div>
            )}

            {result && (
              <div className={resultClass}>
                <div className="flex items-center justify-between">
                  <span className={`${darkMode ? 'text-gray-300' : 'text-gray-700'} font-semibold`}>Sentiment Analysis</span>
                  <div className={`w-4 h-4 rounded-full bg-gradient-to-r ${getSentimentGradient(result.label)} shadow-sm`}></div>
                </div>

                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className={`${darkMode ? 'text-gray-300' : 'text-gray-700'} font-medium`}>Sentiment</span>
                    <span 
                      className="font-bold text-xl"
                      style={{ color: getSentimentColor(result.label) }}
                    >
                      {result.label.charAt(0).toUpperCase() + result.label.slice(1)}
                    </span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className={`${darkMode ? 'text-gray-300' : 'text-gray-700'} font-medium`}>Confidence</span>
                    <span className={`${darkMode ? 'text-white' : 'text-gray-900'} font-bold text-lg`}>
                      {(result.score * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div className="space-y-2">
                    <div className={`h-3 ${darkMode ? 'bg-gray-700/70' : 'bg-gray-200'} rounded-full overflow-hidden shadow-inner`}>
                      <div
                        className={`h-full rounded-full transition-all duration-1000 ease-out bg-gradient-to-r ${getSentimentGradient(result.label)} shadow-sm`}
                        style={{
                          width: `${result.score * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {loading && !result && (
              <div className={`${resultClass} border-2 border-indigo-500/30`}>
                <div className="flex items-center justify-center py-8">
                  <div className="flex items-center space-x-3">
                    <div className="w-5 h-5 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin"></div>
                    <span className={`${darkMode ? 'text-gray-400' : 'text-gray-600'} text-sm`}>
                      Analyzing sentiment...
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
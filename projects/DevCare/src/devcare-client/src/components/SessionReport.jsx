import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { ArrowRight } from 'lucide-react';

export default function SessionReport({ results, bodyEvaluation, onSubmit }) {
  // Sort data so the chart renders properly (descending)
  const data = bodyEvaluation.body_part_scores.map(item => ({
    name: item.part.charAt(0).toUpperCase() + item.part.slice(1),
    score: item.score
  }));

  // Define colors based on score
  const getColor = (score) => {
    if (score >= 90) return '#10B981'; // emerald-500
    if (score >= 75) return '#3B82F6'; // blue-500
    if (score >= 60) return '#F59E0B'; // amber-500
    return '#EF4444'; // red-500
  };

  return (
    <div className="bg-gray-800 p-8 rounded-2xl shadow-xl border border-gray-700 max-w-4xl mx-auto space-y-8 animate-in fade-in zoom-in duration-500">
      <div className="text-center">
        <h2 className="text-4xl font-bold text-white mb-4">Session Complete!</h2>
        <p className="text-gray-400 text-lg">Great job! Here is your AI movement analysis.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left Col: Exercise Summary */}
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-4 text-white">Exercise Summary</h3>
          <div className="space-y-3">
            {results.map((r, idx) => (
              <div key={idx} className="flex justify-between items-center p-3 bg-gray-800 rounded-lg">
                <span className="font-medium text-gray-300">{r.name}</span>
                <div className="text-sm">
                  <span className="text-emerald-400 font-bold mr-4">{r.reps} Reps</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Col: Body Evaluation Chart */}
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-700 flex flex-col">
          <h3 className="text-xl font-semibold mb-4 text-white">Body Part Scores</h3>
          <div className="flex-1 w-full min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <XAxis type="number" domain={[0, 100]} hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#9CA3AF' }} />
                <Tooltip 
                  cursor={{fill: 'rgba(255, 255, 255, 0.05)'}} 
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '0.5rem' }} 
                />
                <Bar dataKey="score" radius={[0, 4, 4, 0]} barSize={20}>
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getColor(entry.score)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <button
        onClick={onSubmit}
        className="flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white w-full py-4 rounded-xl font-bold text-xl transition-all shadow-lg shadow-blue-500/20"
      >
        Submit Report to Doctor <ArrowRight size={24} />
      </button>
    </div>
  );
}

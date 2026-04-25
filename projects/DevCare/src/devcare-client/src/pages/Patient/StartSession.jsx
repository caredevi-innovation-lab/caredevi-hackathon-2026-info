import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import '@mediapipe/pose';
import '@mediapipe/drawing_utils';

const Pose = window.Pose;
const POSE_CONNECTIONS = window.POSE_CONNECTIONS;
const drawConnectors = window.drawConnectors;
const drawLandmarks = window.drawLandmarks;
import { usePose } from '../../hooks/usePose';
import {
  evaluateBicepCurl,
  evaluateSquat,
  evaluateShoulderRaise,
  evaluateKneeExtension,
  evaluateHipAbduction
} from '../../utils/exerciseEvaluators';
import { generateBodyEvaluation } from '../../utils/bodyEvaluation';
import SessionReport from '../../components/SessionReport';
import { CheckCircle, Play, Video, ArrowRight } from 'lucide-react';

const EVALUATOR_MAP = {
  'Bicep Curl': evaluateBicepCurl,
  'Squat': evaluateSquat,
  'Shoulder Raise': evaluateShoulderRaise,
  'Knee Extension': evaluateKneeExtension,
  'Hip Abduction': evaluateHipAbduction,
};

export default function StartSession() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  // State
  const [plan, setPlan] = useState(null);
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [sessionActive, setSessionActive] = useState(false);
  const [sessionCompleted, setSessionCompleted] = useState(false);
  
  const [exerciseState, setExerciseState] = useState({
    reps: 0,
    stage: 'down',
    feedback: 'Get ready',
    currentAngle: 0
  });
  const [results, setResults] = useState([]); // Array to store final results

  const [angleHistory, setAngleHistory] = useState({
    arms: [], shoulders: [], hips: [], knees: [], ankles: []
  });
  const [bodyEvaluation, setBodyEvaluation] = useState(null);

  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const requestRef = useRef(null);
  const exerciseStateRef = useRef(exerciseState);
  const angleHistoryRef = useRef(angleHistory);

  // Sync state to ref for access in onResults callback without re-binding
  useEffect(() => {
    exerciseStateRef.current = exerciseState;
  }, [exerciseState]);

  useEffect(() => {
    angleHistoryRef.current = angleHistory;
  }, [angleHistory]);


  // Mock Fetch Plan
  useEffect(() => {
    // In a real app: axios.get(`/api/rehab/sessions/${sessionId}/plan`)
    const fetchPlan = async () => {
      // Mock data
      setPlan({
        id: sessionId || '123',
        title: "Daily Shoulder & Leg Routine",
        exercises: [
          { name: 'Bicep Curl', targetReps: 5, instructions: 'Keep your elbows close to your torso.' },
          { name: 'Squat', targetReps: 5, instructions: 'Keep your back straight and go low.' },
          { name: 'Shoulder Raise', targetReps: 5, instructions: 'Raise arms parallel to floor.' }
        ]
      });
    };
    fetchPlan();
  }, [sessionId]);

  const currentExercise = plan?.exercises[currentExerciseIndex];

  // Pose Results Callback
  const onResults = useCallback((resultsMediaPipe) => {
    if (!canvasRef.current || !webcamRef.current?.video) return;

    const videoWidth = webcamRef.current.video.videoWidth;
    const videoHeight = webcamRef.current.video.videoHeight;

    canvasRef.current.width = videoWidth;
    canvasRef.current.height = videoHeight;

    const canvasCtx = canvasRef.current.getContext('2d');
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, videoWidth, videoHeight);

    // Draw the video frame
    canvasCtx.drawImage(resultsMediaPipe.image, 0, 0, videoWidth, videoHeight);

    if (resultsMediaPipe.poseLandmarks && currentExercise) {
      // Draw skeleton
      drawConnectors(canvasCtx, resultsMediaPipe.poseLandmarks, POSE_CONNECTIONS, { color: '#00FF00', lineWidth: 4 });
      drawLandmarks(canvasCtx, resultsMediaPipe.poseLandmarks, { color: '#FF0000', lineWidth: 2 });

      // Evaluate exercise
      const evaluator = EVALUATOR_MAP[currentExercise.name];
      if (evaluator) {
        const newState = evaluator(resultsMediaPipe.poseLandmarks, exerciseStateRef.current);
        
        // Track angles based on exercise
        const angle = newState.currentAngle;
        if (angle) {
          const newHistory = { ...angleHistoryRef.current };
          if (currentExercise.name === 'Bicep Curl') newHistory.arms.push(angle);
          if (currentExercise.name === 'Shoulder Raise') newHistory.shoulders.push(angle);
          if (currentExercise.name === 'Squat') {
            newHistory.hips.push(angle);
            newHistory.knees.push(angle);
          }
          if (currentExercise.name === 'Knee Extension') newHistory.knees.push(angle);
          if (currentExercise.name === 'Hip Abduction') newHistory.hips.push(angle);
          
          setAngleHistory(newHistory);
        }

        // Update state if something changed (avoid excessive renders)
        if (
          newState.reps !== exerciseStateRef.current.reps ||
          newState.stage !== exerciseStateRef.current.stage ||
          newState.feedback !== exerciseStateRef.current.feedback
        ) {
          setExerciseState(newState);

          // Check if target reps reached
          if (newState.reps >= currentExercise.targetReps) {
            handleExerciseComplete();
          }
        }
      }
    }
    canvasCtx.restore();
  }, [currentExercise]);

  const { pose, isLoaded } = usePose(onResults);

  // Animation Loop for camera
  const detectPose = useCallback(async () => {
    if (
      typeof webcamRef.current !== "undefined" &&
      webcamRef.current !== null &&
      webcamRef.current.video.readyState === 4 &&
      pose
    ) {
      // Send image to mediapipe
      await pose.send({ image: webcamRef.current.video });
    }
    if (sessionActive) {
      requestRef.current = requestAnimationFrame(detectPose);
    }
  }, [pose, sessionActive]);

  useEffect(() => {
    if (sessionActive) {
      requestRef.current = requestAnimationFrame(detectPose);
    } else {
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    }
    return () => {
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    };
  }, [sessionActive, detectPose]);

  const handleExerciseComplete = () => {
    setSessionActive(false); // Pause detection briefly
    
    // Save Result
    setResults(prev => [...prev, {
      name: currentExercise.name,
      reps: exerciseStateRef.current.reps,
      accuracy: 95, // mock accuracy
      duration: 60 // mock duration
    }]);

    if (currentExerciseIndex < plan.exercises.length - 1) {
      // Move to next
      setCurrentExerciseIndex(prev => prev + 1);
      setExerciseState({ reps: 0, stage: 'down', feedback: 'Get ready', currentAngle: 0 });
    } else {
      // Session Complete
      const evaluation = generateBodyEvaluation(angleHistoryRef.current);
      setBodyEvaluation(evaluation);
      setSessionCompleted(true);
    }
  };

  const startCurrentExercise = () => {
    setSessionActive(true);
  };

  const submitSessionReport = async () => {
    const report = {
      exercise_results: results,
      ...bodyEvaluation
    };
    console.log("Submitting report to backend:", report);
    // Mock API call: await axios.post(`/api/rehab/sessions/${sessionId}/complete/`, report);
    alert("Session report submitted successfully!");
    navigate('/dashboard/patient');
  };

  if (!plan) return <div className="p-8 text-center">Loading session plan...</div>;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between bg-gray-800 p-6 rounded-2xl shadow-xl border border-gray-700">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
              {plan.title}
            </h1>
            <p className="text-gray-400 mt-2">
              Exercise {currentExerciseIndex + 1} of {plan.exercises.length}
            </p>
          </div>
          <div className="text-right">
            <span className="text-sm text-gray-400 block mb-1">Status</span>
            <span className={`px-4 py-1.5 rounded-full text-sm font-semibold ${
              sessionCompleted ? 'bg-green-500/20 text-green-400' :
              sessionActive ? 'bg-blue-500/20 text-blue-400 animate-pulse' : 
              'bg-yellow-500/20 text-yellow-400'
            }`}>
              {sessionCompleted ? 'Completed' : sessionActive ? 'In Progress' : 'Waiting'}
            </span>
          </div>
        </div>

        {/* Main Content */}
        {!sessionCompleted ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left Col: Instructions & Status */}
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-xl">
                <h2 className="text-2xl font-bold text-white mb-2">{currentExercise.name}</h2>
                <p className="text-gray-400 mb-6">{currentExercise.instructions}</p>
                
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-gray-900 p-4 rounded-xl border border-gray-700 text-center">
                    <span className="text-sm text-gray-500 block">Target Reps</span>
                    <span className="text-3xl font-bold text-blue-400">{currentExercise.targetReps}</span>
                  </div>
                  <div className="bg-gray-900 p-4 rounded-xl border border-gray-700 text-center">
                    <span className="text-sm text-gray-500 block">Completed</span>
                    <span className="text-3xl font-bold text-emerald-400">{exerciseState.reps}</span>
                  </div>
                </div>

                <div className="bg-gray-900 p-4 rounded-xl border border-gray-700">
                  <span className="text-sm text-gray-500 block mb-1">AI Feedback</span>
                  <span className={`font-semibold text-lg ${
                    exerciseState.feedback === 'Good form' ? 'text-emerald-400' : 'text-yellow-400'
                  }`}>
                    {exerciseState.feedback}
                  </span>
                </div>
              </div>

              {!sessionActive ? (
                <button
                  onClick={startCurrentExercise}
                  disabled={!isLoaded}
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white py-4 rounded-xl font-bold text-lg transition-all shadow-lg shadow-blue-500/20"
                >
                  <Video size={24} />
                  {isLoaded ? 'Start Tracking' : 'Initializing AI...'}
                </button>
              ) : (
                <button
                  onClick={() => setSessionActive(false)}
                  className="w-full flex items-center justify-center gap-2 bg-red-600 hover:bg-red-500 text-white py-4 rounded-xl font-bold text-lg transition-all shadow-lg shadow-red-500/20"
                >
                  Pause Tracking
                </button>
              )}
            </div>

            {/* Right Col: Camera Feed */}
            <div className="lg:col-span-2 relative bg-black rounded-2xl overflow-hidden border-2 border-gray-700 shadow-2xl aspect-video flex items-center justify-center">
              {!sessionActive && (
                <div className="absolute inset-0 z-10 bg-gray-900/80 backdrop-blur-sm flex flex-col items-center justify-center">
                  <Play size={64} className="text-gray-600 mb-4" />
                  <p className="text-gray-400 text-lg font-medium">Click Start Tracking to begin</p>
                </div>
              )}
              
              <Webcam
                ref={webcamRef}
                className="absolute w-full h-full object-cover"
                mirrored={true}
              />
              <canvas
                ref={canvasRef}
                className="absolute w-full h-full object-cover z-0"
                style={{ transform: 'scaleX(-1)' }} // Mirror canvas to match webcam
              />
            </div>
            
          </div>
        ) : (
          <SessionReport 
            results={results}
            bodyEvaluation={bodyEvaluation}
            onSubmit={submitSessionReport}
          />
        )}

      </div>
    </div>
  );
}

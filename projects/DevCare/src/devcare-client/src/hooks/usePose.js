import '@mediapipe/pose';
import '@mediapipe/camera_utils';

const Pose = window.Pose;
const POSE_CONNECTIONS = window.POSE_CONNECTIONS;
import { useEffect, useRef, useState } from 'react';

/**
 * Hook to manage MediaPipe Pose initialization and lifecycle.
 * @param {Function} onResultsCallback - Callback triggered when pose is detected.
 */
export const usePose = (onResultsCallback) => {
  const poseRef = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const pose = new Pose({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
      }
    });

    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      enableSegmentation: false,
      smoothSegmentation: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    pose.onResults(onResultsCallback);
    poseRef.current = pose;
    
    // Simulate loading completion since MediaPipe initializes asynchronously
    // In a real app we'd wait for the first result or use an initialize callback
    setTimeout(() => setIsLoaded(true), 1000);

    return () => {
      if (poseRef.current) {
        poseRef.current.close();
      }
    };
  }, [onResultsCallback]);

  return { pose: poseRef.current, isLoaded };
};

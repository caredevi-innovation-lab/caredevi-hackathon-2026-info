import { calculateAngle } from './angleUtils';

/**
 * Exercise Evaluators
 * Each function takes `landmarks` and `state` as arguments.
 * `landmarks`: Mediapipe pose landmarks.
 * `state`: Current exercise state object { reps, stage, feedback, ... }.
 * Returns the updated `state`.
 */

// Helper to get landmark
const getLandmark = (landmarks, index) => landmarks[index];

export const evaluateBicepCurl = (landmarks, state) => {
  // landmarks for right arm: shoulder=12, elbow=14, wrist=16
  // We can use left or right. Let's use right for simplicity or choose the most visible one.
  const shoulder = getLandmark(landmarks, 12);
  const elbow = getLandmark(landmarks, 14);
  const wrist = getLandmark(landmarks, 16);

  if (!shoulder || !elbow || !wrist) return state;

  const angle = calculateAngle(shoulder, elbow, wrist);
  let newStage = state.stage;
  let newReps = state.reps;
  let newFeedback = "Good form";

  if (angle > 160) {
    newStage = "down";
  }
  if (angle < 45 && newStage === "down") {
    newStage = "up";
    newReps += 1;
  }

  // Simple mistake detection
  if (angle > 45 && angle < 160) {
    newFeedback = "Keep going";
  }

  return { ...state, reps: newReps, stage: newStage, feedback: newFeedback, currentAngle: angle };
};

export const evaluateSquat = (landmarks, state) => {
  // landmarks for right leg: hip=24, knee=26, ankle=28
  const hip = getLandmark(landmarks, 24);
  const knee = getLandmark(landmarks, 26);
  const ankle = getLandmark(landmarks, 28);

  if (!hip || !knee || !ankle) return state;

  const angle = calculateAngle(hip, knee, ankle);
  let newStage = state.stage;
  let newReps = state.reps;
  let newFeedback = "Good form";

  // Standing: angle ~ 180, Squatting: angle < 90
  if (angle > 160) {
    newStage = "up";
  }
  if (angle < 100 && newStage === "up") {
    newStage = "down";
    newReps += 1;
  }

  if (angle > 100 && angle < 160) {
     newFeedback = "Go lower";
  }

  return { ...state, reps: newReps, stage: newStage, feedback: newFeedback, currentAngle: angle };
};

export const evaluateShoulderRaise = (landmarks, state) => {
  // Lateral raise. Right side: hip=24, shoulder=12, elbow=14
  const hip = getLandmark(landmarks, 24);
  const shoulder = getLandmark(landmarks, 12);
  const elbow = getLandmark(landmarks, 14);

  if (!hip || !shoulder || !elbow) return state;

  const angle = calculateAngle(hip, shoulder, elbow);
  let newStage = state.stage;
  let newReps = state.reps;
  let newFeedback = "Good form";

  // Arms down: angle < 30, Arms up: angle > 80
  if (angle < 30) {
    newStage = "down";
  }
  if (angle > 80 && newStage === "down") {
    newStage = "up";
    newReps += 1;
  }

  if (angle > 90) {
    newFeedback = "Don't raise too high";
  }

  return { ...state, reps: newReps, stage: newStage, feedback: newFeedback, currentAngle: angle };
};

export const evaluateKneeExtension = (landmarks, state) => {
  // Right leg: hip=24, knee=26, ankle=28
  const hip = getLandmark(landmarks, 24);
  const knee = getLandmark(landmarks, 26);
  const ankle = getLandmark(landmarks, 28);

  if (!hip || !knee || !ankle) return state;

  const angle = calculateAngle(hip, knee, ankle);
  let newStage = state.stage;
  let newReps = state.reps;
  let newFeedback = "Good form";

  // Sitting: angle ~ 90, Extended: angle ~ 180
  if (angle < 110) {
    newStage = "down";
  }
  if (angle > 160 && newStage === "down") {
    newStage = "up";
    newReps += 1;
  }

  if (angle < 160 && angle > 110) {
     newFeedback = "Extend fully";
  }

  return { ...state, reps: newReps, stage: newStage, feedback: newFeedback, currentAngle: angle };
};

export const evaluateHipAbduction = (landmarks, state) => {
  // We can measure the angle between the two legs:
  // left knee=25, left hip=23 or right hip=24, right knee=26.
  // Actually, let's use vertical line from hip or just angle between two hips and knee.
  // Left hip = 23, Right hip = 24, Right knee = 26
  const leftHip = getLandmark(landmarks, 23);
  const rightHip = getLandmark(landmarks, 24);
  const rightKnee = getLandmark(landmarks, 26);

  if (!leftHip || !rightHip || !rightKnee) return state;

  const angle = calculateAngle(leftHip, rightHip, rightKnee);
  let newStage = state.stage;
  let newReps = state.reps;
  let newFeedback = "Good form";

  // Standing straight: angle ~ 90
  // Abducted: angle > 110
  if (angle < 100) {
    newStage = "down";
  }
  if (angle > 115 && newStage === "down") {
    newStage = "up";
    newReps += 1;
  }

  return { ...state, reps: newReps, stage: newStage, feedback: newFeedback, currentAngle: angle };
};

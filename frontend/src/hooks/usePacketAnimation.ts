/** Hook for managing packet animation state. */

import { useState, useCallback, useEffect, useRef } from 'react';
import type { PacketSimulationResponse } from '../types';
import type {
  PacketVisualState,
  AnimationStatus,
  AnimationStep,
} from '../constants/animation';
import {
  ANIMATION_TIMING,
  getAnimationDuration,
  createInitialPacketState,
} from '../constants/animation';

interface UsePacketAnimationProps {
  simulationResult: PacketSimulationResponse | null;
  onComplete?: () => void;
}

interface UsePacketAnimationReturn {
  packetState: PacketVisualState;
  animationSteps: AnimationStep[];
  isPlaying: boolean;
  isPaused: boolean;
  play: () => void;
  pause: () => void;
  resume: () => void;
  replay: () => void;
  skip: () => void;
  reset: () => void;
}

export function usePacketAnimation({
  simulationResult,
  onComplete,
}: UsePacketAnimationProps): UsePacketAnimationReturn {
  const [packetState, setPacketState] = useState<PacketVisualState>(createInitialPacketState());
  const [animationSteps, setAnimationSteps] = useState<AnimationStep[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  const animationTimeoutRef = useRef<number | null>(null);
  const currentStepTimeoutRef = useRef<number | null>(null);

  // Clear all timeouts on unmount
  useEffect(() => {
    return () => {
      if (animationTimeoutRef.current) {
        clearTimeout(animationTimeoutRef.current);
      }
      if (currentStepTimeoutRef.current) {
        clearTimeout(currentStepTimeoutRef.current);
      }
    };
  }, []);

  // Build animation steps from simulation result
  useEffect(() => {
    if (!simulationResult || !simulationResult.success) {
      setAnimationSteps([]);
      return;
    }

    const steps: AnimationStep[] = [];

    simulationResult.transformations.forEach((transformation, index) => {
      let status: AnimationStatus;

      // Use switch to avoid TypeScript narrowing issues
      switch (transformation.action) {
        case 'ORIGINAL':
          status = index === 0 ? 'TRAVELLING_TO_GATEWAY' : 'TRAVELLING_TO_DESTINATION';
          break;
        case 'SNAT':
        case 'DNAT':
        case 'REVERSE_SNAT':
          status = 'AT_GATEWAY';
          break;
        case 'FORWARD':
          status = 'TRAVELLING_TO_DESTINATION';
          break;
        default:
          status = 'TRAVELLING_TO_DESTINATION';
          break;
      }

      steps.push({
        index,
        status,
        stage: transformation.stage,
        action: transformation.action,
      });
    });

    // Add completion step
    steps.push({
      index: steps.length,
      status: 'COMPLETED',
      stage: simulationResult.transformations[simulationResult.transformations.length - 1]?.stage || 'INTERNET',
      action: 'FORWARD',
    });

    setAnimationSteps(steps);
  }, [simulationResult]);

  // Initialize packet state when simulation result changes
  useEffect(() => {
    if (!simulationResult || !simulationResult.success) {
      setPacketState(createInitialPacketState());
      setIsPlaying(false);
      setIsPaused(false);
      return;
    }

    const initialState: PacketVisualState = {
      ...createInitialPacketState(),
      protocol: simulationResult.original_packet.protocol,
      sourceIp: simulationResult.original_packet.source_ip,
      sourcePort: simulationResult.original_packet.source_port,
      destinationIp: simulationResult.original_packet.destination_ip,
      destinationPort: simulationResult.original_packet.destination_port,
      translatedPacket: simulationResult.translated_packet ? {
        sourceIp: simulationResult.translated_packet.source_ip,
        sourcePort: simulationResult.translated_packet.source_port,
        destinationIp: simulationResult.translated_packet.destination_ip,
        destinationPort: simulationResult.translated_packet.destination_port,
      } : null,
    };

    setPacketState(initialState);
    setIsPlaying(false);
    setIsPaused(false);
  }, [simulationResult]);

  // Refs for current state to avoid stale closures
  const isPlayingRef = useRef(isPlaying);
  const isPausedRef = useRef(isPaused);
  const packetStateRef = useRef(packetState);
  const animationStepsRef = useRef(animationSteps);
  const onCompleteRef = useRef(onComplete);

  isPlayingRef.current = isPlaying;
  isPausedRef.current = isPaused;
  packetStateRef.current = packetState;
  animationStepsRef.current = animationSteps;
  onCompleteRef.current = onComplete;

  // Animation loop
  const executeStep = useCallback((
    stepIndex: number
  ) => {
    const steps = animationStepsRef.current;

    if (stepIndex >= steps.length) {
      setPacketState(prev => ({ ...prev, status: 'COMPLETED', currentStepIndex: stepIndex }));
      setIsPlaying(false);
      onCompleteRef.current?.();
      return;
    }

    const step = steps[stepIndex];
    const travelDuration = getAnimationDuration(ANIMATION_TIMING.PACKET_TRAVEL_DURATION);
    const pauseDuration = getAnimationDuration(ANIMATION_TIMING.GATEWAY_PAUSE_DURATION);

    const executeNextStep = () => {
      if (!isPlayingRef.current || isPausedRef.current) return;
      if (stepIndex + 1 < steps.length) {
        executeStep(stepIndex + 1);
      } else {
        setPacketState(prev => ({ ...prev, status: 'COMPLETED', currentStepIndex: stepIndex + 1 }));
        setIsPlaying(false);
        onCompleteRef.current?.();
      }
    };

    setPacketState(prev => ({
      ...prev,
      status: step.status,
      currentStepIndex: stepIndex,
      action: step.action,
    }));

    if (step.status === 'TRAVELLING_TO_GATEWAY' || step.status === 'TRAVELLING_TO_DESTINATION') {
      // Travel animation
      const startTime = Date.now();
      const animateTravel = () => {
        if (!isPlayingRef.current || isPausedRef.current) return;

        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / travelDuration, 1);

        setPacketState(prev => ({ ...prev, progress }));

        if (progress >= 1) {
          executeNextStep();
        } else {
          animationTimeoutRef.current = window.requestAnimationFrame(animateTravel);
        }
      };

      animateTravel();
    } else if (step.status === 'AT_GATEWAY') {
      // At gateway - show transformation
      setPacketState(prev => ({ ...prev, progress: 1 }));

      if (pauseDuration > 0) {
        currentStepTimeoutRef.current = window.setTimeout(() => {
          if (!isPlayingRef.current || isPausedRef.current) return;
          executeNextStep();
        }, pauseDuration);
      } else {
        executeNextStep();
      }
    } else if (step.status === 'COMPLETED') {
      // Final state
      setPacketState(prev => ({ ...prev, status: 'COMPLETED', currentStepIndex: stepIndex }));
      setIsPlaying(false);
      onCompleteRef.current?.();
    } else {
      executeNextStep();
    }
  }, []);

  const play = useCallback(() => {
    if (!simulationResult || !simulationResult.success || animationSteps.length === 0) return;

    setIsPlaying(true);
    setIsPaused(false);

    // If already completed, replay from start
    if (packetState.status === 'COMPLETED') {
      setPacketState(createInitialPacketState());
    }

    executeStep(0);
  }, [simulationResult, animationSteps, packetState]);

  const pause = useCallback(() => {
    setIsPaused(true);
    if (animationTimeoutRef.current) {
      window.cancelAnimationFrame(animationTimeoutRef.current);
      animationTimeoutRef.current = null;
    }
    if (currentStepTimeoutRef.current) {
      clearTimeout(currentStepTimeoutRef.current);
      currentStepTimeoutRef.current = null;
    }
  }, []);

  const resume = useCallback(() => {
    if (!isPaused) return;
    setIsPaused(false);
    // Resume from current step
    executeStep(packetState.currentStepIndex);
  }, [isPaused, packetState]);

  const replay = useCallback(() => {
    // Reset and play from beginning
    if (animationTimeoutRef.current) {
      window.cancelAnimationFrame(animationTimeoutRef.current);
      animationTimeoutRef.current = null;
    }
    if (currentStepTimeoutRef.current) {
      clearTimeout(currentStepTimeoutRef.current);
      currentStepTimeoutRef.current = null;
    }

    setPacketState(createInitialPacketState());
    setIsPaused(false);
    setIsPlaying(true);

    // Small delay to allow state to reset
    setTimeout(() => {
      if (!simulationResult || !simulationResult.success) return;
      executeStep(0);
    }, 50);
  }, [simulationResult, animationSteps]);

  const skip = useCallback(() => {
    // Immediately jump to final state
    if (animationTimeoutRef.current) {
      window.cancelAnimationFrame(animationTimeoutRef.current);
      animationTimeoutRef.current = null;
    }
    if (currentStepTimeoutRef.current) {
      clearTimeout(currentStepTimeoutRef.current);
      currentStepTimeoutRef.current = null;
    }

    setIsPlaying(false);
    setIsPaused(false);

    const translated = simulationResult?.translated_packet;
    if (simulationResult && simulationResult.success && translated) {
      setPacketState(prev => ({
        ...prev,
        status: 'COMPLETED',
        sourceIp: translated.source_ip,
        sourcePort: translated.source_port,
        destinationIp: translated.destination_ip,
        destinationPort: translated.destination_port,
        progress: 1,
        currentStepIndex: animationSteps.length - 1,
      }));
    }
  }, [simulationResult, animationSteps]);

  const reset = useCallback(() => {
    if (animationTimeoutRef.current) {
      window.cancelAnimationFrame(animationTimeoutRef.current);
      animationTimeoutRef.current = null;
    }
    if (currentStepTimeoutRef.current) {
      clearTimeout(currentStepTimeoutRef.current);
      currentStepTimeoutRef.current = null;
    }

    setPacketState(createInitialPacketState());
    setIsPlaying(false);
    setIsPaused(false);
  }, []);

  return {
    packetState,
    animationSteps,
    isPlaying,
    isPaused,
    play,
    pause,
    resume,
    replay,
    skip,
    reset,
  };
}
"""
Animation utilities
"""

import math
from dataclasses import dataclass

@dataclass
class AnimationState:
    value: float = 0.0
    target: float = 0.0
    velocity: float = 0.0
    smoothing: float = 0.1
    
    def update(self):
        """Update animation value toward target"""
        diff = self.target - self.value
        self.value += diff * self.smoothing
        return abs(diff) > 0.01
    
    def set_target(self, target: float):
        self.target = target

class SineWave:
    """Sine wave generator for demo data"""
    def __init__(self, period=1.0, amplitude=1.0, offset=0.0):
        self.period = period
        self.amplitude = amplitude
        self.offset = offset
        self.time = 0.0
        
    def update(self, dt: float):
        self.time += dt
        
    def value(self) -> float:
        return self.offset + self.amplitude * math.sin(self.time * 2 * math.pi / self.period)
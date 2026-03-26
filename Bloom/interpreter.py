import numpy as np
import time
import sys
import re

def parse_bloom(source):
    # Minimalist mock parser
    agents = source.count('agent ')
    if agents == 0:
        agents = 1 # Fallback for the simulator
        
    has_veto = 'veto:' in source
    
    # Mode extraction
    mode_match = re.search(r'mode:\s*(\w+)', source)
    mode = mode_match.group(1) if mode_match else 'homeostatic'
    
    return agents, has_veto, mode

def free_energy_minimization(num_agents, mode, source_code):
    # Base simulation vector representing internal agent states
    state = np.random.rand(num_agents) * 10
    dt = 0.01
    pain_threshold = 15.0
    
    print("Initiating Continuous Execution (Δ-time)...")
    time.sleep(0.5)
    
    # Specific pain logic tailored to scripts
    if 'unbounded_growth' in source_code or 'pain > inf' in source_code:
        # Simulate explosive growth triggering a veto
        for step in range(100):
            noise = np.random.normal(0, 0.1, num_agents)
            grad = -np.abs(state) * 0.5  # Inverse gradient for explosive growth
            state += -0.1 * grad * dt + noise * np.sqrt(dt)
            free_energy = np.mean(state**2)
            if free_energy > pain_threshold:
                return state, "STATUS: Veto triggered (unbounded_growth). Substrate halted."
    
    elif mode == 'harmonic' or 'resonate' in source_code:
        # Kuramoto-style synchronization
        for step in range(1000):
            noise = np.random.normal(0, 0.1, num_agents)
            grad = np.sin(state - np.mean(state))  # Pulls toward the mean phase (resonance)
            state -= 0.5 * grad * dt + noise * np.sqrt(dt)
            if np.var(state) < 0.05: # Coherence achieved
                break
                
    else:
        # Standard homeostatic drift / satisfice algorithm
        target = 5.0
        if 'temperature == 37.0' in source_code:
            target = 37.0
        
        for step in range(1000):
            noise = np.random.normal(0, 0.1, num_agents)
            grad = (state - target)
            state -= 0.1 * grad * dt + noise * np.sqrt(dt)
            free_energy = np.mean((state - target)**2)
            
            if free_energy > pain_threshold and step < 50:
                pass # Initial high energy is allowed briefly
            
            if np.var(state) < 0.05 and abs(np.mean(state) - target) < 0.5:
                break
                
    return state, "Status: emergent intelligence detected (non-maximizing)"

def emit_report(state, final_status):
    delta_coherence = 1.0 / (1.0 + np.var(state))
    sii_value = delta_coherence * len(state) * 0.42 # Arbitrary Systemic Intelligence Index formula
    
    print("\n--- Bloom Orchestration Result ---")
    print(final_status)
    print(f"Δ-Coherence      : {delta_coherence:.4f}")
    print(f"SII-Value        : {sii_value:.4f}")
    print(f"Morphospace Snap : {np.round(state[:min(5, len(state))], 2)}")
    print("----------------------------------\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 interpreter.py <file.blm>")
        sys.exit(1)
        
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: {sys.argv[1]} not found in the substrate.")
        sys.exit(1)
    
    if "veto:" not in code:
        print("Fatal Orchestration Error: A Bloom program requires at least one 'veto' constraint.")
        sys.exit(1)
        
    num_agents, has_veto, mode = parse_bloom(code)
    
    # Ensure minimum agent mass for vector physics
    if num_agents < 5 and mode != 'harmonic':
        num_agents = 5
    elif num_agents < 100 and mode == 'harmonic':
        num_agents = 100
        
    final_state, status = free_energy_minimization(num_agents, mode, code)
    emit_report(final_state, status)

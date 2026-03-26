# The Grammar of Bloom

The syntax of Bloom is a blend of minimalist YAML and esoteric incantation. There are no loops and no explicit time control vectors—execution is a continuous dynamic process (continuous-time simulation) that only concludes when the system rests in a coherent homeostasis or is destroyed by a veto.

## EBNF Specification

```ebnf
program        ::= lattice_decl agent_list orchestrate_block
lattice_decl   ::= "lattice:" topology "\n"
topology       ::= "void" | "torus" | "fractal_graph" | "scale_free"

agent_list     ::= (agent_decl)+
agent_decl     ::= "agent" ID ":" "\n"
                   "  blanket:" sensory_states "," active_states "\n"
                   "  local_rule:" rule_expression "\n"
                   "  veto:" veto_expression "\n"

orchestrate_block ::= "orchestrate:" "\n"
                      "  seed:" float_vector_or_generator "\n"
                      "  mode:" ("harmonic" | "homeostatic" | "market" | "flow" | "love_as_constraint") "\n"
                      "  run:" duration "until" condition "\n"

rule_expression ::= "drift" | "satisfice(" expr ")" | "resonate(" expr ")"
veto_expression ::= "pain >" float | "scale_breach" | "unbounded_growth"
```

## Keywords & Semantics

- **`lattice`**: Defines the topology of the substrate. This is not memory, but rather the space where agents causally interact.
- **`agent`**: An autonomous entity.
- **`blanket`**: The Markov blanket of the agent. Dictates local visibility (Sensory) and asymmetric influence on the world (Active). There is no global visibility.
- **`local_rule`**: What the agent strives for locally.
  - *`drift`*: Wander along the local gradients of noise.
  - *`satisfice`*: Search for a threshold value, not an optimum. Once the state is satisfactory, active adjustment ceases.
  - *`resonate`*: Attempt to match frequency/state variations with neighbors within the Markov blanket.
- **`veto`**: The core design principle of the substrate. Free energy is measured as *Pain*. If a constraint is breached, the substrate destroys the agent (Execution Halted).
- **`orchestrate`**: Initializes the physics-based execution cycle.
- **`love_as_constraint`**: An execution mode that respects local autonomy but prevents competitive destruction through a holonic embrace.

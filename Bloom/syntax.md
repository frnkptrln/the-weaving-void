# The Grammar of Bloom

Die Syntax von Bloom ist eine Mischung aus minimalistischem YAML und esoterischen Zaubersprüchen. Es gibt keine Schleifen (Loops) und keine explizite Zeitsteuerung – die Ausführung ist ein kontinuierlicher dynamischer Prozess (continuous-time simulation), der erst endet, wenn das System in einer kohärenten Homeostase ruht oder durch ein Veto zerstört wird.

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

- **`lattice`**: Definiert die Topologie des Substrats. Es ist kein Speicher (Memory), sondern der Raum, in dem Agenten kausal interagieren.
- **`agent`**: Eine autonome Entität.
- **`blanket`**: Die Markov-Decke des Agenten. Erlaubt nur *lokale* Sichtbarkeit (Sensory) und asymmetrische Einflüsse auf die Welt (Active).
- **`local_rule`**: Was der Agent lokal anstrebt.
  - *`drift`*: Wandern entlang lokaler Gradienten des Rauschens.
  - *`satisfice`*: Suchen nach einem Schwellenwert, nicht nach einem Optimum.
  - *`resonate`*: Versuchen, die Frequenz an die Nachbarn in der Markov-Decke anzupassen.
- **`veto`**: Das Kern-Designprinzip des Substrats. Free-Energy wird als *Pain* (Schmerz) gemessen. Bricht ein Constraint, zerstört das Substrat den Agenten (Execution Halted).
- **`orchestrate`**: Startet die physikbasierte Ausführung.
- **`love_as_constraint`**: Ein Modus, der lokale Autonomie respektiert, aber durch eine holonische Klammer destruktive Konkurrenz verhindert.

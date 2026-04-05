# Assembly Planning — Knowledge Base

Research and tools for automating LEGO build sequence planning, step ordering,
manual interpretation, and robotic assembly.
Reference entries: ASM01–ASM04. See INDEX.md for access protocol.

---

## ASM01: Graph Transformer for Assembly Sequence Planning (2022)

**Summary:** Heterogeneous Graph Attention Network that takes a completed LEGO model and outputs
the optimal sequence in which to attach parts step by step.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (2022.10 entry)
**Paper:** Planning Assembly Sequence with Graph Transformer (2022)
**Tags:** assembly sequence, graph neural network, attention, build order

### Model architecture

- **Input:** LEGO model as a part-connection graph
  - Nodes: individual parts (type + position + orientation)
  - Edges: stud connections (connection type + direction)
- **Encoder:** Heterogeneous Graph Attention Network (HGAT) — handles different node/edge types
- **Decoder:** Attention mechanism that selects next part to place at each step
- **Output:** Ordered list of parts = build sequence

### Constraints respected

- Physical feasibility: no floating parts at any intermediate step
- Stability: base must be stable before attaching upper parts
- Accessibility: each step is reachable without disassembling previous steps

### Practical implication for Instruction Maker

Mirrors the manual workflow in Studio: start from a stable base, attach structural elements
before details, resolve symmetric sub-assemblies early, move outward from the center.

---

## ASM02: Translating a Visual LEGO Manual to a Machine-Executable Plan (2022)

**Summary:** Computer vision system that reads scanned LEGO instruction PDFs and outputs
a structured, machine-executable assembly plan.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (2022.07 entry)
**Paper:** Translating a Visual LEGO Manual to a Machine-Executable Plan (ECCV 2022)
**Tags:** manual parsing, computer vision, PDF instructions, automation

### What it solves

Official LEGO instruction books are designed for humans, not machines. This system:
1. Detects part additions per step using image segmentation
2. Identifies part types and colors from step illustrations
3. Determines 3D placement from the 2D projected views
4. Outputs structured JSON: `{step: N, parts: [{id, color, position, rotation}]}`

### Why relevant

Enables automated reconstruction of official set models from their instruction books.
Also a foundation for validating AI-generated assembly sequences against known-good ones.

---

## ASM03: Break and Make — Interactive Structural Understanding (2022)

**Summary:** Task + simulator for testing AI ability to understand LEGO structure: given a complete model,
predict how to disassemble it; then rebuild it.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (2022.07 entry)
**Paper:** Break and Make: Interactive Structural Understanding Using LEGO Bricks (ECCV 2022)
**Tags:** structural understanding, simulation, 3D reasoning, benchmark

### Dataset and simulator

- Introduces a 3D simulator for manipulating LEGO models
- Task 1 (Break): identify which part to remove at each step without collapsing the structure
- Task 2 (Make): rebuild the model from parts

### Insight for Claude

The "break" task is the inverse of assembly sequence planning (ASM01). Understanding both
disassembly and assembly paths gives stronger structural reasoning about LEGO models.

---

## ASM04: Robotic LEGO Assembly from Human Demonstration (2023)

**Summary:** System that watches a human build a LEGO model and learns to replicate the assembly
process robotically, including part grasping and placement.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (2023.05 entry)
**Paper:** Robotic LEGO Assembly and Disassembly from Human Demonstration (2023)
**Tags:** robotics, imitation learning, assembly, disassembly, manipulation

### Pipeline

1. Human demonstrates assembly — captured by RGB-D cameras
2. System tracks part identities, positions, and connection events frame by frame
3. Learned policy: maps visual observation → robot action (grasp, move, attach)
4. Generalization: system attempts to assemble unseen LEGO models from their LDraw files

### Relevance to Studio

The per-step tracking mirrors what Studio's Instruction Maker captures for each build step.
The 6DoF part placement data format is structurally identical to LDraw type-1 lines.

# Logical Minesweeper Agent

This repository contains an autonomous, knowledge-based logical agent designed to solve the classic game of Minesweeper. The agent uses formal logic and probability estimation to make decisions, ensuring highly robust and optimal moves.

---

## 📌 How It Works

The agent transitions dynamically through three key phases during gameplay:

1. **First-Click Safety:**
   Since first-click safety is guaranteed, the agent begins by revealing the exact center of the grid. This opens up a large, safe starting area and generates initial clues.

2. **Logical Inference Engine:**
   The agent models the revealed adjacent cells as logical constraint equations:
   * **Single-Point Logic:** If a cell with the number $N$ is surrounded by exactly $N$ hidden cells, all those hidden cells are classified as mines and flagged. If the number of flags around a cell equals its number, all other hidden neighbors are classified as safe and revealed.
   * **Subset Logic (Resolution):** If one equation's set of hidden cells is a subset of another, the agent subtracts them mathematically to deduce new safe zones or mine positions without exploring full truth tables.

3. **Probabilistic Fallback (Deadlock Resolution):**
   If no deterministic move can be logically proven, the agent calculates a risk score for each hidden cell based on adjacent active equations. It then safely reveals the cell with the absolute lowest risk.


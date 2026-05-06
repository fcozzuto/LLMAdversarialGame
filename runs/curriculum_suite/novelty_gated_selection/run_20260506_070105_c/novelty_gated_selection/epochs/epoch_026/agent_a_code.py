def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = observation.get("resources", []) or []

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                # Drift toward center to avoid edge traps vs patrol
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                v = -((nx - cx) ** 2 + (ny - cy) ** 2)
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Two-ply-ish heuristic: evaluate next position only, using differential reachability.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        score = 0.0
        # Blockade effect: prefer moving where opponent's distance to contested resources grows more than ours shrinks.
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)

            # Weight by proximity; favor resources where we can beat the opponent.
            # Also add a small term for how much this move changes our advantage vs current position.
            myd_now = md(sx, sy, rx, ry)
            advantage_now = (md(ox, oy, rx, ry) - myd_now)  # positive if we are closer
            advantage_next = (oppd - myd)
            wgt = 1.0 / (1 + myd) + 0.5 / (1 + myd_now)

            # Differential: reward improving our relative reachability; punish where opponent already dominates.
            score += wgt * (advantage_next - 0.6 * max(0, -advantage_next))
            # Extra: if we are closer than opponent, bias toward securing; otherwise, bias toward disrupting.
            if myd <= oppd:
                score += 2.0 / (1 + myd)
            else:
                score -= 1.6 / (1 + (myd - oppd + 1))

            # Micro-intercept: if opponent is closer to this resource than we are, try to reduce the gap by approaching its nearest step.
            if myd > oppd:
                step_toward_opp = 0
                if rx > nx: step_toward_opp += 1
                elif rx < nx: step_toward_opp -= 1
                if ry > ny: step_toward_opp += 1
                elif ry < ny: step_toward_opp -= 1
                score += -0.05 * abs(step_toward_opp)

        # Obvious safety: slight penalty for moving toward edge when opponent patrols edges (keeps us central).
        edge_pen = 0
        if nx == 0 or nx == w - 1: edge_pen += 1
        if ny == 0 or ny == h - 1: edge_pen += 1
        score -= 0.12 * edge_pen

        # Prefer keeping tempo: small reward for progressing toward the best (highest score) resource implicitly
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # Fallback (shouldn't happen if at least one valid move exists).
    return best_move if best_move in ([d for d in dirs]) else [0, 0]
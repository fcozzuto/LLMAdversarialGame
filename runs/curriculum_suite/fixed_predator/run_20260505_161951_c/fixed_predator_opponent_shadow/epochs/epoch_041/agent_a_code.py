def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Deterministic tie-break: prefer smaller (dx,dy) ordering after scoring.
    order = {(0, 0): 0, (0, -1): 1, (0, 1): 2, (-1, 0): 3, (1, 0): 4, (-1, -1): 5, (1, -1): 6, (-1, 1): 7, (1, 1): 8}

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy, nx, ny in moves:
            val = (md(nx, ny, tx, ty), md(nx, ny, ox, oy))
            cand = (val, order[(dx, dy)])
            if best is None or cand < best:
                best = cand
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Pick best move by contesting the most favorable reachable resource.
    # Lookahead uses only current positions (fast) but compares post-move distance gaps.
    best = None
    for dx, dy, nx, ny in moves:
        # Evaluate against a small deterministic subset of resources to control runtime.
        # Sort by opponent advantage (weaker for us -> later), but deterministic.
        scored = []
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # If opponent is much closer, resource is less attractive.
            gap = (od - sd)
            # Encourage closeness and avoiding giving opponent huge advantage.
            scored.append((gap, -sd, rx, ry))
        # Take top resources by gap first; deterministic slice
        scored.sort(reverse=True)
        subset = scored[:3] if len(scored) >= 3 else scored

        # Value: try to maximize our advantage; tie-break to minimize our distance.
        best_gap = None
        best_sd = None
        for gap, negsd, rx, ry in subset:
            sd = -negsd
            if best_gap is None or gap > best_gap or (gap == best_gap and sd < best_sd):
                best_gap = gap
                best_sd = sd

        # Additional pressure: also mildly prefer moves that reduce distance to opponent when we're behind (avoid being intercepted).
        self_to_opp = md(nx, ny, ox, oy)
        us_to_opp = md(sx, sy, ox, oy)
        behind = 1 if self_to_opp > us_to_opp else 0
        val = (-best_gap, best_sd, behind, md(nx, ny, (ox + sx) // 2, (oy + sy) // 2))
        cand = (val, order[(dx, dy)])
        if best is None or cand < best:
            best = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
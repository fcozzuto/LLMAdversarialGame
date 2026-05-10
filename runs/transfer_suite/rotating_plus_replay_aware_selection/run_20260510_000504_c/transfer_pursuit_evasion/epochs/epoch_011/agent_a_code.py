def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer_self = ("purs" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursuer" in self_role)
    pursuer_opp = ("purs" in opp_role) or ("hunter" in opp_role) or ("chaser" in opp_role) or ("pursuer" in opp_role)
    pursue = pursuer_self or (not pursuer_opp)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_score = None
    best_step = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        ddx = nx - ox
        ddy = ny - oy
        d2 = ddx * ddx + ddy * ddy
        man = abs(ddx) + abs(ddy)

        if pursue:
            score = (-d2) * 1000 - man
        else:
            score = (d2) * 1000 + man

        step = abs(dx) + abs(dy)

        # Secondary: avoid staying still unless it's the only option; then prefer lexicographically smaller moves.
        if best is None or score > best_score or (score == best_score and (step > best_step or (step == best_step and (dx, dy) < best))):
            best = (dx, dy)
            best_score = score
            best_step = step

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
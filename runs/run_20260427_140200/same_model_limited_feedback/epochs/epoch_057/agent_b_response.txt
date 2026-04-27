def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        # No resources visible: move to center deterministically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]
    best = None
    tx = ty = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # Compete: prefer resources we're closer to (with slight penalty if opponent is also close)
        val = (sd - 0.8 * od)
        if best is None or val < best:
            best = val; tx, ty = rx, ry
    dx0 = 0 if sx == tx else (1 if sx < tx else -1)
    dy0 = 0 if sy == ty else (1 if sy < ty else -1)
    # Deterministic move priority toward target, with fallback preserving strong progress
    candidates = []
    candidates.append((dx0, dy0))
    # If diagonal toward target is not possible, try 2-step-like components first
    candidates.append((dx0, 0))
    candidates.append((0, dy0))
    candidates.append((dx0, -dy0))
    candidates.append((-dx0, dy0))
    candidates.append((-dx0, 0))
    candidates.append((0, -dy0))
    candidates.append((0, 0))
    # Ensure unique while preserving order
    seen = set()
    ordered = []
    for c in candidates:
        if c not in seen:
            seen.add(c); ordered.append(c)
    best_move = (0, 0); best_score = None
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: 
            continue
        if (nx, ny) in obstacles:
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        # tie-break: also reduce distance to opponent to contest near contact
        contest = 0.15 * (abs(ox - nx) + abs(oy - ny))
        score = nd + contest
        if best_score is None or score < best_score:
            best_score = score; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(a, b, c, d):
        dx = a - c; dx = dx if dx >= 0 else -dx
        dy = b - d; dy = dy if dy >= 0 else -dy
        return dx + dy
    if (sx, sy) in resources:
        return [0, 0]
    # If resources exist, choose a resource to maximize "lead after move", but when behind, contest instead.
    best_target = None
    best_key = (-10**18, -10**18, 10**18)  # (lead preference, opp urgency, self closeness)
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        lead = od - sd  # positive means we are closer
        opp_urgency = -od
        # When behind (lead<0), still consider resources where we can reduce od faster than sd (contest).
        key = (lead, opp_urgency, sd)
        if best_target is None or key > best_key:
            best_key = key
            best_target = (rx, ry)
    rx, ry = best_target if best_target is not None else (sx, sy)

    # Evaluate next moves by immediate progress and blocking the opponent's approach to the chosen resource.
    def step_dir(cx, cy, tx, ty):
        dx = 0 if tx == cx else (1 if tx > cx else -1)
        dy = 0 if ty == cy else (1 if ty > cy else -1)
        return dx, dy

    # Also compute an "opponent direction bias" to avoid feeding them direct lines.
    odx, ody = step_dir(ox, oy, rx, ry)
    best_mv = (0, 0)
    best_val = (-10**18, -10**18, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d = md(nx, ny, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        # Our lead after move:
        lead_after = opp_d - self_d
        # Prefer reducing distance, but if we are behind, prioritize moves that reduce our distance most.
        progress = -self_d
        # Discourage stepping into a square that makes opponent's direct step to target easier.
        opp_next = (ox + odx, oy + ody)
        block = 0
        if (nx, ny) == opp_next:
            block = 2  # making the opponent step be "our" move target square (still may be invalid later, but deterministic)
        # Small penalty for staying still
        stay_pen = 0 if (dx == 0 and dy == 0) else 0
        val = (lead_after, progress + block, -md(nx, ny, ox, oy) + stay_pen)
        if val > best_val:
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]
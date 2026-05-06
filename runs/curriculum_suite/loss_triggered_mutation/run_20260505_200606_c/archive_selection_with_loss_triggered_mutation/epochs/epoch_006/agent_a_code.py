def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx*dx + dy*dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        # Drift toward center-ish while staying relative to opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx + (cx - ox) // 2, cy + (cy - oy) // 2
        tx = max(0, min(w - 1, tx)); ty = max(0, min(h - 1, ty))
        bestm = [0, 0, 10**9]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            val = d2(nx, ny, tx, ty)
            if (val, dx, dy) < (bestm[2], bestm[0], bestm[1]):
                bestm = [dx, dy, val]
        return [bestm[0], bestm[1]]

    # Pick a target deterministically: prefer resources where we have a relative advantage.
    best = None
    for rx, ry in resources:
        self_d = d2(sx, sy, rx, ry)
        opp_d = d2(ox, oy, rx, ry)
        adv = opp_d - self_d  # positive => we are closer
        # Add small preference toward center and away from opponent to reduce edge running.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        center_bias = -((rx - cx)*(rx - cx) + (ry - cy)*(ry - cy))
        val = (-(adv > 0), -adv, -center_bias, self_d, rx, ry)  # deterministic tuple
        if best is None or val < best[0]:
            best = (val, rx, ry, adv)
    _, tx, ty, _ = best

    # Evaluate candidate moves by resulting advantage and closeness to target; obstacle-safe.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        self_d = d2(nx, ny, tx, ty)
        opp_d = d2(ox, oy, tx, ty)
        adv_after = opp_d - self_d
        # If we move onto a resource, boost hard using distance=0.
        on_res = 1 if (nx, ny) in map(tuple, resources) else 0
        # Also lightly discourage moving toward opponent directly (prevents mirroring traps).
        opp_dist = d2(nx, ny, ox, oy)
        score = (-(on_res), -adv_after, self_d, -opp_dist, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]
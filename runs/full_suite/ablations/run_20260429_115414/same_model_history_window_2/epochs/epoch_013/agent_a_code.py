def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If no resources remain, move to center while minimizing approach to opponent.
    if not resources or observation.get("remaining_resource_count", len(resources)) <= 0:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -md(nx, ny, cx, cy) - 0.1 * md(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Target by maximizing advantage: (opp distance - my distance) to the same resource.
    # Also encourage moving toward the best target after the move.
    best_overall = None; best_val = -10**18
    for dx, dy, nx, ny in legal:
        my_best = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            if not inb(rx, ry) or (rx, ry) in blocked:
                continue
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Gap is positive when I am closer.
            gap = opd - myd
            # Prefer nearer resources when gap ties.
            v = gap * 10 - myd * 0.3
            # If opponent is very close to the resource, prioritize blocking/intercept by not letting myd grow.
            if opd <= 1:
                v -= myd * 2.0
            if v > my_best:
                my_best = v

        # Mildly penalize moves that get closer to opponent when I don't have advantage.
        myd_opp = md(nx, ny, ox, oy)
        curd_opp = md(sx, sy, ox, oy)
        penalty = 0.0
        if my_best < 0 and myd_opp < curd_opp:
            penalty = (curd_opp - myd_opp) * 1.5

        val = my_best - penalty
        if val > best_val or (val == best_val and (dx, dy) < (best_overall if best_overall else (1,1))):
            best_val = val; best_overall = (dx, dy)

    return [best_overall[0], best_overall[1]]
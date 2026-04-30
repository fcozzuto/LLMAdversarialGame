def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # One-step lookahead: pick move maximizing competitive advantage.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Also slightly prefer moving toward opponent if it forces a resource contest disruption.
    opp_bias = cheb(sx, sy, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        # Evaluate best resource to target after this move.
        best_adv = -10**18
        best_own = 10**9
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Advantage: higher means we are closer (or opponent farther).
            adv = (do - dm)
            # Tie-break: prefer shorter own distance, and avoid moving into general congestion near opponent.
            congestion = cheb(nx, ny, ox, oy)  # smaller is riskier; penalize being too close
            val = adv * 1000 - dm * 5 - congestion * 2
            if val > best_adv:
                best_adv = val
                best_own = dm
        # If we can't improve on current best, still allow progress: prioritize reducing our nearest distance.
        cur_near = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
        if best_adv == -10**18:
            best_adv = -cur_near
        # Global tie-breakers
        val2 = best_adv + (cur_near - best_own) * 50 + (opp_bias - cheb(nx, ny, ox, oy)) * 1
        if val2 > best_val:
            best_val = val2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
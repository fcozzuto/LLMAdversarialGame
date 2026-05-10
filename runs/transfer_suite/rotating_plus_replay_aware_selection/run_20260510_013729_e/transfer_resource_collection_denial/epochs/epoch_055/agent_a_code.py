def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_resource_value(x, y):
        best = (-10**18, 10**9, 10**9)  # (score, self_dist, resource_key)
        # Deterministic ordering for tie breaks
        for rx, ry in sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1])):
            if (rx, ry) in obst:
                continue
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive: we are closer
            cap = 1.0 if (x, y) == (rx, ry) else 0.0
            # Also discourage letting opponent be significantly closer
            danger = 1.0 if do <= ds else 0.0
            score = 4.0 * lead + 3.0 * cap - 2.0 * danger - 0.08 * ds
            key = rx * 8 + ry
            cand = (score, ds, key)
            if cand[0] > best[0] or (cand[0] == best[0] and (cand[1], cand[2]) < (best[1], best[2])):
                best = cand
        return best[0]

    best_move = (0, 0)
    best_val = -10**18

    # Prefer moves that increase immediate lead to the best collectible
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        # Two-term evaluation: immediate capture potential + next-step improvement (1-step lookahead)
        v0 = best_resource_value(nx, ny)
        # If we can capture now, strongly prefer; otherwise nudge toward routes that keep lead
        if v0 > 2.5:
            v = v0
        else:
            best_next = -10**18
            # small lookahead to avoid getting stuck
            for ddx, ddy in moves:
                mx, my = nx + ddx, ny + ddy
                if not inb(mx, my) or (mx, my) in obst:
                    continue
                vv = best_resource_value(mx, my)
                if vv > best_next:
                    best_next = vv
            v = 0.75 * v0 + 0.25 * best_next

        # Deterministic tie-break: favor staying if equal, else smaller (dx,dy) lexicographically
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
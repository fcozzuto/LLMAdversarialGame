def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    obs_set = set()
    for p in obstacles:
        obs_set.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    if not resources:
        # Fallback: move away from opponent toward center-ish
        tx, ty = w // 2, h // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obs_set or nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            s = cheb(nx, ny, ox, oy) + 0.1 * (-(cheb(nx, ny, tx, ty)))
            if s > best_score:
                best_score = s
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # Precompute resources objective: prefer resources where we have distance advantage over opponent.
    # Strategy: choose move that maximizes "best target" value after this step.
    cx, cy = w // 2, h // 2
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obs_set or nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        total = 0
        # Evaluate best resource target for this post-move position
        best_t = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer targets we are closer to; penalize targets opponent is closer to.
            rel = 3.5 if ds < do else (0.5 if ds == do else -2.0)
            # Encourage actually getting there soon, and avoid being too far.
            time = -1.2 * ds
            # Slightly prefer resources nearer to center (break ties deterministically).
            center = -0.05 * cheb(rx, ry, cx, cy)
            t = rel + time + center
            if t > best_t:
                best_t = t
        # Also lightly penalize moving adjacent to opponent to reduce contest losses.
        contest = -0.25 * cheb(nx, ny, ox, oy)
        total = best_t + contest
        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying.
        if total > best_score:
            best_score = total
            best = [dx, dy]
        elif total == best_score:
            # tie-breaker order: among same score, pick move with lexicographically smallest (dx,dy) with preference for (0,0)
            def key(m):
                if m[0] == 0 and m[1] == 0:
                    return (-1, 0, 0)
                return (0, abs(m[0]), abs(m[1]))
            if best is None or key([dx, dy]) < key(best):
                best = [dx, dy]

    return best if best is not None else [0, 0]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_pursuer = ("pursuer" in self_role) or ("pursue" in self_role)
    opp_pursuer = ("pursuer" in opp_role) or ("pursue" in opp_role)
    i_am_pursuer = self_pursuer or (opp_pursuer and not self_pursuer)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy  # squared distance, deterministic monotone for comparisons

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-breaker: prefer smaller (dx,dy) lexicographically
    deltas.sort()

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        # Obstacle avoidance: penalize adjacency more than staying centered
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    adj += 1
        d = cheb(nx, ny, ox, oy)

        if i_am_pursuer:
            # maximize "closeness": smaller distance is better, so use negative
            score = (-d) - 3.0 * adj
            better = (best_score is None) or (score > best_score)
        else:
            # evade: maximize distance
            score = (d) - 3.0 * adj
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
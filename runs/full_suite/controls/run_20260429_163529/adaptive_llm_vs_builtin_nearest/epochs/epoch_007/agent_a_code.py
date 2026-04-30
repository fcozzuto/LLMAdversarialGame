def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_resource(rx, ry, mx, my):
        md = cheb(mx, my, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Contest preference: prioritize resources where we are at least as close.
        # If not, still move toward minimizing the gap, with tie-break toward higher coords.
        gap = md - od
        return (0 if gap <= 0 else 1, md, gap, rx * 8 + ry)

    if not resources:
        # Fallback: move toward opponent to deny territory
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    best_move = (0, 0)
    best_eval = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        # One-step lookahead: assume we then go greedily toward the best resource.
        # Also, if opponent is adjacent to a resource and we can take a safer one, prefer that.
        eval_best = None
        for r in resources:
            rx, ry = r
            s = score_resource(rx, ry, nx, ny)
            # Extra nudge for grabbing a resource immediately.
            if rx == nx and ry == ny:
                s = (s[0], 0, s[2], s[3])
            # Penalize if opponent can also take it next step (chebyshev <=1 from current).
            if cheb(ox, oy, rx, ry) <= 1 and cheb(nx, ny, rx, ry) > 1:
                s = (s[0], s[1], s[2] + 2, s[3])
            if eval_best is None or s < eval_best:
                eval_best = s

        if eval_best is None:
            continue

        # Deterministic tie-break: prefer moves that reduce distance to opponent centerline-ish.
        tie = cheb(nx, ny, ox, oy)
        cand = (eval_best[0], eval_best[1], eval_best[2], eval_best[3], tie, dx, dy)
        if best_eval is None or cand < best_eval:
            best_eval = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
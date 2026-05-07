def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if ok(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        # Manhattan: simple and stable
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        # Prefer resources where we are closer than opponent; if none, prefer least-opponent-advantaged.
        best_score = None
        best_target = None
        for rx, ry in resources:
            d_self = dist(sx, sy, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            # Strongly favor (d_opp - d_self) positive; tie-break by our closeness
            s = (d_opp - d_self) * 100 - d_self
            if best_score is None or s > best_score or (s == best_score and d_self < dist(sx, sy, best_target[0], best_target[1])):
                best_score = s
                best_target = (rx, ry)

        tx, ty = best_target
        # If we're already on it, grab by staying (often still allowed and deterministic).
        if sx == tx and sy == ty:
            return [0, 0]

        # Choose move that maximizes immediate progress to target while minimizing opponent ability
        # next step: reduce opponent's advantage by moving closer to target than opponent (if possible).
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d_self_n = dist(nx, ny, tx, ty)
            d_opp = dist(ox, oy, tx, ty)
            # Encourage reducing opponent's (d_opp - d_self)
            score = (d_opp - d_self_n) * 100 - d_self_n
            # Avoid helping opponent by stepping closer to them when tie
            score -= 0.5 * dist(nx, ny, ox, oy)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # No visible resources: reposition deterministically to opposite-corner pressure line
    cx, cy = (w - 1) // 2, (h - 1) // 2
    # Drift toward center if it increases distance from opponent; otherwise maximize distance from opponent.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_opp = dist(nx, ny, ox, oy)
        d_center = dist(nx, ny, cx, cy)
        score = d_opp * 10 - d_center
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]
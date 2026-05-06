def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    resources = observation.get("resources") or []
    res = [(r[0], r[1]) for r in resources if isinstance(r, (list, tuple)) and len(r) == 2]
    if not res:
        # Fallback: maximize distance from opponent while moving toward board center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        def dist(x1, y1, x2, y2):
            dx = x1 - x2
            if dx < 0: dx = -dx
            dy = y1 - y2
            if dy < 0: dy = -dy
            return dx + dy
        best = None
        for dx, dy, nx, ny in legal:
            key = (-dist(nx, ny, ox, oy), dist(nx, ny, cx, cy))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Contest target: resource that minimizes total arrival time to both agents.
    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best_target = None
    best_key = None
    for rx, ry in res:
        k = (manhattan(sx, sy, rx, ry) + manhattan(ox, oy, rx, ry),
             manhattan(ox, oy, rx, ry) - manhattan(sx, sy, rx, ry),
             rx, ry)
        if best_key is None or k < best_key:
            best_key = k
            best_target = (rx, ry)

    tx, ty = best_target

    # Move that reduces distance to target while discouraging getting too close to opponent.
    best = None
    for dx, dy, nx, ny in legal:
        d_self = manhattan(nx, ny, tx, ty)
        d_opp = manhattan(nx, ny, ox, oy)
        # Tie-break deterministically with coordinates.
        key = (d_self, -d_opp, dx, dy, nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]